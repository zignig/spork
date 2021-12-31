# Base types as python objects
# used for type checking and allocation

class BaseVType:
    _size = 1
    pass

class Vint(BaseVType):
    name = 'int'
    pass

class Vuint(BaseVType):
    name = 'uint'
    pass

class Vchar(BaseVType):
    name = 'char'
    pass

class Vbool(BaseVType):
    name = 'bool'
    pass


class Vstring(BaseVType):
    name = 'string'
    pass

class Vpointer(BaseVType):
    name = 'ptr'
    pass

type_list = [Vint,Vuint,Vchar,Vbool,Vstring,Vpointer]

__all__ = [i.__name__ for i in type_list] + ['type_list']

