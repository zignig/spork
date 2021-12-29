// fib program 

func fib(int count) { 
    var int x = 0 
    var int y = 1
    var int z
    while(x < count){
        x = y 
        y = z
        z = x + y
        print(z)
    }
}

func main(){
    fib(10)
    fib(20)
}
