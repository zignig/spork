class BaseStruct:
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._size = 1


class Pointer(BaseStruct):
    pass


class Int16(BaseStruct):
    pass
