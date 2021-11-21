from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
from datetime import datetime
from sys import argv

import print_utils
from graph_reader import read_matrix, read_vertexes, compute_distance
from print_utils import print_matrix, print_result, print_result_to_file, edge_to_str, print_formatted_matrix
from timer_util import timeit
from tree import Tree


def result_to_str(result: Tree):
    diameter = result.diameter
    res = f'{result.weight} {diameter[2]} {edge_to_str([diameter[0], diameter[1]])}'
    res += ''.join(sorted([f"e {edge_to_str(edge)}\n" for edge in result.edges]))
    return res


class Res:
    def __init__(self, v):
        self.v = v
        self.t = None


def find_diameter_limited_spanning_tree(graph, n, d, vertexes):
    radius, v_i, v = find_center(vertexes)
    solution = Res(None)
    results = set()
    # with ThreadPoolExecutor(max_workers=15) as executor:
    with ProcessPoolExecutor(max_workers=8) as executor:
        executors = [executor.submit(find_spanning_tree, graph, n, i, d, solution, v_i) for i in range(n)]
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
    # for i in range(n):
    #     spanning_tree = find_spanning_tree(graph, n, i, d, solution.weight if solution else None, v_i)
    #     if not spanning_tree:
    #         continue
    #     stringed_res = result_to_str(spanning_tree)
    #     if stringed_res not in results:
    #         print_result_to_file(d, graph, spanning_tree)
    #     results.add(stringed_res)
    #     if solution is None:
    #         solution = spanning_tree
    #     elif solution.weight > spanning_tree.weight:
    #         solution = spanning_tree
    return solution.t


# def find_diameter_limited_spanning_tree(graph, n, d, vertexes):
#     radius, v_i, v = find_center(vertexes)
#     solution = find_spanning_tree(graph, n, v_i, d, None)
#     print_result_to_file(d, graph, solution)
#     return solution


def find_spanning_tree(graph, n: int, start_node: int, d, old_res, v_i):
    o = old_res.v
    depths = [0 for _ in range(n)]
    tree = Tree(n)
    tree.nodes.add(start_node)
    max_depth = int(d/2)
    bad_edges = set()
    tree, depths, bad_edges = construct_spanning_tree(graph, tree, max_depth, depths, bad_edges, o)
    if not tree:
        return tree
    print_result_to_file(d, graph, tree)
    leaves = tree.get_leaves()
    for leaf in leaves:
        tree.nodes.remove(leaf[1])
        tree.remove_edge(leaf)
        depths[leaf[1]] = 0
    tree, depths, bad_edges = construct_spanning_tree(graph, tree, max_depth, depths, bad_edges, o)
    return tree


def construct_spanning_tree(graph, tree, max_depth, depths, bad_edges, old_res):
    max_edge_count = tree.n - 1
    while len(tree.edges) < max_edge_count:
        if old_res and tree.weight > old_res:
            return None, None, None
        candidates = set()
        for node in tree.nodes:
            nearest_nodes = find_nearest_neighbors(graph, tree, node)
            candidates.update((node, nearest_node, graph[node][nearest_node]) for nearest_node in nearest_nodes)
        # candidates = {(node, nearest_node, graph[node][nearest_node])
        #               for node in tree.nodes
        #               for nearest_node in find_nearest_neighbors(graph, tree, node)}
        candidates.difference_update(bad_edges)
        while True:
            min_edge = find_min_edge(candidates)
            candidates.remove(min_edge)
            tree.nodes.add(min_edge[1])
            tree.add_edge(min_edge)
            depths[min_edge[1]] = depths[min_edge[0]] + 1
            if depths[min_edge[1]] > max_depth:
                depths[min_edge[1]] = 0
                tree.nodes.remove(min_edge[1])
                tree.remove_edge_by_index(-1)
                bad_edges.add(min_edge)
            else:
                break
    return tree, depths, bad_edges


def find_nearest_neighbor(graph, tree, node):
    min_dist = 999999999
    node_index = -1
    for neighbor_i, neighbor_dist in enumerate(graph[node]):
        if neighbor_dist != 0 and neighbor_i not in tree.nodes and neighbor_dist < min_dist:
            min_dist = neighbor_dist
            node_index = neighbor_i
    return node_index


def find_neighbors_in_radius(graph, tree, node, radius) -> list:
    node_indies = []
    for neighbor_i, neighbor_dist in enumerate(graph[node]):
        if neighbor_i not in tree.nodes and neighbor_dist != 0 and neighbor_dist <= radius:
            node_indies.append(neighbor_i)
    return node_indies


def find_nearest_neighbors(graph, tree, node) -> list:
    min_dist = 999999999
    node_indies = []
    for neighbor_i, neighbor_dist in enumerate(graph[node]):
        if neighbor_i not in tree.nodes and neighbor_dist != 0:
            if neighbor_dist < min_dist:
                min_dist = neighbor_dist
                node_indies.clear()
                node_indies.append(neighbor_i)
            elif neighbor_dist == min_dist:
                node_indies.append(neighbor_i)
    return node_indies


def find_min_edge(edges):
    return min(edges, key=lambda edge: edge[2])


def find_center(vertexes):
    p_max = list(vertexes[0])
    p_min = list(vertexes[0])
    for v in vertexes:
        if v[0] > p_max[0]:
            p_max[0] = v[0]
        if v[1] > p_max[1]:
            p_max[1] = v[1]
        if p_min[0] > v[0]:
            p_min[0] = v[0]
        if p_min[1] > v[1]:
            p_min[1] = v[1]

    p_center = (int((p_max[0] + p_min[0]) / 2), int((p_max[1] + p_min[1]) / 2))
    r = compute_distance(p_center, p_max) / 2
    v_center = 0
    for i, v in enumerate(vertexes):
        if compute_distance(v, p_center) < compute_distance(vertexes[v_center], p_center):
            v_center = i
    return r, v_center, vertexes[v_center]


@timeit
def main():
    graph = read_matrix(argv[1])
    d = int(len(graph) / 32 + 2)
    n = len(graph)
    # print_formatted_matrix(graph)
    vertexes = read_vertexes(f'Benchmark/Taxicab_{n}.txt')
    print(f'Max diameter = {d}', f'N = {n}', sep='\n')
    print(f'start: {datetime.now()}')
    tree = find_diameter_limited_spanning_tree(graph, n, d, vertexes)
    print_result(graph, tree)
    # with open('res_matrix.txt', 'w', encoding='utf-8') as f:
    #     f.write(print_utils.matrix_to_str(tree.adj_matrix))
    # print_matrix(tree.adj_matrix)


if __name__ == '__main__':
    main()
