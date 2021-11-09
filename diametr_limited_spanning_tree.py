from sys import argv

from graph_reader import read_matrix
from print_utils import print_matrix, print_result, print_matrix_graph
from tree import Tree


def find_diameter_limited_spanning_tree(graph, d):
    res = find_spanning_tree(graph, 64, d, 0)
    return res


def find_spanning_tree(graph, max_edge_count: int, d: int, start_node: int):
    tree = Tree()
    tree.nodes.add(start_node)
    while len(tree.nodes) < max_edge_count:
        candidates = list()
        for node in tree.nodes:
            nearest_node = find_nearest_neighbors(graph, tree, node)
            if nearest_node:
                candidates.append([node, nearest_node, graph[node][nearest_node]])
            else:
                print(node)
        min_edge = find_min_edge(candidates, tree)
        # print(candidates)
        # print()
        tree.nodes.add(min_edge[1])
        tree.edges.append(min_edge)
    return tree


def find_nearest_neighbors(graph, tree, node):
    min_dist = 999999999
    node_index = None
    for neighbor_i, neighbor_dist in enumerate(graph[node]):
        if neighbor_dist != 0 and neighbor_i not in tree.nodes and neighbor_dist < min_dist:
            min_dist = neighbor_dist
            node_index = neighbor_i
    return node_index


def find_min_edge(edges, tree):
    min_edge = edges[0]
    for edge_i, edge in enumerate(edges):
        if edge[2] < min_edge[2] and not (edge[1] in tree.nodes and edge[0] in tree.nodes):
            min_edge = edge
    return min_edge


def main():
    graph = read_matrix(argv[1])
    d = int(len(graph) / 32 + 2)
    tree = find_diameter_limited_spanning_tree(graph, d)
    print(tree.weight)
    adj_matrix = tree.adj_matrix
    print_matrix(adj_matrix)
    print(tree.diameter)


if __name__ == '__main__':
    main()
