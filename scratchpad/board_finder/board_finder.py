# select a board from the following list",

import os, importlib


from ..logger import logger

log = logger(__name__)


# Board listings
def extract_boards():
    "get a list of all the nmigen_boards"

    global _boards_built, _boards

    if _boards_built:
        return _boards

    import nmigen_boards

    path = nmigen_boards.__path__[0]
    file_list = os.listdir(path)
    board_files = []
    # get a list of the the board files
    for name in file_list:
        if name.endswith(".py"):
            short_name = name.split(".")[0]
            if short_name != "__init__":
                log.debug("Found board %s", name)
                board_files.append(short_name)

    name_dict = {}
    # get the platform names
    for f in board_files:
        board = importlib.import_module(nmigen_boards.__package__ + "." + f)
        platform = board.__all__[0]
        class_name = board.__dict__[platform]
        name_dict[f] = (class_name, platform)

    _boards = name_dict
    _boards_built = True
    return name_dict


def get_board(name):
    " get board by name"
    boards = extract_boards()
    if name in boards:
        return (name, boards[name])


def board_info(board):
    "get board information for templating"
    # Board name
    name = board[0]
    # Create an instance
    module = board[1][0].__module__
    return {
        "name": name,
        "module": module,
        "class_name": board[1][1],
        "cls": board[1][0],
    }


def short_list():
    " return a list of the board names"
    boards = extract_boards()
    return list(boards.keys())


def show_list():
    print("Available Boards")
    print()
    for num, board in enumerate(short_list()):
        print("{:>4}  {}".format(num, board))
    print()


# Interactive


def select_board():
    " select one board from all available boards"
    boards = short_list()
    val = select_from_list(boards, name="Boards")
    board = check_board(val)
    return board


def check_board(name):
    boards = extract_boards()
    info = None
    if name in boards:
        info = board_info(get_board(name))
    else:
        boards = short_list()
        for num, board in enumerate(boards):
            print("{:>4}  {}".format(num, board))
        print("\nBoard does not exist\n")

    return info
