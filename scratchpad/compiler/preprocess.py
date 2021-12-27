# simple preprocess to find use stanza and preload the text of the library

import os

class Preprocessor:
    def __init__(self,file_data):
        self.file_stack = []
        self.name_stack = []
        self.data_dict= {}
        self.complete_data = ""
        self.data = file_data

    def _get_file(self,file_name):
        try:
            os.stat(file_name+".prg")
        except:
            print(file_name)
            raise Exception("File missing")
        data = open(file_name+".prg").read()
        return data 

 
    def start(self):
        self.scan(self.data)
        while(len(self.name_stack) > 0):
            name = self.name_stack.pop()
            data = self._get_file(name)
            if name not in self.data_dict: 
                print('get file',name)
                self.scan(data)
                self.file_stack.insert(0,name+'.prg')
                self.data_dict[name] = data

    def scan(self,data):
        line = data.split('\n') 
        for i in line:
            if i.find('use') == 0 :
                split_pos=  i.find(' ')
                files = i[split_pos:].split(',') 
                for j in files:
                    self.name_stack.insert(0,j.strip())
                
    def __repr__(self):
        s = 'Preprocessor \n'
        for i in self.name_stack:
            s += '\t' + i +  '\n'
        s += str(self.file_stack)
        return s
        
        

        
