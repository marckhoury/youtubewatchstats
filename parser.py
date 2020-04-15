import os
import time
import datetime 
import dateutil.parser

from html.parser import HTMLParser

pattern = 'content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1'

class YouTubeHistoryParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.video_ids = [] 
        self.datetimes = []

        self.inside_content_cell = False
        self.first_a_element = False
        self.second_a_element = False

    def handle_starttag(self, tag, attrs): 
        if self.inside_content_cell:
            if tag == 'a' and not self.first_a_element:
                url = attrs[0][1]
                start = url.find('watch')
                vid = url[start+8:]
                self.video_ids.append(vid)
            elif tag == 'a':
                self.second_a_element = True
        elif tag == 'div' and len(attrs) == 1 and len(attrs[0]) == 2 and \
             attrs[0][0] == 'class' and attrs[0][1] == pattern:
            self.inside_content_cell = True 
    
    def handle_endtag(self, tag):
        if self.inside_content_cell:
            if tag == 'div':
                self.inside_content_cell = False
                self.first_a_element = False
            elif tag == 'a' and not self.first_a_element:
                self.first_a_element = True
            elif tag == 'a':
                self.second_a_element = False
   
    def handle_data(self, data):
        if self.inside_content_cell:
            if self.first_a_element and not self.second_a_element:
                try: 
                    dt = dateutil.parser.parse(data, ignoretz=True) 
                    self.datetimes.append(dt)
                except ValueError as e:
                    pass
