#fd

fd@ubuntu:~$ ls -al
total 40
drwxr-x---  5 root   fd   4096 Oct 26 03:50 .
drwxr-xr-x 75 root   root 4096 Dec 12 07:37 ..
d---------  2 root   root 4096 Jun 12  2014 .bash_history
-r-sr-x---  1 fd_pwn fd   7322 Jun 11  2014 fd
-rw-r--r--  1 root   root  418 Jun 11  2014 fd.c
-r--r-----  1 fd_pwn root   50 Jun 11  2014 flag
-rw-------  1 root   root  128 Oct 26 03:50 .gdb_history
dr-xr-xr-x  2 root   root 4096 Aug 20  2014 .irssi
drwxr-xr-x  2 root   root 4096 Oct 23 10:38 .pwntools-cache
fd@ubuntu:~$ cd fd.c
-bash: cd: fd.c: Not a directory
fd@ubuntu:~$ cat fd.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
char buf[32];
int main(int argc, char* argv[], char* envp[]){
	if(argc<2){
		printf("pass argv[1] a number\n");
		return 0;
	}
	int fd = atoi( argv[1] ) - 0x1234;
	int len = 0;
	len = read(fd, buf, 32);
	if(!strcmp("LETMEWIN\n", buf)){
		printf("good job :)\n");
		system("/bin/cat flag");
		exit(0);
	}
	printf("learn about Linux file IO\n");
	return 0;

}

fd@ubuntu:~$ ./fd 4660
LETMEWIN
good job :)
mommy! I think I know what a file descriptor is!!
fd@ubuntu:~$ ~
-bash: /home/fd: Is a directory
fd@ubuntu:~$ 
fd@ubuntu:~$ Connection to pwnable.kr closed.
asakuratoshiaki-no-MacBook-Pro:~ Toshiaki$ 
