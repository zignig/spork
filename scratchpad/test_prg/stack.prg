// stack 

var int[20] stack
var int pos = 0 

func pop(){
    var int value = stack[pos]
    pos = pos -1 
    return value
}

func push(int value){
    pos = pos + 1 
    stack[pos] = value
}
