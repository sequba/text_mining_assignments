class UnionFind:
    parent = None
    rank = None

    def __init__(self):
        self.parent = dict()
        self.rank = dict()

    def make_set(self, x):
        self.parent[x] = x
        self.rank[x]   = 0

    def union(self, x, y):
        xRoot = self.find(x)
        yRoot = self.find(y)
        if self.rank[xRoot] > self.rank[yRoot]:
            self.parent[yRoot] = xRoot
        elif self.rank[xRoot] < self.rank[yRoot]:
            self.parent[xRoot] = yRoot
        elif xRoot != yRoot: # Unless x and y are already in same set, merge them
            self.parent[yRoot] = xRoot
            self.rank[xRoot] += 1

    def find(self, x):
        if self.parent[x] == x:
            return x
        else:
            self.parent[x] = self.find(self.parent[x])
            return self.parent[x]

