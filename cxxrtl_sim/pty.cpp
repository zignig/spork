#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <cstdio>
#include <pty.h>
#include <termios.h>

#define BUF_SIZE (256)

int main(int, char const *[])
{
    int master, slave;
    char buf[BUF_SIZE];
    struct termios tty;
    tty.c_iflag = (tcflag_t) 0;
    tty.c_lflag = (tcflag_t) 0;
    tty.c_cflag = CS8;
    tty.c_oflag = (tcflag_t) 0;

    auto e = openpty(&master, &slave, buf, &tty, nullptr);
    if(0 > e) {
    std::printf("Error: %s\n", strerror(errno));
        return -1;
    }

    int r;
    std::printf("Slave PTY: %s\n", buf);


    while ( (r = read(master, buf, BUF_SIZE)) > 0 )
    {
        write(master, buf, r);
        std::printf("hello %d",r); 
    }

    close(slave);
    close(master);

    return 0;
}
