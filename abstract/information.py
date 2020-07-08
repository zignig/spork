import inspect, ast


class reg:
    pass


class base:
    def __init__(self):
        a = reg()
        b = reg()


if __name__ == "__main__":
    r = base()
    ast.dump(r)
