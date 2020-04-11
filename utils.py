import json

def parse_duration(duration):
    h, m, s = 0, 0, 0

    _, duration = duration.split('T')
    tokens = duration.split('H')
    if len(tokens) == 1:
        duration = tokens[0]
    else:
        h = int(tokens[0])
        duration = tokens[1]

    tokens = duration.split('M')
    if len(tokens) == 1:
        duration = tokens[0]
    else:
        m = int(tokens[0])
        duration = tokens[1]

    tokens = duration.split('S')
    if len(tokens) == 1:
        duration = tokens[0]
    else:
        s = int(tokens[0])
        duration = tokens[1]

    return h, m, s

def chunks(arr, k):
    res = []
    for i in range(0, len(arr), k):
        res.append(arr[i:i+k])
    return res

def read_database(filename):
    data = {}
    with open(filename, 'r') as fin:
        json_data = json.load(fin) 
        for item in json_data['items']:
            vid = item['id']
            duration = item['contentDetails']['duration']
            data[vid] = duration
    return data
