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
    nodes: set = dataclasses.field(default_factory=set)
    edges: list = dataclasses.field(default_factory=list)

    @property
    def weight(self):
        return sum(edge[2] for edge in self.edges)

    @property
    def adj_matrix(self):
        n = len(self.nodes)
        matrix = [[0] * n for _ in range(n)]
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

