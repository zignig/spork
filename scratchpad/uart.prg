use hardware 

var char[32] buffer
var int pos = 0 

struct string{
    var int length 
    var char[] data
}

func has_char(){
    if (hardware.uart.rx_ready == 1){
       char[pos] = hardware.uart.rx
       pos = pos + 1
    }
}

func write_string(string s){
    var int len
    var int pos = 0 
    len = s.length
    while(pos <= len){
        write(s.char[pos])
        pos = pos + 1 
    }
}

func write(char val){
    while(hardware.uart.tx_ready != 0){}
    // write to uart 
    hardware.uart.tx = val
}
