// fib program 

func main() { 
    var int x = 0 
    var int y = 1
    var int z
    while(x < 2**16){
        x = y 
        y = z
        z = x + y
        print(z)
    }
}

main()
test(1,2,3)
