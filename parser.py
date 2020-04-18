import dateutil.parser

class YouTubeHistoryParser():
    def __init__(self):
        super().__init__()
        self.video_ids = [] 
        self.datetimes = []

    def feed(self, data):
        for i in range(len(data)):
            entry = data[i]
            if 'titleUrl' in entry and 'time' in entry:
                url = entry['titleUrl']
                
                vid = url[url.find('watch')+8:] 
                dt = dateutil.parser.parse(entry['time'], ignoretz=True)
                
                self.video_ids.append(vid)
                self.datetimes.append(dt) 
