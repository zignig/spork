//enum state { init,start,run,stop,error }

//task bob{}

var int test

func add( int a , int b){
    var int c 
    c = a + b
    return c
}

func loop(int counter){
    var int count = 0 
    while(counter != count){
        count = count +1
        print(count)
    }
}



func setup(){}
func main(){
    var int value 
    value = add(1,3)
    loop(1000)
    loop(50)
}
