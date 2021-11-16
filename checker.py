import sys

import print_utils
from checkers.connected_components_counter import count_connected_components
from graph_reader import read_matrix
from checkers.loop_finder import has_loop


def read_res(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        weight = int(file.readline().split(', ')[0].split(' ')[-1])
        n = int(file.readline().split(' ')[-1])
        edges = [list(map(int, line.lstrip('e ').split(' '))) for line in file.readlines()[:n]]
        print(f'v = {len(edges) + 1}')
        print(f'w = {weight}')
        print(f'n = {n}')
        # for row in edges:
        #     print(row)
    return edges, weight, len(edges) + 1


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


def main():
    res_file_path = sys.argv[1]
    edges, weight, n = read_res(res_file_path)
    graph = read_matrix(f'Taxicab_{n}_matrix.txt')
    print(f'Edges existing: {check_edge_existing(graph, edges, weight)}')
    print(f'Loop existing:  {has_loop(n, edges)}')
    print(f'Connected components:  {count_connected_components(n, edges)}')
    if len(sys.argv) > 2:
        print_utils.print_matrix(create_tree_by_edge(graph, edges, n))


if __name__ == '__main__':
    main()