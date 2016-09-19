#!/usr/bin/python

##########################################################################
# This script allows to continuously receive graphite metrics from an    #
# external program through a pipe and to inject the metrics to a given   #
# Graphite carbon daemon through its pickle protocol                     #
#                                                                        #
# Copyright 2016 by Rodrigue Chakode <rodrigue.chakode@realopinsight.com>#
##########################################################################

import os
import re
import sys
import time
import socket
import platform
import subprocess
import pickle
import struct
import fileinput

# Set the address of the graphite carbon server. localhost by default
CARBON_CACHE_SERVER = os.getenv('CARBON_CACHE_SERVER', 'localhost')

# Set the port on which the carbon server expect pickle data. 2004 by default.
CARBON_CACHE_PICKLE_PORT = os.getenv('CARBON_CACHE_PICKLE_PORT', 2004)

#  Set the amount of graphite metrics to pack in each pickle request. 100 by default.
METRICS_BUFFER_SIZE = int( os.getenv('METRICS_BUFFER_SIZE', 100) )

# In some cases, if the amount of metrics packed in one request is very significant,  
# their handling by the carbon daemon may take a while. In those cases, it may be 
# helpful to wait a certain time (in second, floating number accepted) so to be sure
# that the carbon daemon has finished to handle the previous request before 
# submitting another one. Set it to 0, by default, means to not wait. 
TIME_BEFORE_NEXT_REQUEST = float( os.getenv('TIME_BEFORE_NEXT_REQUEST', 0) )

def print_progress(line_count):
  sys.stdout.write("\rLines parsed: %d" % (line_count) )
  sys.stdout.flush()
  
def print_error_and_exit(msg):
  print msg
  sys.exit(1)
	
def batch_metrics_and_subject_to_carbon(sock):
    tuples = ([])
    line_count = 0
    for line in fileinput.input():
        line_count += 1;
        entries = line.split()
        if len(entries) == 3:
          tuples.append((entries[0], (entries[2], entries[1])))
        else:
          print ("Entry has %d fields, instead of 3\n => %s" % (len(entries), line))
          
        if line_count % METRICS_BUFFER_SIZE == 0:  
          package = pickle.dumps(tuples, 1)
          size = struct.pack('!L', len(package))
          sock.sendall(size)
          sock.sendall(package)
          time.sleep(TIME_BEFORE_NEXT_REQUEST)
          print_progress(line_count)
          tuples = ([])

    package = pickle.dumps(tuples, 1)
    size = struct.pack('!L', len(package))
    sock.sendall(size)
    sock.sendall(package)
    print_progress(line_count)
  
    
def main():
    sock = socket.socket()
    try:
      sock.connect( (CARBON_CACHE_SERVER, CARBON_CACHE_PICKLE_PORT) )
    except socket.error:
      raise SystemExit("Couldn't connect to graphite backend, is carbon-cache.py running?")
    
    try:
      batch_metrics_and_subject_to_carbon(sock)
    except KeyboardInterrupt:
      sys.stderr.write("\nExiting on CTRL-c\n")
      sys.exit(0)
      
if __name__ == "__main__":
    main()
