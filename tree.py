import dataclasses

import print_utils
from distance_matrix import DistanceMatrix


def edge_to_str(edge):
    if edge[0] < edge[1]:
        return str(edge[0]) + " " + str(edge[1])
    else:
        return str(edge[1]) + " " + str(edge[0])


INF = 999999999


@dataclasses.dataclass
class Tree:
    n: int
    nodes: set = dataclasses.field(default_factory=set)
    edges: set = dataclasses.field(default_factory=set)

    @property
    def weight(self):
        return sum(edge[2] for edge in self.edges)

    @property
    def adj_matrix(self):
        matrix = [[0] * self.n for _ in range(self.n)]
        for it in self.edges:
            r, c, v = it
            matrix[r][c] = v
            matrix[c][r] = v
        return matrix

    def __repr__(self):
        return f'Tree(nodes={sorted(self.nodes)}, edges={sorted([f"{edge_to_str(edge)} {edge[2]}" for edge in self.edges])})'

    @property
    def distance_matrix(self):
        return DistanceMatrix(self.adj_matrix)

    @property
    def diameter(self):
        return max(map(max, self.distance_matrix.distance_matrix))

    def remove_edge(self, edge):
        adj_matrix = self.adj_matrix
        for e in self.edges:
            if e[0] == edge[0] and e[1] == edge[1] or e[0] == edge[1] and e[1] == edge[0]:
                self.edges.remove(e)
                adj_matrix[e[0]][e[1]] = 0
                adj_matrix[e[1]][e[0]] = 0
                break
        for i, row in enumerate(adj_matrix):
            if sum(row) == 0:
                self.nodes.remove(i)
