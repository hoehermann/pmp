#! /usr/bin/env python2

import Queue
import threading
import sys
from process_memory_pictures_tk import process_memory_pictures_frontend
from process_memory_pictures_producer import process_memory_pictures_producer

if __name__ == "__main__":
    image_queue = Queue.Queue(1)
    termination_request_queue = Queue.Queue()
    pmpp = process_memory_pictures_producer(image_queue, termination_request_queue)
    thread = threading.Thread(target=pmpp.extract_images, args=(sys.argv[1:],))
    thread.start()
    sleeptime_milliseconds = 200
    pmpf = process_memory_pictures_frontend(image_queue, sleeptime_milliseconds, fullscreen=True)
    pmpf.run()
    print("Frontend has ended. Requesting worker thread termination...")
    termination_request_queue.put(None)
    if thread.is_alive():
        print("Waiting for worker thread...")
        try:
            image_queue.get(block=False)
        except Queue.Empty:
            pass
    thread.join()
    print("Clean exit.")
    
