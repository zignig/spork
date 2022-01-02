# The base object for all the compiler objects


# An upwards searching symbol table
# Used all the way through the compiler

_DEBUG = False 
class SymbolTable:
    debug = False
    def __init__(self, parent=None, name="anon"):
        if _DEBUG:
            print("Create table %s" % name)
        self.symbols = {}
        # for nested tables
        self.children = []
        self.parent = parent
        self.name = name
        self._empty = True
        if self.parent is not None:
            if isinstance(parent, SymbolTable):
                parent.children.append(self)
            else:
                raise BaseException("Not a symbol table")

    def add(self, name, value):
        self._empty = False
        if _DEBUG:
            print("adding -> ", name, value, " to ", self.name)
        if name in self.symbols:
            print(self)
            raise BaseException("symbol already exists %s" % name)
        self.symbols[name] = value

    def get(self, name):
        if self.debug:
            print("?", name, ">", self.name,end='')
        if name in self.symbols:
            if self.debug:
                print("... found ", name, " in ", self.name)
            return self.symbols[name]
        # search up the scopes
        if self.parent is not None:
            if self.debug:
                print(" ->", self.parent.name,end='')
            return self.parent.get(name)
        # no symbol at this point
        print(">", name, "< not found in")
        print(self)
        raise BaseException("no symbol found >%s<" % name)

    def __repr__(self):
        lines = []
        lines.append("Symbol Table for %s" % (self.name))
        if self.parent is not None:
            lines.append("%s >> %s" % (self.parent.name, self.name))
        else:
            lines.append(self.name)
        for key, value in self.symbols.items():
            lines.append("|%12s|: %20r |" % (key, value))
        lines.append("\n")
        if len(self.children) > 0:
            for i in self.children:
                if not i._empty:
                    lines.append(i.__repr__())
                else:
                    lines.append("Empty table "+i.name)
        s = "\n".join(lines)
        return s


class Base:
    name = "anon"
    _symbols = SymbolTable(name="global")
    _current = _symbols

    def __init__(self,meta, tree):
        self.meta = meta
        self.body = tree


    def add_sym(self,name,value):
        Base._current.add(name,value)
        self.local_symbols = Base._current

    def add_namespace(self,name):
        Base._current = SymbolTable(Base._current,name)
        self.local_symbols = Base._current
    
    def pop_namespace(self):
        Base._current = Base._current.parent

    def detail(self):
        " print detailed information " 
        base = (
            ""
            + str(self.__class__.__qualname__) 
            + '\n Name:'
            + str(self.name)
            + "\n"
        )
        for i in dir(self):
            if i.startswith('_') == False:
                base += (i+' : '+str(getattr(self,i))+'\n')
        base += (str(self.meta.line)+','+str(self.meta.column)+'\n')
        print(base)


    def __repr__(self):
        base = (
            # str(type(self))
            # + "-"
            "("
            + str(self.__class__.__qualname__)
            + " - "
            + str(self.name)
            + ")"
        )
        if hasattr(self, "params"):
            base += " "
            base += str(self.params)
        if hasattr(self, "vtype"):
            base += " |> "
            base += str(self.vtype)
        return base

    def _indent(self, level, val):
        if self.body is not None:
            for i, j in enumerate(self.body):
                print(level * "\t", i, j)
                level += 1
                j._indent(level, j)
                level -= 1
