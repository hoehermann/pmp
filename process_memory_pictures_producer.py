#! /usr/bin/env python2

"""@package docstring
Documentation for this module.
More details.
"""

BACKEND = "pil"
if BACKEND == "pil":
    from io import BytesIO
    from PIL import Image
elif BACKEND == "opencv":
    import cv2
    import numpy as np
else:
    raise RuntimeError()

import Queue
import re
import errno
from process_memory_reader import process_memory_reader
import process_lister
    
JPEG_HEADER = b"\xff\xd8\xff\xe0\x00\x10\x4A\x46\x49\x46\x00"
PNG_HEADER = b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"
HEADER_REGEX = re.compile(b"|".join([JPEG_HEADER,PNG_HEADER]))

class process_memory_pictures_producer():
    def __init__(self, image_queue, termination_request_queue):
        self.image_queue = image_queue
        self.termination_request_queue = termination_request_queue
        self.keep_running = True

    def termination_requested(self):
        try:
            self.termination_request_queue.get(block=False)
            self.keep_running = False
        except Queue.Empty:
            pass
        return not self.keep_running

    def extract_images(self, pids=[]):
        num_images = 0
        while not self.termination_requested():
            if not pids:
                #print("Getting pids...")
                pids = process_lister.get_pids()
            for pid in pids:
                #print("Reading memory from %s..."%pid)
                try:
                    pmr = process_memory_reader(pid)
                    for chunk in pmr.get_chunk():
                        if self.termination_requested():
                            break
                        for m in HEADER_REGEX.finditer(chunk):
                            if self.termination_requested():
                                break
                            offset = m.start()
                            image = None
                            try:
                                if BACKEND == "pil":
                                    # https://stackoverflow.com/questions/32908639/
                                    image = Image.open(BytesIO(chunk[offset:]))
                                elif BACKEND == "opencv":
                                    # https://stackoverflow.com/questions/13329445/
                                    image = cv2.imdecode(
                                        np.asarray(
                                            bytearray(chunk[offset:]), 
                                            dtype=np.uint8), 
                                        1)
                            except IOError as ioe:
                                #print(str(ioe))
                                pass
                            if image is not None and image:
                                #image.save("%03d.png"%(num_images))
                                # TODO: this is not perfectly deadlock-free
                                self.image_queue.put(image, block=True)
                                num_images += 1
                except IOError as ioe:
                    if ioe.errno == errno.EACCES:
                        print("Permission Denied while accessing memory of process %s.\nCheck permissions or run as root."%(pid))
                        self.image_queue.put(None, block=True)
                        raise
                    else:
                        pass
                        
if __name__ == "__main__":
    import threading
    import sys
    image_queue = Queue.Queue()
    termination_request_queue = Queue.Queue()
    pmpp = process_memory_pictures_producer(image_queue, termination_request_queue)
    thread = threading.Thread(target=pmpp.extract_images, args=(sys.argv[1:],))
    thread.start()
    while True:
        if not thread.is_alive():
            print("Worker thread ended.")
            break
        try:
            image = image_queue.get(block=True, timeout=0.01)
            print(image)
        except Queue.Empty:
            pass
        except KeyboardInterrupt:
            print("Terminating...")
            termination_request_queue.put(None)
            break
    if thread.is_alive():
        print("Waiting for worker thread...")
    thread.join()
    print("Clean exit.")
