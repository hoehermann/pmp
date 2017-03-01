#! /usr/bin/env python2

PIDS_FILTER = "all"

if PIDS_FILTER == "graphical":
    import subprocess
    def get_pids():
        pids = set()
        wmctrldata = subprocess.check_output(["wmctrl", "-lp"])
        #[parts[2] for line in wmctrldata.split("\n") if parts for parts in line.split()])
        for line in wmctrldata.split("\n"):
            parts = line.split()
            if parts and int(parts[2]) > 0:
                pids.add(parts[2])
        return pids

elif PIDS_FILTER == "all":
    import os
    def get_pids():
        return [d for d in os.listdir("/proc") if d.isdigit() and int(d) > 100]
