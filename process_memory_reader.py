#! /usr/bin/env python2

"""@package docstring
Documentation for this module.
More details.
"""

import re
import os

class process_memory_reader():
    """Documentation for a class.
    https://unix.stackexchange.com/questions/6301/how-do-i-read-from-proc-pid-mem-under-linux
    """
    def __init__(self, pid):
        self.maps_file = open("/proc/%s/maps"%(pid), 'r')
        self.mem_file = open("/proc/%s/mem"%(pid), 'rb', 0)

    def get_chunk(self):
        for line in self.maps_file.readlines():  # for each mapped region
            m = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+) ([-r])', line)
            if m.group(3) == 'r':  # if this is a readable region
                start = int(m.group(1), 16)
                end = int(m.group(2), 16)
                length = end-start
                intmax = 1<<63-1
                if start <= intmax: # TODO: make this work with long adresses
                    self.mem_file.seek(start)  # seek to region start
                    somebytes = None
                    try:
                        yield self.mem_file.read(length)  # read region contents
                    except IOError as ioe:
                        #print(str(ioe))
                        pass
                        
if __name__ == "__main__":
    import sys
    pid = sys.argv[1]
    num_chunks = 0
    total_length = 0
    pmr = process_memory_reader(pid)
    for chunk in pmr.get_chunk():
        num_chunks += 1
        total_length += len(chunk)
    print("Read %d chunks of %d bytes total length from process %s."%(num_chunks,total_length,pid))
