# pmp
Process Memory Pictures - A screensaver-esque application displaying images scraped from currently allocated memory.

### Dependencies
python2, PIL and tkinter.

### Usage
Start with

    sudo python2 process_memory_pictures.py

Must be run as root, since only root may access arbitrary memory regioins currently allocated by running processes.

### Sample
It looks like this:

![Screenshot](/screenshot.png?raw=true "Screenshot")

Pictures were extracted from some nvidia background task, thunar and firefox.
