
func comp_test(int a,int b ){
    if( a < b){}
    if( a > b){}
    if( a >= b){}
    if( a <= b){}
    if( a == b){}
    if( a != b){}
}
// recursion test 
func down(int depth){
   if(depth > 0){
        depth = depth -1
        down()
   }
   return 0
}

func el_test(){
    var int a
    if( a == 2){
        print("hello")
    }else{
        print("bork")
    }
}

func test(int count,int a,int b,ptr c,string d){}
func main(){
    down(5)
    var int counter 
    var int limit = 100
    while( counter < limit){
        var int a
        var int b
        var int c
        var int d = 100
        counter = counter + 1
        if(counter % 5 == 0){
            test(4,a,b,c,d)
        }
    }
}
