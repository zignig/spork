// sieve of erath 
const int length = 128

func sieve(){
    var int[length] values
    var int counter = 0 
    var int num = 0 
    var int pos = 0 
    while ( counter < length ){
        while ( pos < length ){
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
