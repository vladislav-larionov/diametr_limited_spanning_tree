from concurrent.futures import as_completed, ProcessPoolExecutor
from copy import deepcopy
from sys import argv

from graph_reader import read_matrix, read_vertexes, compute_distance
from print_utils import print_result, print_result_to_file, edge_to_str, print_formatted_matrix
from timer_util import timeit
from tree import Tree


def result_to_str(result: Tree):
    diameter = result.diameter
    res = f'{result.weight} {diameter}'
    res += ''.join(sorted([f"e {edge_to_str(edge)}\n" for edge in result.edges]))
    return res


class Res:
    def __init__(self, v=None):
        self.v = v
        self.t = None


def find_diameter_limited_spanning_tree(graph, n, d, vertexes):
    radius, v_i, v = find_center(vertexes)
    results = set()
    solution = Res()
    with ProcessPoolExecutor(max_workers=2) as executor:
        executors = [executor.submit(find_spanning_tree, graph, n, i, d, solution, v_i) for i in range(0, n)]
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
    #     spanning_tree = find_spanning_tree(graph, n, i, d, solution, v_i)
    #     if not spanning_tree:
    #         continue
    #     stringed_res = result_to_str(spanning_tree)
    #     if stringed_res not in results:
    #         print_result_to_file(d, graph, spanning_tree)
    #     results.add(stringed_res)
    #     if solution.v is None:
    #         solution.v = spanning_tree.weight
    #         solution.t = spanning_tree
    #     elif solution.v > spanning_tree.weight:
    #         solution.v = spanning_tree.weight
    #         solution.t = spanning_tree
    return solution.t


def find_spanning_tree(graph, n: int, start_node: int, d, old_res, v_i):
    depths = [0 for _ in range(n)]
    tree = Tree(n)
    tree.nodes.add(start_node)
    max_depth = int(d/2)
    tree, depths = construct_spanning_tree(graph, tree, max_depth, depths, old_res)
    if not tree:
        return tree
    print_result_to_file(d, graph, tree)
    optimized_tree = deepcopy(tree)
    remove_leaves(optimized_tree, depths)
    optimized_tree, depths = construct_spanning_tree(graph, optimized_tree, max_depth, depths, old_res)
    if optimized_tree and tree.weight > optimized_tree.weight:
        return optimized_tree
    return tree


def remove_leaves(tree, depths, count=None):
    l_edges, leaves = tree.get_leaves()
    if count:
        for leaf in l_edges[:count]:
            tree.remove_edge(leaf)
            depths[leaf[1]] = 0
            tree.nodes.remove(leaf[1])
    else:
        for leaf in l_edges:
            tree.remove_edge(leaf)
            depths[leaf[1]] = 0
        for leaf in leaves:
            tree.nodes.remove(leaf)


def construct_spanning_tree(graph, tree, max_depth, depths, old_res: Res):
    max_edge_count = tree.n - 1
    while len(tree.edges) < max_edge_count:
        if old_res.v and tree.weight > old_res.v:
            return None, None
        candidates = list()
        for node in tree.nodes:
            if depths[node] + 1 <= max_depth:
                candidates.extend(find_candidates(graph, node, tree.nodes, max_depth, depths))

        # min_edges = find_min_edge(candidates)
        min_edges = candidates
        min_edges.sort(key=lambda edge: (edge[2], edge[3]), reverse=True)
        min_edge = min_edges[-1]
        depths[min_edge[1]] = depths[min_edge[0]] + 1
        tree.nodes.add(min_edge[1])
        tree.add_edge((min_edge[0], min_edge[1], min_edge[2]))
    return tree, depths


def find_candidates(graph, node, stop_list, max_depth, depths):
    candidates = set()
    if depths[node] + 1 <= max_depth:
        nearest_nodes = find_nearest_neighbors(graph, stop_list, node)
        candidates.update((node, nearest_node, graph[node][nearest_node], depths[node] + 1) for nearest_node in nearest_nodes)
    return candidates


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


def find_nearest_neighbors(graph, stop_list, node) -> list:
    min_dist = 999999999
    node_indies = []
    for neighbor_i, neighbor_dist in enumerate(graph[node]):
        if neighbor_i not in stop_list and neighbor_dist != 0:
            if neighbor_dist < min_dist:
                min_dist = neighbor_dist
                node_indies.clear()
                node_indies.append(neighbor_i)
            elif neighbor_dist == min_dist:
                node_indies.append(neighbor_i)
    return node_indies


def find_min_edge(edges):
    # return min(edges, key=lambda edge: edge[2])
    mins = []
    min_v = None
    for edge in edges:
        if min_v is None:
            mins.append(edge)
            min_v = edge[2]
        elif edge[2] < min_v:
            min_v = edge[2]
            mins.clear()
            mins.append(edge)
        elif edge[2] == min_v:
            mins.append(edge)
    return mins


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
    vertexes = read_vertexes(f'Benchmark/Taxicab_{n}.txt')
    print(f'Max diameter = {d}', f'N = {n}', sep='\n')
    tree = find_diameter_limited_spanning_tree(graph, n, d, vertexes)
    if tree:
        print_result(graph, tree)
    else:
        print('tree is none')
    # with open('res_matrix.txt', 'w', encoding='utf-8') as f:
    #     f.write(print_utils.matrix_to_str(tree.adj_matrix))
    # print_matrix(tree.adj_matrix)


if __name__ == '__main__':
    main()
