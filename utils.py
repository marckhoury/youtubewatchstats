import json
import re

def parse_duration(duration):
    pattern = r"\d+[HMS]"
    h, m, s = 0, 0, 0
    matches = re.finditer(pattern, duration)
    for i, match in enumerate(matches):
        match = match.group()
        val, unit = int(match[:-1]), match[-1]   
        if unit == 'H':
            h = val
        elif unit == 'M':
            m = val 
        else:
            s = val
    return h, m, s

def chunks(arr, k):
    res = []
    for i in range(0, len(arr), k):
        res.append(arr[i:i+k])
    return res
