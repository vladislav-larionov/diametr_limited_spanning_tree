import sys

from graph_reader import read_matrix
from loop_finder import has_loop


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
    return edges, weight


def check_edge_existing(graph, edges, weight):
    total_weight = 0
    for edge in edges:
        total_weight += graph[edge[0]][edge[1]]
    return total_weight == weight


def main():
    res_file_path = sys.argv[1]
    edges, weight = read_res(res_file_path)
    graph = read_matrix(f'Taxicab_{len(edges) + 1}_matrix.txt')
    print(f'Edges existing: {check_edge_existing(graph, edges, weight)}')
    print(f'Loop existing:  {has_loop(len(graph), edges)}')


if __name__ == '__main__':
    main()