# all the named objects
# functions , vars , task , 'n stuff

# TODO frobulate all the names

from .base import Base


class Named(Base):
    def __init__(self, name):
        self.name = name
