from sys import argv

from graph_reader import read_matrix
from print_utils import print_matrix, print_result, print_matrix_graph
from tree import Tree


def find_diameter_limited_spanning_tree(graph, d):
    spanning_tree = find_spanning_tree(graph, 0)
    return spanning_tree


def find_spanning_tree(graph, start_node: int):
    tree = Tree()
    tree.nodes.add(start_node)
    max_edge_count = len(graph) - 1
    for i in range(max_edge_count):
        candidates = []
        for node in tree.nodes:
            nearest_node = find_nearest_neighbors(graph, tree, node)
            if nearest_node >= 0:
                candidates.append([node, nearest_node, graph[node][nearest_node]])
        if not candidates:
            raise RuntimeError("Empty candidate list")
        min_edge = find_min_edge(candidates, tree)
        tree.nodes.add(min_edge[1])
        tree.edges.append(min_edge)
    return tree


def find_nearest_neighbors(graph, tree, node):
    min_dist = 999999999
    node_index = -1
    for neighbor_i, neighbor_dist in enumerate(graph[node]):
        if neighbor_dist != 0 and neighbor_i not in tree.nodes and neighbor_dist < min_dist:
            min_dist = neighbor_dist
            node_index = neighbor_i
    return node_index


# def find_min_edge(edges, tree):
#     min_edge = edges[0]
#     for edge_i, edge in enumerate(edges):
#         if edge[2] < min_edge[2] and edge[1] not in tree.nodes:
#             min_edge = edge
#     return min_edge
def find_min_edge(edges, tree):
    filtered = filter(lambda edge: edge[1] not in tree.nodes, edges)
    return min(filtered, key=lambda edge: edge[2])


def main():
    graph = read_matrix(argv[1])
    d = int(len(graph) / 32 + 2)
    print(f'Max diameter is {d}')
    tree = find_diameter_limited_spanning_tree(graph, d)
    # print_result(graph, tree)
    print(tree.weight)
    print(tree.diameter)


if __name__ == '__main__':
    main()
