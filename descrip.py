# this is test for python descriptors

# https://docs.python.org/3/howto/descriptor.html#descriptor-howto-guide


class Base:
    def __set_name__(self, owner, name):
        print(self, owner, name)
        owner._insert(owner, name, self)
        self._private_name = "_" + name

    def __get__(self, obj, objtype=None):
        return getattr(obj, self._private_name)

    def __set__(self, obj, value):
        setattr(obj, self._private_name, value)


class Periph(Base):
    pass


class Upper:
    def __set_name__(self, owner, name):
        print(self, owner, name)
        owner._insert(owner, name, self)
        self._private_name = "_" + name

    def _insert(self, name, base):
        if not hasattr(self, "_sub"):
            setattr(self, "_sub", {})
        self._sub[name] = base

    def _list(self):
        for i in self._sub.items():
            print(i)


class thing(Upper):
    test = Base()
    stuff = Base()


class UART(Upper):
    three = Base()


class tester(Upper):
    bob = Periph()
    bob2 = Periph()
    timer = Periph()
    checksum = Periph()
    warmboot = Periph()
    u = UART()


u = Upper()
b = thing()
t = tester()
