func looper(int value){
    while( value > 0){
        counter = counter -1
    }
}


func main(){
    var int step = 0 
    while(step < 100){
        looper(step)
        step = step + 10
    }
}
