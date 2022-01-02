# resolve variables and create an infinte register machines 

class Register:
    def __init__(self,name,num,parent):
        self.name = name
        self.num = num
        self.parent = parent
    
    def __repr__(self):
        return self.name

class Resolver:
    
    def __init__(self):
        self.counts = {}
        self.registers = {}

    def name(self,name='temp'):
        if name not in self.counts:
            count = self.counts[name] = 1
            
        else:
            count = self.counts[name] 
        new_name = name
        new = Register(new_name,count,self)
        self.registers[new_name] = name
        return new         
        
    def new(self,name='temp'):
        if name not in self.counts:
            count = self.counts[name] = 1
            
        else:
            count = self.counts[name] 
        new_name = name +'_'+ str(count)
        new = Register(new_name,count,self)
        self.counts[name] += 1
        self.registers[new_name] = name
        return new         

class Label:
    "Label for assembler"
    "need to retarget for boneless at some point " 
    pass

class Labels:
    "Make local sets of labels"
    _post_counter = 0 
    def __init__(self):
        self._postfix = "_{:04X}".format(Labels._post_counter)
        self._names = {}
        Labels._post_counter += 1
    
    def set(self,value):
        self._names[value] = value + self._postfix
        return self._names[value]

    def __getattr__(self, key):
        if key in self._names:
            return self._names[key]
        # for forward declarations
        self._names[key] = key + self._postfix
        setattr(self, key, key + self._postfix)
        return self._names[key]
    
        
