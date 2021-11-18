import sys


def read_res(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        comment = file.readline()
        tree_info = file.readline()
        edges = [list(map(int, line.lstrip('e ').split(' '))) for line in file.readlines()]
    return comment, tree_info, edges


def print_res(comment, tree_info, edges):
    with open('fixed.txt', 'w', encoding='utf-8') as file:
        file.writelines([comment, tree_info])
        file.writelines(list(map(lambda e: f'e {e[0]} {e[1]}\n', [edge for edge in edges])))
    return comment, tree_info, edges


def main():
    res_file_path = sys.argv[1]
    comment, tree_info, edges = read_res(res_file_path)
    edges = list(map(lambda e: [e[0]+1, e[1]+1], [edge for edge in edges]))
    print_res(comment, tree_info, edges)


if __name__ == '__main__':
    main()
