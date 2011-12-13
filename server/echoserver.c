#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <strings.h>
#include <arpa/inet.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <libvirt/libvirt.h>


#define LISTEN_QUEUE_LENGTH 8
#define BUFFER_SIZE 1024

struct sockaddr *address;
struct socklen_t *address_len;


// read at most max_len into buf (null terminated)
// buf should be a memory allocation of size >= max_len
// terminate at first occurrence of \r or \n
ssize_t readline(int fd, char *buf, size_t max_len)
{
  char c, *p;
  
  for (p = buf, c = 0;  p < buf + max_len - 1 && c != '\n';) {
    switch (read(fd, &c, 1)) {
    case 1:  /* read a byte */
        if(c == '\n' || c == '\r')
            goto finish;
        *p++ = c;
        break;
    case 0:  /* read EOF    */
        goto finish;
        break;
    case -1: /* error       */
      if (errno == EINTR) {
	continue;
      } else {
	perror("read");
	return -1;
      }
      break;
    }
  }
finish:
  *p = 0;
  return p - buf;
}

//write the line out to the users
ssize_t writeline(int fd, const char *buf, size_t len)
{
  size_t written, total_written;
  const char *p;
  
  for (written = total_written = 0, p = buf; total_written < len; p += written, total_written += written) {
    if ((written = write(fd, buf, len - written)) <= 0) {
      return total_written;
    }
  }
  
  return total_written;
}

int main(int argc, char *argv[])
{

  virConnectPtr conn;

  conn = virConnectOpen("qemu:///system");
  if (conn == NULL) {
    fprintf(stderr, "Failed to open connection to qemu:///system\n");
    return 1;
  }

  //file descriptors
  int listenfd;
  int acceptfd;
  
  //the adress of the server and the client (singular)
  struct sockaddr_in server_addr;
  struct sockaddr_in client_addr;
  socklen_t client_addr_len;
  
  //buffer for the message being sent
  char buffer[BUFFER_SIZE];
  //size of blocks that can be read or written, no idea
  ssize_t length;
  
  //if you do not have a port
  if (argc != 2) {
    fprintf(stderr, "Usage: %s <port>\n", argv[0]);
    return -1;
  }
  
  //if the socket is already being used
  //upon success it sets the listenfd to the socket to listen to
  if ((listenfd = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
    perror("socket");
    
    return -1;
  }
  
  //zeroing out our server address
  bzero(&server_addr, sizeof (server_addr));
  
  //setting up the server struct
  //ipv4
  server_addr.sin_family = AF_INET;
  //host to network short aka putting 7700 in there
  server_addr.sin_port = htons(atoi(argv[1]));
  //local ip address
  server_addr.sin_addr.s_addr = INADDR_ANY;
  
  //binds the socket given to the address of the server
  if (bind(listenfd, (struct sockaddr *) &server_addr, sizeof (server_addr))) {
    perror("bind");
    return -1;
  }
  
  //set the wait queue for pending to 8 people
  if (listen(listenfd, LISTEN_QUEUE_LENGTH)) {
    perror("listen");
    return -1;
  }
  
  //infinite loop that listens to connections and messages
  fd_set fds;
  fd_set ret;
  FD_ZERO(&fds);
  FD_ZERO(&ret);
  FD_SET(listenfd,&ret);
  int i;
  for (;;) {
    fds = ret;
    int rc = select(FD_SETSIZE, &fds, NULL, NULL, NULL);
    if (rc==-1) {
      perror("select failed");
      return -1;
    }
    for(i = 0; i < FD_SETSIZE; ++i){
      //if each i is in the set returned
      if(FD_ISSET(i,&fds)){
	//if i was equal to listenfd, new connection
	if(i == listenfd){
	  //address of a single client
	  client_addr_len = sizeof (client_addr);
	  //set the accept fd to listen to the connection from the given address
	  int acceptfd;
	  if ((acceptfd = accept(listenfd, (struct sockaddr *) &client_addr, &client_addr_len)) == -1) {
	    perror("accept");
	    return -1;
	  }
	  FD_SET(acceptfd,&ret);
	  fprintf(stderr, "Connection Made\n");
	  fprintf(stderr, "acceptfd: %d\n", acceptfd);
	  fprintf(stderr, "client_addr_len: %d\n", client_addr_len);
	  //should be the file descriptor
	  fprintf(stderr, "i: %d\n\n", i);
	  fprintf(stderr, "client_addr.sin_port: %d\n", ntohs(client_addr.sin_port));
	  char str[INET_ADDRSTRLEN];
	  inet_ntop(AF_INET, &(client_addr.sin_addr), str, INET_ADDRSTRLEN);
	  fprintf(stderr,"s_addr: %s\n", str);
	} else{
	  //message came in
	  fprintf(stderr, "Message Received\n");
	  length = readline(i, buffer, BUFFER_SIZE);
	  //if there actually is a message				
	  if(length != 0){
             fprintf(stderr, "got: %s\n", buffer);
            
	    //this will eventually be received as a key from the guest OS
	    //i.e. take buffer, lookup in a table from keys to UUIDS (EG below)
            //char* termStr = strchr(buffer, '\r');
	    virDomainPtr dom;
            
	    dom = virDomainLookupByName(conn, buffer);

            unsigned char replUUID[VIR_UUID_BUFLEN];
            virGenerateUUID(replUUID);

	    //take domainName, add delimiter and then counter for number of times it's been forked
	    virDomainLiveSave(dom, "/tmp/vm_1.1",
			      replUUID, "vm_1.1");

            writeline(i, "forked\n", 7);

	    virDomainRestore(conn,"/tmp/vm_1.1");

            //writeline(i,"!\n", 2);

	    /*
	    char *domainUUID = "00311636-7767-71d2-e94a-26e7b8bad250";
	    virDomainPtr dom;

	    dom = virDomainLookupByUUIDString(conn, domainUUID);
	     */


	    /*for(j = listenfd+1; j < FD_SETSIZE; ++j){
	      //need to send message to j
	      if(FD_ISSET(j, &ret)){
		//fprintf(stderr, "Did I loop?")
		if (i != j) writeline(j, buffer, length);
	      }
	      }*/
	  } else {
	    //end the connection
	    fprintf(stderr, "Connection Lost\n");
	    close(i);
	    FD_CLR(i, &ret);
	  }
	}
      }
    }
  }
  virConnectClose(conn);
  return 0;
}
