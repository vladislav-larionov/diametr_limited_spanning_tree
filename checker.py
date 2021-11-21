import sys
from collections import deque

import print_utils
import numpy as np
from checkers.connected_components_counter import count_connected_components
from graph_reader import read_matrix
from checkers.loop_finder import has_loop


def read_res(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        info = file.readline().split(', ')
        weight = int(info[0].split(' ')[-1])
        d = int(info[1].split(' ')[-1])
        tree_info = file.readline().split(' ')
        n = int(tree_info[-2])
        e = int(tree_info[-1])
        edges = [list(map(int, line.lstrip('e ').split(' '))) for line in file.readlines()[:n]]
        edges = list(map(lambda e: [e[0]-1, e[1]-1], [edge for edge in edges]))
        print(f'w = {weight}')
        print(f'n = {n}')
        print(f'edges = {e}')
        print(f'd = {d}')
        # for row in edges:
        #     print(row)
    return edges, weight, n, d, e


def check_edge_existing(graph, edges, weight):
    total_weight = 0
    for edge in edges:
        total_weight += graph[edge[0]][edge[1]]
    return total_weight == weight


def create_tree_by_edge(graph, edges, n):
    tree = [[0 for i in range(n)] for j in range(n)]
    for edge in edges:
        tree[edge[0]][edge[1]] = graph[edge[0]][edge[1]]
        tree[edge[1]][edge[0]] = graph[edge[1]][edge[0]]
    return tree


def bfs_by_matrix(graph, n, node):
    dist = [0 for i in range(n)]
    queue = deque()
    visited = {node}
    queue.append(node)
    while queue:
        s = queue.popleft()
        for neighbor_i, neighbor_dist in enumerate(graph[s]):
            if neighbor_dist != 0 and neighbor_i not in visited:
                dist[neighbor_i] = dist[s] + 1
                visited.add(neighbor_i)
                queue.append(neighbor_i)
    return dist


def diameter(tree, n, start):
    from_node = to_node = 0
    start_node = start

    dist = bfs_by_matrix(tree, n, start_node)

    # for i, value in enumerate(dist):
    #     if dist[i] > dist[from_node]:
    #         from_node = i
    from_node = np.argmax(dist)
    dist = bfs_by_matrix(tree, n, from_node)

    # for i, value in enumerate(dist):
    #     if dist[i] > dist[to_node]:
    #         to_node = i
    to_node = np.argmax(dist)
    return from_node, to_node, dist[to_node]


def edges_to_node_set(edges):
    nodes = set()
    for e in edges:
        nodes.add(e[0])
        nodes.add(e[1])
    return nodes


def main():
    res_file_path = sys.argv[1]
    edges, weight, n, d, e = read_res(res_file_path)
    graph = read_matrix(f'Taxicab_{n}_matrix.txt')
    print(f'Nodes: {len(edges_to_node_set(edges))} {n == len(edges_to_node_set(edges))}')
    print(f'Edges: {len(edges)} {len(edges) == e}')
    print(f'Edges existing: {check_edge_existing(graph, edges, weight)}')
    loop = has_loop(n, edges)
    print(f'Loop existing:  {loop} {loop == False}')
    components = count_connected_components(n, edges)
    print(f'Connected components:  {components} {1 == components}')
    diam = diameter(create_tree_by_edge(graph, edges, n), n, edges[0][0])
    d = int(len(graph) / 32 + 2)
    print(f'Diameter:  {diam}, {diam[2] <= d}')
    if len(sys.argv) > 2:
        with open('checked_matrix.txt', 'w', encoding='utf-8') as f:
            f.write(print_utils.matrix_to_str(create_tree_by_edge(graph, edges, n)))


if __name__ == '__main__':
    main()