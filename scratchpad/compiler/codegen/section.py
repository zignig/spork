# These are the code snippets for building a program
# this is platform specific, grab the code from lib and convert
__all__ = [
    "Rem",
    "program_prelude",
    "program_epilog",
    "function_prelude",
    "function_epilog",
]


class Rem:
    " for adding remarks in code "

    def __init__(self, val):
        self.val = val

    def __call__(self, m):
        return []

    def __repr__(self):
        return 'Rem("' + str(self.val) + '")'


def program_prelude():
    return Rem("Program Prelude")


def program_epilog():
    return Rem("Program Epilog")


def function_prelude():
    return Rem("Function Prelude")


def function_epilog():
    return Rem("Function Epilog")
