// stack 

var ptr[20] stack
var int pos = 0 

func pop(){
    var ptr value
    value = ptr[pos]
    pos = pos -1 
    return value
}

func push(ptr value){
    pos = pos + 1 
    ptr[pos] = value
}
