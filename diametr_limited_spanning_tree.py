from sys import argv

from graph_reader import read_matrix
from print_utils import print_matrix, print_result, print_matrix_graph, print_result_to_file
from tree import Tree


def find_diameter_limited_spanning_tree(graph, d):
    solution = None
    for i in range(len(graph)):
        spanning_tree = find_spanning_tree(graph, i, d)
        print_result_to_file(d, graph, spanning_tree)
        if solution and solution.weight > spanning_tree.weight:
            solution = spanning_tree
    return solution

# def find_diameter_limited_spanning_tree(graph, d):
#     solution = None
#     # for i in range(len(graph)):
#     solution = find_spanning_tree(graph, 0, d-1)
#     print_result_to_file(d-1, graph, solution)
#     return solution


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
        # min_edge = find_min_edge(candidates, tree)
        # tree.nodes.add(min_edge[1])
        # tree.edges.add(min_edge)
        while True:
            min_edge = find_min_edge(candidates, tree)
            tree.nodes.add(min_edge[1])
            tree.edges.add(min_edge)
            diam = tree.distance_matrix.diameter_path_in_edges
            # print(diam)
            if diam <= d:
                break
            tree.nodes.remove(min_edge[1])
            tree.edges.remove(min_edge)
            bad_edges.add(min_edge)
            candidates.difference_update(bad_edges)
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


def main():
    graph = read_matrix(argv[1])
    d = int(len(graph) / 32 + 2)
    print(f'Max diameter is {d}')
    tree = find_diameter_limited_spanning_tree(graph, d)
    print_result(graph, tree)
    # print(tree.weight)
    # print(tree.diameter)
    print_matrix(tree.adj_matrix)


if __name__ == '__main__':
    main()
