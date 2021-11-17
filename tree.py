import dataclasses

from collections import deque
import numpy as np


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
    edges: list = dataclasses.field(default_factory=list)

    def __post_init__(self):
        self.adj_matrix = [[0] * self.n for _ in range(self.n)]
        self.adj_list = [set() for _ in range(self.n)]

    @property
    def weight(self):
        return sum(edge[2] for edge in self.edges)

    def add_edge(self, edge: tuple):
        self.adj_matrix[edge[0]][edge[1]] = edge[2]
        self.adj_matrix[edge[1]][edge[0]] = edge[2]
        self.edges.append(edge)
        self.adj_list[edge[0]].add(edge[1])
        self.adj_list[edge[1]].add(edge[0])

    def remove_edge(self, edge: tuple):
        self.adj_matrix[edge[0]][edge[1]] = 0
        self.adj_matrix[edge[1]][edge[0]] = 0
        self.edges.remove(edge)
        self.adj_list[edge[0]].remove(edge[1])
        self.adj_list[edge[1]].remove(edge[0])

    def remove_edge_by_index(self, index: int):
        edge = self.edges[index]
        self.remove_edge(edge)

    # @property
    # def adj_matrix(self):
    #     matrix = [[0] * self.n for _ in range(self.n)]
    #     for it in self.edges:
    #         r, c, v = it
    #         matrix[r][c] = v
    #         matrix[c][r] = v
    #     return matrix

    def __repr__(self):
        return f'Tree(nodes={sorted(self.nodes)}, edges={sorted([f"{edge_to_str(edge)} {edge[2]}" for edge in self.edges])})'

    @property
    def diameter(self):
        # tree = self.adj_matrix
        # from_node = to_node = 0
        start_node = self.edges[0][0]
        dist = self._bfs(self.n, start_node)

        # dist = self._bfs(tree, self.n, start_node)

        # for i, value in enumerate(dist):
        #     if dist[i] > dist[from_node]:
        #         from_node = i
        from_node = np.argmax(dist)

        dist = self._bfs(self.n, from_node)
        # dist = self._bfs(tree, self.n, start_node)

        # for i, value in enumerate(dist):
        #     if dist[i] > dist[to_node]:
        #         to_node = i
        to_node = np.argmax(dist)
        return from_node, to_node, dist[to_node]

    def _bfs(self, n, node):
        dist = [0 for i in range(n)]
        queue = deque()
        visited = {node}
        queue.append(node)
        while queue:
            s = queue.popleft()
            for neighbor in self.adj_list[s]:
                if neighbor not in visited:
                    dist[neighbor] = dist[s] + 1
                    visited.add(neighbor)
                    queue.append(neighbor)
        return dist


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

