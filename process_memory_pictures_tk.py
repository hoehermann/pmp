#! /usr/bin/env python2

import Queue
from PIL import Image, ImageTk
import Tkinter as tk
import threading
from random import randint

class process_memory_pictures_frontend():
    
    def random_position(self, width, height):
        width = min(width, self.canvas_width)
        height = min(height, self.canvas_height)
        x = randint(0,self.canvas_width-width)
        y = randint(0,self.canvas_height-height)
        return (x,y)
    
    def __init__(self, image_queue, sleeptime_milliseconds, fullscreen = True):
        self.queue = image_queue
        self.sleeptime_milliseconds = sleeptime_milliseconds
        self.root = tk.Tk()
        # https://stackoverflow.com/questions/7966119/
        self.root.attributes('-fullscreen', fullscreen)
        self.canvas_width = self.root.winfo_screenwidth()
        self.canvas_height = self.root.winfo_screenheight()
        if not fullscreen:
            self.canvas_width //= 2
            self.canvas_height //= 2
        self.canvas = Image.new('RGB', self.get_canvas_dimensions(), (0,0,0))
        self.tk_canvas_adapter = ImageTk.PhotoImage(self.canvas)
        self.tk_canvas = tk.Canvas(
            self.root, 
            width=self.canvas_width,
            height=self.canvas_height,
            bg='black'
        )
        self.tk_canvas.pack()
        self.root.focus_set()
        self.root.bind('<Escape>', lambda e: e.widget.quit())
    
    def get_canvas_dimensions(self):
        return (self.canvas_width, self.canvas_height)
        
    def pop_image_queue(self):
        try:
            image = self.queue.get(block=False)
            if image is None:
                self.root.quit()
            else:
                width, height = image.size
                self.canvas.paste(image, self.random_position(width, height))
                self.tk_canvas_adapter = ImageTk.PhotoImage(self.canvas)
                self.tk_canvas.create_image(0,0,image=self.tk_canvas_adapter,anchor="nw")
                self.root.update()
        except Queue.Empty:
            pass
        except IOError as ioe:
            # IOError: unrecognized data stream contents when reading image file
            pass
        except SyntaxError as se:
            #SyntaxError: broken PNG file (chunk '\x00\x00\x00\x00'
            pass
        except:
            self.root.quit()
            raise
        self.root.after(self.sleeptime_milliseconds, self.pop_image_queue)
    
    def run(self):
        w, h = self.get_canvas_dimensions()
        self.tk_canvas.create_text(
            w//2,
            h//2,
            fill="white",
            text="Press escape to exit."
        )
        self.root.update()
        self.root.after(self.sleeptime_milliseconds, self.pop_image_queue)
        self.root.mainloop()
        
if __name__ == "__main__":
    sleeptime_milliseconds = 200
    image_queue = Queue.Queue()
    for i in range(255):
        color = (i,(i*2)%256,(i*3)%256)
        image_queue.put(Image.new('RGB', (100,100), color))
    pmpf = process_memory_pictures_frontend(image_queue, sleeptime_milliseconds)
    pmpf.run()
