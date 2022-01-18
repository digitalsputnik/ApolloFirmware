import time

synced = False

offset = 0

def sync(time_in):
    global offset, synced
    offset = abs(time.ticks_diff(time_in, time.ticks_ms()))
    synced = True