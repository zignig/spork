var string[10] other

func add(int a,int b){
  var int c
  c = a+b
    return c
}


struct vec { 
	var int x
	var int y
}

impl vec.add(vec v1){
    vec.x = vec.x + v1.x
    vec.y = vec.y + v1.y
}

struct robot {
	var string name
	var vec pos
	var vec velocity 
	var vec[10] path
}

func addvec(vec v1,vec v2){
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

