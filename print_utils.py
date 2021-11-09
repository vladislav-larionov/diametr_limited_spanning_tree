from tree import Tree


def print_matrix(matrix):
    for row in matrix:
        print(", ".join(map(str, row)))


def print_result(orig_graph, tree: Tree):
    print(f'c Вес дерева = {sum(map(lambda e: e[2], tree.edges))}, число листьев = ?')
    print(f'p edge {len(orig_graph)} {len(tree.edges)}')
    for e in sorted([f"e {edge_to_str(edge)}\n" for edge in tree.edges]):
        print(e, end='')


def print_result_to_file(k, orig_graph, tree_edges):
    with open(f'temp_res_{k}.txt', 'a+', encoding='utf-8') as file:
        file.write(f'c Вес дерева = {sum(map(lambda e: e[2],tree_edges))}, число листьев = ?\n')
        file.write(f'p edge {len(orig_graph)} {len(tree_edges)}\n')
        for e in sorted([f"e {edge_to_str(edge)}\n" for edge in tree_edges]):
            file.write(e)
        file.write("\n")
        # for edge in tree_edges:
        #     file.write(f"{edge}\n")
        # for row in k_min_spanning_tree.adj_mat:
        #     file.write(f'{", ".join(map(str, row))}\n')
        # file.write("\n")
        file.write("-------------------------------------------")
        file.write("\n")


def edge_to_str(edge):
    if edge[0] < edge[1]:
        return str(edge[0]) + " " + str(edge[1])
    else:
        return str(edge[1]) + " " + str(edge[0])


def print_matrix_graph(matrix):
    print('   |\t', end='')
    for i, _ in enumerate(matrix):
        print(f'{i:3}\t', end='')
    print()
    for j, row in enumerate(matrix):
        print(f'{j:3}|\t' + "\t".join([f'{el:3}' for el in row]))
