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
    print("Up to 10")
    fib(10)
    print("Up to 20")
    fib(20)
}
