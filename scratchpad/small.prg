func die(){}

func looper(int value){
    while( value > 0){
        counter = counter -1
    }
    if ( value < 100){
        die()
    }
    while(value > 100){
        value = 1000
    }
}


func main(){
    var int step = 0 
    while(step < 100){
        looper(step)
        step = step + 10
    }
}
