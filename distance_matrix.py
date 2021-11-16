
INF = 999999999


class DistanceMatrix:
    def __init__(self, adj_matrix):
        self.n = len(adj_matrix)
        self.distance_matrix = list(map(list, adj_matrix))
        self.path_matrix = [[None for i in range(self.n)] for j in range(self.n)]
        self._create_distance_matrix()
        self.diameter = max(map(max, self.distance_matrix))
        self.diameter_path = self._diameter_path()
        self.diameter_path_in_edges = len(self.diameter_path)

    def _create_distance_matrix(self):
        for i in range(self.n):
            for j in range(self.n):
                if i != j and self.distance_matrix[i][j] != 0:
                    self.path_matrix[i][j] = j
                if i == j:
                    self.path_matrix[i][j] = i
                if i != j and self.distance_matrix[i][j] == 0:
                    self.distance_matrix[i][j] = INF
                # if distance_matrix[i][j] == 0:
                #     distance_matrix[i][j] = INF
        for k in range(self.n):
            for i in range(self.n):
                for j in range(self.n):
                    if self.distance_matrix[i][k] + self.distance_matrix[k][j] < self.distance_matrix[i][j]:
                        self.distance_matrix[i][j] = self.distance_matrix[i][k] + self.distance_matrix[k][j]
                        self.path_matrix[i][j] = self.path_matrix[i][k]
        for i in range(self.n):
            for j in range(self.n):
                if i != j and self.distance_matrix[i][j] == INF:
                    self.distance_matrix[i][j] = 0
        # a = [[0 for i in range(self.n)] for j in range(self.n)]
        # for i in range(self.n):
        #     for j in range(i, self.n):
        #         a[i][j] = len(self.path(i, j))

    def path(self, from_node, to_node) -> list:
        if self.path_matrix[from_node][to_node] is None:
            return []
        p = [from_node]
        while from_node != to_node:
            from_node = self.path_matrix[from_node][to_node]
            p.append(from_node)
        return p

    def _diameter_path(self) -> list:
        for i, row in enumerate(self.distance_matrix):
            if self.diameter in row:
                return self.path(i, row.index(self.diameter))
