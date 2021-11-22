from concurrent.futures import ProcessPoolExecutor, as_completed
from copy import deepcopy
from sys import argv

from diametr_limited_spanning_tree import construct_spanning_tree, find_nearest_neighbors, find_min_edge, remove_leaves, \
    find_center, Res
from graph_reader import read_matrix, read_vertexes, compute_distance
from print_utils import print_matrix, print_result, print_result_to_file, edge_to_str, print_formatted_matrix
from timer_util import timeit
from tree import Tree


def result_to_str(result: Tree):
    diameter = result.diameter
    res = f'{result.weight} {diameter[2]} {edge_to_str([diameter[0], diameter[1]])}'
    res += ''.join(sorted([f"e {edge_to_str(edge)}\n" for edge in result.edges]))
    return res

def find_diameter_limited_spanning_tree(graph, n, d, vertexes):
    radius, v_i, v = find_center(vertexes)
    solution = Res()
    results = set()
    h = set()
    # for r in list(set(1+0.05*x for x in range(0, 14))) + [1.25]:
    # for r in [1, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.35, 1.4, 1.45, 1.5, 1.55, 1.6, 2]:
    for r in [1, 1.05, 1.1, 1.15, 1.20, 1.25, 1.3, 1.35, 1.4, 1.45, 1.5]:
    # for r in [1.25]:
        radiuses = [None, radius, int(radius/r)]
        # radiuses = [None, radius]
        if (None, radius, int(radius/r)) in h:
            continue
        h.add((None, radius, int(radius/r)))
        print(radiuses)
        for i in range(0, n):
            spanning_tree = find_spanning_tree(graph, n, i, d, solution, radiuses)
            if not spanning_tree:
                continue
            stringed_res = result_to_str(spanning_tree)
            if stringed_res not in results:
                print_result_to_file(d, graph, spanning_tree)
            results.add(stringed_res)
            if solution.v is None:
                solution.v = spanning_tree.weight
                solution.t = spanning_tree
            elif solution.v > spanning_tree.weight:
                solution.v = spanning_tree.weight
                solution.t = spanning_tree
    return solution.t


# def find_diameter_limited_spanning_tree(graph, n, d, vertexes):
#     radius, v_i, v = find_center(vertexes)
#     print(radius, v_i, v, sep='\n')
#     radiuses = [None, radius, int(radius / 1.25)]
#     print(radiuses)
#     solution = find_spanning_tree(graph, n, v_i, d, None, radiuses)
#     print_result_to_file(d, graph, solution)
#     return solution


def find_diameter_limited_spanning_tree_concurrent(graph, n, d, vertexes):
    radius, v_i, v = find_center(vertexes)
    results = set()
    h = set()
    solution = Res()
    with ProcessPoolExecutor(max_workers=6) as executor:
        executors = []
        # for r in list(set(0.4+0.01*x for x in range(0, 80))):
        # for r in [1, 1.05, 1.1, 1.15, 1.20, 1.25, 1.3, 1.35, 1.4, 1.45, 1.5, 1.55, 1.65, 1.6, 2, 3]:
        for r in [1.25, 1.35]:
            # if (None, radius, int(radius/r)) in h:
            #     continue
            # h.add((None, radius, int(radius/r)))
            radiuses = [None, radius, int(radius/r)]
            executors.extend([executor.submit(find_spanning_tree, graph, n, i, d, solution, radiuses) for i in range(0, n, 25)])
            print(radiuses)
        for future in as_completed(executors):
            spanning_tree = future.result()
            if not spanning_tree:
                continue
            stringed_res = result_to_str(spanning_tree)
            if stringed_res not in results:
                print_result_to_file(d, graph, spanning_tree)
            results.add(stringed_res)
            if solution.v is None:
                solution.v = spanning_tree.weight
                solution.t = spanning_tree
            elif solution.v > spanning_tree.weight:
                solution.v = spanning_tree.weight
                solution.t = spanning_tree
    return solution.t


def find_spanning_tree(graph, n: int, start_node: int, d, old_res: Res, radius_range):
    depths = [0 for _ in range(n)]
    tree = Tree(n)
    tree.nodes.add(start_node)
    bad_edges = set()
    radiuses = list(radius_range)
    max_depth = int(d/2)
    tree, depths, bad_edges = construct_spanning_tree_by_radius(graph, tree, max_depth, depths, bad_edges, old_res,
                                                                radiuses)
    # print_matrix(tree.adj_matrix)
    if not tree:
        return tree
    print_result_to_file(d, graph, tree)
    optimized_tree = deepcopy(tree)
    remove_leaves(optimized_tree, depths)
    optimized_tree, depths, bad_edges = construct_spanning_tree(graph, optimized_tree, max_depth, depths,
                                                                bad_edges, old_res)
    if optimized_tree and tree.weight > optimized_tree.weight:
        return optimized_tree
    return tree


def construct_spanning_tree_by_radius(graph, tree, max_depth, depths, bad_edges, old_res: Res, radiuses):
    max_edge_count = tree.n - 1
    cur_radius = radiuses.pop()
    while len(tree.edges) < max_edge_count:
        if old_res.v and tree.weight > old_res.v:
            return None, None, None
        candidates = set()
        for node in tree.nodes:
            if depths[node] + 1 <= max_depth:
                if cur_radius is not None:
                    nearest_nodes = find_neighbors_in_radius(graph, tree, node, cur_radius)
                    candidates.update((node, nearest_node, graph[node][nearest_node]) for nearest_node in nearest_nodes)
                else:
                    nearest_nodes = find_nearest_neighbors(graph, tree, node)
                    candidates.update((node, nearest_node, graph[node][nearest_node]) for nearest_node in nearest_nodes)
        candidates.difference_update(bad_edges)
        if not candidates:
            cur_radius = radiuses.pop()
        while candidates and len(tree.edges) < max_edge_count:
            min_edge = find_min_edge(candidates)
            candidates.remove(min_edge)
            if min_edge[1] not in tree.nodes and depths[min_edge[0]] + 1 <= max_depth:
                tree.nodes.add(min_edge[1])
                tree.add_edge(min_edge)
                depths[min_edge[1]] = depths[min_edge[0]] + 1
            else:
                bad_edges.add(min_edge)
    return tree, depths, bad_edges


def find_neighbors_in_radius(graph, tree, node, radius) -> list:
    node_indies = []
    for neighbor_i, neighbor_dist in enumerate(graph[node]):
        if neighbor_i not in tree.nodes and neighbor_dist != 0 and neighbor_dist <= radius:
            node_indies.append(neighbor_i)
    return node_indies


@timeit
def main():
    graph = read_matrix(argv[1])
    d = int(len(graph) / 32 + 2)
    n = len(graph)
    # print_formatted_matrix(graph)
    vertexes = read_vertexes(f'Benchmark/Taxicab_{n}.txt')
    print(f'Max diameter = {d}', f'N = {n}', sep='\n')
    # tree = find_diameter_limited_spanning_tree_concurrent(graph, n, d, vertexes)
    tree = find_diameter_limited_spanning_tree(graph, n, d, vertexes)
    print_result(graph, tree)
    # print_matrix(tree.adj_matrix)


if __name__ == '__main__':
    main()
