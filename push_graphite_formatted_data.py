#!/usr/bin/python

import os
import re
import sys
import time
import socket
import platform
import subprocess
import pickle
import struct
from perfvizutils import print_progress

CARBON_SERVER = os.getenv('CARBON_SERVER', 'perfviz')
CARBON_PICKLE_PORT = os.getenv('CARBON_PICKLE_PORT', 2004)
MAX_BUFFER_SIZE = int( os.getenv('MAX_BUFFER_SIZE', 1000) )
SLEEP_INTERVAL = float( os.getenv('SLEEP_INTERVAL', 0) )

def run(sock, file):
    """Make the client go go go"""
    with open(file) as fp:
        tuples = ([])
        line_count = 0
        for line in fp:
            line_count += 1;
            entries = line.split()
            if len(entries) == 3:
                tuples.append((entries[0], (entries[2], entries[1])))
            else:  
                print ("bad line: %s" % line)

            if line_count % MAX_BUFFER_SIZE == 0:  
                package = pickle.dumps(tuples, 1)
                size = struct.pack('!L', len(package))
                sock.sendall(size)
                sock.sendall(package)
                time.sleep(SLEEP_INTERVAL)
                print_progress(line_count)
                tuples = ([])
 
        package = pickle.dumps(tuples, 1)
        size = struct.pack('!L', len(package))
        sock.sendall(size)
        sock.sendall(package)
        print_progress(line_count)
        
def main():
    """Wrap it all up together"""
    if len(sys.argv) <= 1:
        raise SystemExit("usage %s <datafile>" % sys.argv[0])
    
    sock = socket.socket()
    try:
        sock.connect( (CARBON_SERVER, CARBON_PICKLE_PORT) )
    except socket.error:
        raise SystemExit("Couldn't connect to %(server)s on port %(port)d, is carbon-cache.py running?" % { 'server':CARBON_SERVER, 'port':CARBON_PICKLE_PORT })
    
    try:
        run(sock, sys.argv[1])
    except KeyboardInterrupt:
        sys.stderr.write("\nExiting on CTRL-c\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
