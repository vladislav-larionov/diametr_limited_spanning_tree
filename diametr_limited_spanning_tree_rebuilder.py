from copy import deepcopy
from sys import argv

from checker import read_res
from diametr_limited_spanning_tree import remove_leaves, find_nearest_neighbors, find_min_edge, Res, result_to_str
from graph_reader import read_matrix
from print_utils import print_result, print_result_to_file
from timer_util import timeit
from tree import Tree


def remove_max_leaf(tree, depths, count=None):
    l_edges, leaves = tree.get_leaves()
    if not count:
        count = len(l_edges)
    for leaf in sorted(l_edges[:count], key=lambda e: e[2])[:count]:
        tree.remove_edge(leaf)
        depths[leaf[1]] = 0
        tree.nodes.remove(leaf[1])


def reconstruct_spanning_tree(graph, tree, d, old):
    bads = set()
    while len(tree.nodes) < tree.n:
        if old is not None and tree.weight >= old:
            return None
        candidates = set()
        for node in tree.nodes:
            nearest_nodes = find_nearest_neighbors(graph, tree.nodes, node)
            candidates.update((node, nearest_node, graph[node][nearest_node]) for nearest_node in nearest_nodes)
        candidates.difference_update(bads)
        while True:
            min_edges = find_min_edge(candidates)
            # min_edges.sort(key=lambda edge: edge[2], reverse=True)
            min_edge = min_edges[-1]
            candidates.remove(min_edge)
            tree.nodes.add(min_edge[1])
            tree.add_edge((min_edge[0], min_edge[1], min_edge[2]))
            if tree.diameter <= d:
                break
            tree.nodes.remove(min_edge[1])
            tree.remove_edge(min_edge)
            bads.add(min_edge)
    return tree


def create_tree_by_edge(graph, edges, n):
    tree = Tree(n)
    for edge in edges:
        edge.append(graph[edge[0]][edge[1]])
        tree.nodes.add(edge[0])
        tree.nodes.add(edge[1])
        tree.add_edge(tuple(edge))
    return tree


def bruteforce(graph, tree, d):
    depths = [0 for _ in range(tree.n)]
    solution = deepcopy(tree)
    remove_leaves(tree, depths)
    # remove_max_leaf(tree, depths, 3)
    results = set()
    bads = set()
    for i in {i for i in range(tree.n)} - tree.nodes:
        to_opt = deepcopy(tree)
        candidates = sorted({(node, i, graph[i][node]) for node in to_opt.nodes} - bads, key=lambda e: e[2], reverse=True)
        # candidates = [(node, i, graph[i][node]) for node in to_opt.nodes]
        for min_edge in candidates:
            found = False
            to_opt1 = deepcopy(to_opt)
            while not found:
                to_opt1.nodes.add(min_edge[1])
                to_opt1.add_edge((min_edge[0], min_edge[1], min_edge[2]))
                bads.add(min_edge)
                if to_opt1.diameter <= d:
                    found = True
                else:
                    to_opt1.nodes.remove(min_edge[1])
                    to_opt1.remove_edge(min_edge)
            spanning_tree = reconstruct_spanning_tree(graph, to_opt1, d, solution.weight if solution else None)
            if not spanning_tree:
                continue
            stringed_res = result_to_str(spanning_tree)
            if stringed_res not in results:
                print_result_to_file(d+1, graph, spanning_tree)
            results.add(stringed_res)
            if solution is None:
                solution = spanning_tree
            elif solution.weight > spanning_tree.weight:
                solution = spanning_tree
    return solution

@timeit
def main():
    edges, weight, n, _d, _e = read_res(argv[1])
    graph = read_matrix(f'Taxicab_{n}_matrix.txt')
    d = int(len(graph) / 32 + 2)
    tree = create_tree_by_edge(graph, edges, n)
    if len(argv) > 2:
        tree = bruteforce(graph, tree, d)
    else:
        reconstruct_spanning_tree(graph, tree, d, None)
    if tree:
        print_result_to_file(d, graph, tree, f'reconstructed_{n}_tree.txt')
        print_result(graph, tree)
    else:
        print('tree is none')
    # with open('res_matrix.txt', 'w', encoding='utf-8') as f:
    #     f.write(print_utils.matrix_to_str(tree.adj_matrix))
    # print_matrix(tree.adj_matrix)


# первый параметр - файл с деревом
# второй параметр - флаг полного перебора. Если его нет, то пройдёт только одна итерация
if __name__ == '__main__':
    main()
