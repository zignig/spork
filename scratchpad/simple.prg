enum state { init,start,run,stop,error }
var int a
var int b
struct test{
	var int a
	var string name
}

func bigger(a,b){
    if(a>b){
        return a
    } else {
        return b
    }
    var int c
    c = ( a + b ) /2
    return c
}

func add(a,b){
	var int result 
        result = a + b
        result = bigger(a,b)
	return result 
}
