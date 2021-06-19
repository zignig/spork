// test program 

use uart

var int a = 1
var int gr = 400
var int r = 200
var int test

struct vector {
	var int x
	var int y
}

struct tensor {
	var string name
	var vector a
	var vector b
}

struct item { 
	var string name
	var int value
}

struct menu {
	var item[10] test
	var item test2
}

var tensor bob2
var vector v1
var vector v2

func asdf(int a, int b,int c){
	var int bob 
	var int test
	var menu m
	func gorf(){}
}

func add(int a,int b){
	return a+b
}

func plus2(int a){
	return a+2 
}

func wait(int count){
	var int counter 
	var bool exit = false
	while(exit == false){
		counter = counter + 1
		if(counter==count){
			 exit = True 
		}
	}
}

func hello(){
	print("hello")
}

task blink {
	var item fnord
	var int counter = 0 
	counter = counter + 1
	hello()
	wait(100)
}

task monitor {
}

task build {
    func aa(){}
    while(bob == true){}
}

func  norg(){
	var int hello
	var int counter
	hello = 5
	counter = counter + 1	
        var int r 
        var int j
	if(counter==100){
		asdf()
		wait(100)
	}
	r = 2 * ( 4 + a * 0.5 ) 
        j = ((a*a)+(b*b))*((a*a)+(b*b))
        r = a + b + ( c * d )
}

