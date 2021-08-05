// sieve of erath 


func sieve(){
    var int[128] values
    var int counter = 0 
    var int num = 0 
    var int pos = 0 
    while ( counter < 128 ){
        while ( pos < 128 ){
           nums[pos] = 1
           pos = pos + counter 
        }
        pos = counter
        counter = counter + 1
    }
}

func main(){
    sieve()
}
