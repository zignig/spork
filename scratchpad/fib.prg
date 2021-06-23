// fib program 


func main() { 
    var int x = 0 
    var int y = 1
    var int z
    while(True){
        x = 0
        y = 1 
        while( z < 255 ){
            x = y 
            y = z
            z = x + y
            print(z)
        }
    }
}

main()
