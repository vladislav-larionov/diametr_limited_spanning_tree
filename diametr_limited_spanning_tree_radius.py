from concurrent.futures import ProcessPoolExecutor, as_completed
from copy import deepcopy
from sys import argv

from diametr_limited_spanning_tree import find_nearest_neighbors,  remove_leaves, \
    find_center, Res, construct_spanning_tree, result_to_str
from graph_reader import read_matrix, read_vertexes
from print_utils import print_result, print_result_to_file, edge_to_str, print_formatted_matrix
from timer_util import timeit
from tree import Tree


def find_diameter_limited_spanning_tree(graph, n, d, vertexes):
    radius, v_i, v = find_center(vertexes)
    solution = Res()
    results = set()
    # for r in [1, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.35, 1.4, 1.45, 1.5, 1.55, 1.6, 2]:
    # for r in [1, 1.05, 1.1, 1.15, 1.20, 1.25, 1.3, 1.35, 1.4, 1.45, 1.5]:
    radiuses = [radius] + [int(radius/r) for r in [1.05, 1.1, 1.15, 1.20, 1.25, 1.3, 1.35, 1.4, 1.45]]
    print(radiuses)
    for i in range(0, n):
        spanning_tree = find_spanning_tree(graph, n, i, d, solution, radiuses)
        if not spanning_tree:
            continue
        stringed_res = result_to_str(spanning_tree)
        if stringed_res not in results:
            print_result_to_file(d+1, graph, spanning_tree)
        results.add(stringed_res)
        if solution.v is None:
            solution.v = spanning_tree.weight
            solution.t = spanning_tree
        elif solution.v > spanning_tree.weight:
            solution.v = spanning_tree.weight
            solution.t = spanning_tree
    return solution.t



def find_diameter_limited_spanning_tree_concurrent(graph, n, d, vertexes):
    radius, v_i, v = find_center(vertexes)
    results = set()
    solution = Res()
    with ProcessPoolExecutor(max_workers=2) as executor:
        executors = []
        radiuses = [radius] + [int(radius/r) for r in [1, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.35, 1.4, 1.45, 1.5, 1.55, 1.6, 2]]
        # radiuses = [radius] + [int(radius/r) for r in [1.05, 1.1, 1.15, 1.20, 1.25, 1.3, 1.35, 1.4, 1.45]]
        # radiuses = [radius] + [int(radius/r) for r in [1]]
        executors.extend([executor.submit(find_spanning_tree, graph, n, i, d, solution, radiuses) for i in range(0, n)])
        print(radiuses)
        for future in as_completed(executors):
            spanning_tree = future.result()
            if not spanning_tree:
                continue
            stringed_res = result_to_str(spanning_tree)
            if stringed_res not in results:
                print_result_to_file(d+1, graph, spanning_tree)
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
    radiuses = list(radius_range)
    max_depth = int(d/2)
    tree, depths = construct_spanning_tree_by_radius(graph, tree, max_depth, depths, old_res, radiuses)
    # print_matrix(tree.adj_matrix)
    if not tree:
        return tree
    print_result_to_file(d+1, graph, tree)
    for i in range(0, 10):
        optimized_tree = deepcopy(tree)
        optimized_depths = list(depths)
        remove_leaves(optimized_tree, depths)
        optimized_tree, optimized_depths = construct_spanning_tree(graph, optimized_tree, max_depth, optimized_depths, old_res)
        if optimized_tree and tree.weight > optimized_tree.weight:
            tree = optimized_tree
            depths = optimized_depths
    return tree


def construct_spanning_tree_by_radius(graph, tree, max_depth, depths, old_res: Res, radiuses):
    max_edge_count = tree.n - 1
    max_r_index = len(radiuses)
    while len(tree.edges) < max_edge_count:
        if old_res.v and tree.weight > old_res.v:
            return None, None
        candidates = set()
        cur_radius = max_r_index
        while not candidates and cur_radius:
            cur_radius -= 1
            for node in tree.nodes:
                if depths[node] + 1 <= max_depth:
                    nearest_nodes = find_neighbors_in_radius(graph, tree, node, radiuses[cur_radius])
                    candidates.update((node, nearest_node, graph[node][nearest_node], depths[node] + 1) for nearest_node in nearest_nodes)
        if not candidates:
            for node in tree.nodes:
                if depths[node] + 1 <= max_depth:
                    nearest_nodes = find_nearest_neighbors(graph, tree.nodes, node)
                    candidates.update((node, nearest_node, graph[node][nearest_node], depths[node] + 1) for nearest_node in nearest_nodes)
        candidates = sorted(candidates, key=lambda edge: (edge[3], edge[2]), reverse=True)
        while candidates and len(tree.edges) < max_edge_count:
            # min_edge = find_min_edge(candidates)
            # candidates.remove(min_edge)
            min_edge = candidates.pop()
            if min_edge[1] not in tree.nodes and depths[min_edge[0]] + 1 <= max_depth:
                tree.nodes.add(min_edge[1])
                tree.add_edge((min_edge[0], min_edge[1], min_edge[2]))
                depths[min_edge[1]] = depths[min_edge[0]] + 1
    return tree, depths


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
    tree = find_diameter_limited_spanning_tree_concurrent(graph, n, d, vertexes)
    # tree = find_diameter_limited_spanning_tree(graph, n, d, vertexes)
    if tree:
        print_result(graph, tree)
    else:
        print('none')
    # print_matrix(tree.adj_matrix)


if __name__ == '__main__':
    main()
