# radix tree

# references
# https://db.in.tum.dw/~leis/papers/ART.pdf
# https://en.wikipedia.org/wiki/Radix_tree


class Node:
    def __init__(self):
        self.children = {}
        self.terminal = False

    def add(self, name):
        n = Node()
        self.children[name] = n
        return n

    def insert(self, name):
        for i, j in self.children.items():
            if i.startswith(name):
                print("new prefix ", i)
                insert = self.children[i]
                del self.children[i]
                below = self.add(name)
                below.add(i[len(name) :])
                return

            if name.startswith(i):
                print(i, name, name[len(i) :])
                postfix = name[len(i) :]
                j.insert(postfix)
                return

        self.add(name)

    def show(self, depth=0):
        for i, j in self.children.items():
            indent = "".join("  " for _ in range(depth))
            print(indent, i)
            j.show(depth + 1)


class RTree:
    def __init__(self):
        self.root = Node()

    def add(self, name):
        print(name)

    def show(self):
        self.root.show()


if __name__ == "__main__":
    r = RTree()
    n = Node()
    n.add("asdf")
    n.add("wer")
