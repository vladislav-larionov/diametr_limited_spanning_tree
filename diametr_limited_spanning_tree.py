from sys import argv

from graph_reader import read_matrix
from print_utils import print_matrix, print_result, print_result_to_file, edge_to_str
from timer_util import timeit
from tree import Tree


def result_to_str(result: Tree):
    diameter = result.diameter
    res = f'{result.weight} {diameter[2]} {edge_to_str([diameter[0], diameter[1]])}'
    res += ''.join(sorted([f"e {edge_to_str(edge)}\n" for edge in result.edges]))
    return res


def find_diameter_limited_spanning_tree(graph, n, d):
    solution = None
    results = set()
    # for i in range(0, len(graph), 4):
    for i in range(n):
        spanning_tree = find_spanning_tree(graph, n, i, d, solution.weight if solution else None)
        if not spanning_tree:
            continue
        stringed_res = result_to_str(spanning_tree)
        if stringed_res not in results:
            print_result_to_file(d, graph, spanning_tree)
        results.add(stringed_res)
        if solution is None:
            solution = spanning_tree
        elif solution.weight > spanning_tree.weight:
            solution = spanning_tree
    return solution


# def find_diameter_limited_spanning_tree(graph, n, d):
#     solution = find_spanning_tree(graph, n, 0, d, None)
#     # print_result_to_file(d, graph, solution)
#     return solution

def find_spanning_tree(graph, n: int,  start_node: int, d, old_res: int):
    # TODO  подумать о том, чтобы дополнять список кандидатов при поиске соседей и добавлении вершины
    # TODO  опробовать брать рёбра, которые дают наименьший диаметр
    tree = Tree(n)
    tree.nodes.add(start_node)
    max_edge_count = tree.n - 1
    bad_edges = set()
    for i in range(max_edge_count):
        if old_res and tree.weight > old_res:
            return None
        candidates = set()
        for node in tree.nodes:
            # TODO Попробовать брать все с одинаковым весом
            # nearest_nodes = find_nearest_neighbors(graph, tree, node)
            # candidates.update((node, nearest_node, graph[node][nearest_node]) for nearest_node in nearest_nodes)
            nearest_node = find_nearest_neighbor(graph, tree, node)
            candidates.add((node, nearest_node, graph[node][nearest_node]))
        candidates.difference_update(bad_edges)
        while True:
            min_edge = find_min_edge(candidates)
            tree.nodes.add(min_edge[1])
            tree.add_edge(min_edge)
            diameter = tree.diameter
            if diameter[2] <= d:
                break
            tree.nodes.remove(min_edge[1])
            tree.remove_edge_by_index(-1)
            candidates.remove(min_edge)
            bad_edges.add(min_edge)
    return tree


def find_nearest_neighbor(graph, tree, node):
    min_dist = 999999999
    node_index = -1
    for neighbor_i, neighbor_dist in enumerate(graph[node]):
        if neighbor_dist != 0 and neighbor_i not in tree.nodes and neighbor_dist < min_dist:
            min_dist = neighbor_dist
            node_index = neighbor_i
    return node_index


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


@timeit
def main():
    graph = read_matrix(argv[1])
    d = int(len(graph) / 32 + 2)
    n = len(graph)
    print(f'Max diameter = {d}', f'N = {n}', sep='\n')
    tree = find_diameter_limited_spanning_tree(graph, n, d)
    print_result(graph, tree)
    # print_matrix(tree.adj_matrix)


if __name__ == '__main__':
    main()
