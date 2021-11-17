import dataclasses

from collections import deque


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
    def diameter(self):
        tree = self.adj_matrix
        # TODO подкумать как использовать только рёбра
        from_node = to_node = 0
        start_node = self.edges[0][0]
        dist = self._bfs(tree, self.n, start_node)
        for i, value in enumerate(dist):
            if dist[i] > dist[from_node]:
                from_node = i
        dist = self._bfs(tree, self.n, from_node)
        for i, value in enumerate(dist):
            if dist[i] > dist[to_node]:
                to_node = i
        return from_node, to_node, dist[to_node]

    def _bfs(self, graph, n, node):
        dist = [0 for i in range(n)]
        queue = deque()
        visited = set()
        visited.add(node)
        queue.append(node)
        while queue:
            s = queue.popleft()
            for neighbor_i, neighbor_dist in enumerate(graph[s]):
                if neighbor_dist != 0 and neighbor_i not in visited:
                    dist[neighbor_i] = dist[s] + 1
                    visited.add(neighbor_i)
                    queue.append(neighbor_i)
        return dist

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
