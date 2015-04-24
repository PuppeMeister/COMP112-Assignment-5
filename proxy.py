# Jim Mao and Max Cohen
# Comp112: Networks
# Assigment 5: HTTP Proxy
# April 7, 2015


import os,sys,thread,socket,calendar,time

#********* CONSTANT VARIABLES *********
BACKLOG = 50            # how many pending connections queue will hold
MAX_DATA_RECV = 999999  # max number of bytes we receive at once
DEBUG = True            # set to True to see the debug msgs
BLOCKED = []            # [] for no blocking at all.
CACHE_SIZE = 20         # maximum number of files that can be stored in the cache

#**************************************
#********* MAIN PROGRAM ***************
#**************************************
def main():

    # check the length of command running
    if (len(sys.argv) < 2):
        print "No port given, using :8080 (http-alt)" 
        port = 8080
    else:
        port = int(sys.argv[1]) # port from argument

    # host and port info.
    host = ''               # blank for localhost
    
    print "Proxy Server Running on ",host,":",port

    try:
        # create a socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # associate the socket to host and port
        s.bind((host, port))

        # listening
        s.listen(BACKLOG)
    
    except socket.error, (value, message):
        if s:
            s.close()
        print "Could not open socket:", message
        sys.exit(1)

    # get the connection from client
    while 1:
        conn, client_addr = s.accept()

        # create a thread to handle request
        thread.start_new_thread(proxy_thread, (conn, client_addr))
        
    s.close()
#************** END MAIN PROGRAM ***************

def printout(type, request, address):
    if "Block" in type or "Blacklist" in type:
        colornum = 91
    elif "Request" in type:
        colornum = 92
    elif "Reset" in type:
        colornum = 93

    print address[0],"\t",type,"\t",request


cache = [""] * CACHE_SIZE
num_cache_entries = 0
#*******************************************
#********* PROXY_THREAD FUNC ***************
# A thread to handle request from browser
#*******************************************
def proxy_thread(conn, client_addr):
    # Dealing with global/local variable and threading issues here....Jim help
    global cache 
    global num_cache_entries

    # get the request from browser
    request = conn.recv(MAX_DATA_RECV)
    # print request

    first_line = request.split('\n')[0]     # parse the first line

    if first_line != '':    # only get the requested url if it exists
        url = first_line.split(' ')[1]    # get url
    else:
        return 

    # check if url is blocked
    for i in range(0, len(BLOCKED)):
        if BLOCKED[i] in url:
            printout("Blacklisted", first_line, client_addr)
            conn.close()
            sys.exit(1)

    printout("Request", first_line, client_addr)

    
    # find the webserver and port
    http_pos = url.find("://")          # find pos of ://
    if (http_pos == -1):
        temp = url
    else:
        temp = url[(http_pos + 3):]       # get the rest of url
    
    port_pos = temp.find(":")           # find the port pos (if any)

    # find end of web server
    webserver_pos = temp.find("/")
    if webserver_pos == -1:
        webserver_pos = len(temp)

    webserver = ""
    port = -1
    if (port_pos == -1 or webserver_pos < port_pos):      # default port
        port = 80
        webserver = temp[:webserver_pos] # webserver is the name of the server from which the client requested data
        #print webserver
    else:       # specific port
        port = int((temp[(port_pos + 1):])[:webserver_pos - port_pos - 1])
        webserver = temp[:port_pos]
        #print webserver

    try:
        cur_time = calendar.timegm(time.gmtime())
        getData = False

        # removing illegal characters from file name
        url_file_name = url.replace("http://", "").replace("HTTP://", "").replace("/", "").replace("?", "").replace("\\", "").replace(":", "").replace("*", "").replace("\"", "").replace("<", "").replace(">", "").replace("|", "")
        url_file_name = url_file_name[0:255]    # maxmimum file name length is 255

        if os.path.isfile(url_file_name):   # cache file exists
            cache_file = open(url_file_name, "r")
            cache_file_time = float(cache_file.readline()) # read the first line of the cache file which is the time the cache entry was created
            #print "cur_time: %d" % (cur_time)
            #print "cache_file_time: %d" % (cache_file_time)
            #print "cur_time - cache_file_time: %d" % (cur_time - cache_file_time)

            if cur_time - cache_file_time > 86400: # if the cache file is older than one day (86400 seconds in day), refresh it
                cache_file = open(url_file_name, "w+") # erase the current contents of the cache file for webserver
                cache_file.write(repr(cur_time))   # update the current timestamp of the cache file
                cache_file.write('\n')
                getData = True
        else:   # cache file does not exist, create it
            lru_file = cache[num_cache_entries] 

            if os.path.isfile(lru_file):    # rm the least recently used file from the cache
                #print "lru_file: %s" % lru_file
                os.remove(lru_file)

            cache[num_cache_entries] = url_file_name    # insert the new file into the cache, replacing the old one if the cache is at its capacity

            num_cache_entries = (num_cache_entries + 1) % CACHE_SIZE    # increment the place to add the new cache entry in the circular array

            cache_file = open(url_file_name, "w+") # erase the current contents of the cache file for webserver
            cache_file.write(repr(cur_time))   # update the current timestamp of the cache file
            cache_file.write('\n')
            getData = True

        if getData: # if the cache file data is expired
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # create a socket to connect to the web server
            s.connect((webserver, port))
            s.send(request)     # send request to webserver

            while 1:
                # receive data from web server
                data = s.recv(MAX_DATA_RECV) # Max - Change to recvfrom to also get the address from which data is receive - When implementing multiple clients
                               
                if (len(data) > 0):
                    cache_file = open(url_file_name, "a+") # Update the cache with new version of file from webserver
                    cache_file.write(data)
                    cache_file.close()
                    # send to browser
                    conn.send(data) # Max - Change to sendto to specify the address to send the data to - When implementing multiple clients
                else:
                    break
            s.close()
        else:
            timestamp = cache_file.readline() # move the file pointer past the timestamp line
            data = cache_file.read() # read data from the cache file
            conn.send(data)
        conn.close()
    except socket.error, (value, message):
        if s:
            s.close()
        if conn:
            conn.close()
        printout("Peer Reset", first_line, client_addr)
        sys.exit(1)

#********** END PROXY_THREAD ***********

def count_files_in_directory(dir):
    return len([name for name in os.listdir(dir) if os.path.isfile(name)])
    
if __name__ == '__main__':
    main()
