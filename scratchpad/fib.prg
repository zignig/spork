// fib program 


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
