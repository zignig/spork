// fib program 


func test(int a){
    a = a +1
    return a
}

func test2(int a , int b){
}

func main() { 
    var int x = 0 
    var int y = 1
    var int z
    while(1){
        x = 0
        y = 1 
        while( z < 65536 ){
            x = y 
            y = z
            z = x + y
            print(z)
        }
    }
}

main()
