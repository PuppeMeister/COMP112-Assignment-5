import socket

#********* CONSTANT VARIABLES *********
backlog = 50            # how many pending connections queue will hold
max_data_recv = 999999  # max number of bytes we receive at once
debug = True            # set to True to see the debug msgs
blocked = ["www.cs.tufts.edu", "www.python.org"]            # [] for no blocking at all.
ip_blocked = [socket.gethostbyname(host) for host in blocked]
cache_size = 10         # maximum number of files that can be stored in the cache