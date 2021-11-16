from sys import argv

from graph_reader import read_matrix
from print_utils import print_matrix, print_result, print_result_to_file
from timer_util import timeit
from tree import Tree


# def find_diameter_limited_spanning_tree(graph, d):
#     solution = None
#     for i in range(1, len(graph)):
#         spanning_tree = find_spanning_tree(graph, i, d)
#         print_result_to_file(d, graph, spanning_tree)
#         if not solution and solution.weight > spanning_tree.weight:
#             solution = spanning_tree
#     return solution


def find_diameter_limited_spanning_tree(graph, d):
    solution = find_spanning_tree(graph, 0, d)
    print_result_to_file(d, graph, solution)
    return solution


def find_spanning_tree(graph, start_node: int, d):
    # TODO  Не искать всё время, а брать из отсортированного списка
    #  подумать о том, чтобы дополнять список кандидатов при поиске соседей и добавлении вершины
    tree = Tree(len(graph))
    tree.nodes.add(start_node)
    max_edge_count = tree.n - 1
    bad_edges = set()
    for i in range(max_edge_count):
        candidates = set()
        for node in tree.nodes:
            nearest_node = find_nearest_neighbors(graph, tree, node)
            candidates.add((node, nearest_node, graph[node][nearest_node]))
        candidates.difference_update(bad_edges)
        if not candidates:
            print(tree)
        while True:
            min_edge = find_min_edge(candidates, tree)
            tree.nodes.add(min_edge[1])
            tree.edges.append(min_edge)
            diameter = tree.diameter
            if diameter[2] <= d:
                break
            tree.nodes.remove(min_edge[1])
            tree.edges.remove(min_edge)
            candidates.remove(min_edge)
            bad_edges.add(min_edge)
    return tree


def find_nearest_neighbors(graph, tree, node):
    min_dist = 999999999
    node_index = -1
    for neighbor_i, neighbor_dist in enumerate(graph[node]):
        if neighbor_dist != 0 and neighbor_i not in tree.nodes and neighbor_dist < min_dist:
            min_dist = neighbor_dist
            node_index = neighbor_i
    return node_index


def find_min_edge(edges, tree):
    # filtered = filter(lambda edge: edge[1] not in tree.nodes, edges)
    # return min(filtered, key=lambda edge: edge[2])
    return min(edges, key=lambda edge: edge[2])


@timeit
def main():
    graph = read_matrix(argv[1])
    d = int(len(graph) / 32 + 2)
    print(f'Max diameter is {d}')
    tree = find_diameter_limited_spanning_tree(graph, d)
    print_result(graph, tree)
    # print_matrix(tree.adj_matrix)


if __name__ == '__main__':
    main()
