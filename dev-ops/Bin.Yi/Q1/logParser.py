#!/usr/bin/env python3

import gzip
import pathlib

class Entry:
    def __init__(self, deviceName, processId, processName, description, timeWindow, numberOfOccurrence):
        self.deviceName = deviceName
        self.processId = processId
        self.processName = processName
        self.description = description
        self.timeWindow = timeWindow
        self.numberOfOccurrence = numberOfOccurrence

def getTimeWindow(hour):
    intHour = int(hour)
    return "%02d00-%02d00" % (intHour, intHour+1)

def parseLine(line, last):
    import re
    m = re.match(r"\w{3} \d+ (\d{2}):\d{2}:\d{2} ([\w|\.]+) ([\w|\.| ]+)\[(\d+)\](.*)", line)
    if m:
        current = {
            "deviceName" : m.group(2),
            "processId" : m.group(4),
            "processName" : m.group(3),
            "description" : m.group(5),
            "timeWindow" : getTimeWindow(m.group(1)),
            "numberOfOccurrence" : 1,
        }
        return last, current
    else:
        m1 = re.match(r"\w{3} \d+ (\d{2}):\d{2}:\d{2} --- last message repeated (\d+) time ---", line)
        if m1:
            if last == None:
                # if this line is repeat but no last line
                print("NO PREVIOUS LINE: ", line)
                return None, None
            if getTimeWindow(m1.group(1)) != last["timeWindow"]:
                # if this line is repeat but last line in different hour
                print("WARN: REPEAT MESSAGE CROSS HOUR")
            last["numberOfOccurrence"] += int(m1.group(2))
            return last, None
        else:
            # not a first line, not a repeat line, should be succeeded line(s)
            if last == None:
                print("NO PREVIOUS LINE: ", line)
                return None, None
            last["description"] += "\n" + line
            # don't return last since it's possible have extra succeeded line(s)
            return None, last
    

def send(cache):
    import requests, os
    url = os.getenv('API_ENDPOINT')
    if url == None:
        url = "http://localhost:8000"
    print("sending",  len(cache), "entries...")
    r = requests.post(url, json=cache)
    print("server returns", r.status_code)

dir = pathlib.Path(__file__).parent.absolute()

BATCH_LINES = 1000

with gzip.open(str(dir) + "/../../DevOps_interview_data_set.gz", 'rb') as f:
    last = None
    lineNumber = 0
    cache = []
    for line in f:
        last, this = parseLine(line.decode().strip(), last)
        if last != None:
            cache.append(last)
            if len(cache) >= BATCH_LINES:
                send(cache)
                cache = []
        last = this
        lineNumber += 1
    if this != None:
        cache.append(this)
    send(cache)
