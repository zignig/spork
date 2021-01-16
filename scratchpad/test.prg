var int a
var int b 
var string[10] other
func add(a,b){
  c = a+b
}


struct vec { 
	var int x
	var int y
}

struct robot {
	var string name
	var vec pos
	var vec velocity 
	var vec[10] path
}

func addvec(v1,v2){
	var vec v3
	v3.x = v1.x + v2.x
	v3.x = v1.y + v2.y
	return v3
}

on timer {
	var int counter 
	counter =  counter + 1 
}

task bork{
	var bool status = false
	var int counter
	var int limit = 100
	while(status == false){
		couter = counter + 1
		if( counter > limit){
			status = true
		}		
	}
	counter = 0
}

