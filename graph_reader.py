def read_vertexes(filename):
    with open(filename) as file:
        _ = file.readline()
        return list(map(lambda l: [int(v) for v in l.split('	')], file.readlines()))


def compute_distance(vertex1, vertex2):
    return int(abs(vertex1[0] - vertex2[0]) + abs(vertex1[1] - vertex2[1]))


def create_graph(vertexes_):
    n = len(vertexes_)
    graph = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(0, n):
            if i != j:
                graph[i][j] = compute_distance(vertexes_[i], vertexes_[j])
    return graph


def matrix_to_edge_list(matrix_):
    edge_list = list()
    n = len(matrix_)
    for r in range(n):
        for c in range(r + 1, n):
            if matrix_[r][c] != 0:
                edge_list.append([r, c, matrix_[r][c]])
                print(r, c, matrix_[r][c])


def edge_list_to_matrix(edge_list):
    n = len(edge_list)
    matrix_ = [[0] * n for _ in range(n)]
    for it in edge_list:
        r, c, v = it
        matrix_[r][c] = matrix_[c][r] = v
    return matrix_


def read_graph_as_matrix(filename):
    vertexes_ = read_vertexes(filename)
    return create_graph(vertexes_)


def read_matrix(filename):
    with open(filename) as file:
        return list(map(lambda l: [int(v) for v in l.split(', ')], file.readlines()))


if __name__ == '__main__':
    graph = read_matrix('Taxicab_64_matrix.txt')
    matrix_to_edge_list(graph)
    # print(graph)

