import os
import sys
import math
import time
import datetime
import json

import numpy as np
import pandas as pd

import api
import utils
import database

from flask import Flask
from flask import render_template, request
from werkzeug.utils import secure_filename
from logging.config import dictConfig

from parser import YouTubeHistoryParser

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.FileHandler',
        'filename': 'diagnostics.log',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['GET', 'POST'])
def results():
    if request.method == 'GET':
        return render_template('index.html')
    else: # request.method == 'POST'
        f = request.files['watchHistoryFile']
        data = f.read().decode() 
        
        parser = YouTubeHistoryParser()
        parser.feed(data)

        app.logger.info('file successfully parsed')        

        conn = database.create_connection('yt-data.db')
        database.create_table(conn)
  
        queries = set([]) 
        for vid in parser.video_ids:
            if database.select_video(conn, vid) == None:
                queries.add(vid)
        
        previously_queried = len(parser.video_ids) - len(queries)
        if len(queries) > 0:
            queries = list(queries)
            queries = utils.chunks(queries, 50)
       
            youtube = api.create_youtube_api_client()
            for query in queries:
                remaining_queries = set(query)

                response = api.request_video_list(youtube, query) 

                for item in response['items']:
                    vid = item['id']
                    title, duration = '', ''
                    if 'title' in item['snippet']:
                        title = item['snippet']['title']
                    if 'duration' in item['contentDetails']:
                        duration = item['contentDetails']['duration']
                
                    database.create_video(conn, (vid, title, duration, 1))
                    remaining_queries.remove(vid)
        
                # all remaining queries are invalid, don't query api again
                for vid in remaining_queries:
                    database.create_video(conn, (vid, None, None, 0))
        
            conn.commit()
        
        app.logger.info('{0} videos of {1} in database, {2} queries saved'.format(previously_queried, len(parser.video_ids), math.ceil(previously_queried / 50)))
         
        total_seconds = 0 
        durations, datetimes = [], []
        for i in range(len(parser.video_ids)):
            vid = parser.video_ids[i]
            _, _, duration, valid = database.select_video(conn, vid)
            if valid:
                h, m, s = utils.parse_duration(duration) 
                seconds = 3600 * h + 60 * m + s
                durations.append(seconds / 60.0)
                datetimes.append(parser.datetimes[i])
                total_seconds += seconds
    
        number_of_videos = len(durations)
        total_days = total_seconds / 3600.0 / 24.0
   
        data = {'number_of_videos': number_of_videos, 'total_days': total_days}
         
        df = pd.DataFrame(parser.datetimes, columns=['date'])
        month_count = df.groupby([df["date"].dt.year, df["date"].dt.month]).count()
        month_count = month_count.rename(columns={'date': 'value'})
        month_count['date'] = month_count.index
        month_count = month_count.reset_index(drop=True)
        month_count = month_count.to_dict(orient='records')
        data['month_count'] = json.dumps(month_count, indent=2)


        day_count = df.groupby([df["date"].dt.year, df["date"].dt.month, df['date'].dt.day]).count()
        day_count = day_count.rename(columns={'date': 'value'})
        day_count['date'] = day_count.index
        day_count = day_count.reset_index(drop=True)
        day_count = day_count.to_dict(orient='records')
        data['day_count'] = json.dumps(day_count, indent=2)


        df = pd.DataFrame({'date': datetimes, 'duration': durations})
        month_sum = df.groupby([df["date"].dt.year, df["date"].dt.month]).sum() / 60.0
        month_sum = month_sum.rename(columns={'duration': 'value'})
        month_sum['date'] = month_sum.index
        month_sum = month_sum.reset_index(drop=True)
        month_sum = month_sum.to_dict(orient='records')
        data['month_sum'] = json.dumps(month_sum, indent=2)
       
 
        day_sum = df.groupby([df["date"].dt.year, df["date"].dt.month, df['date'].dt.day]).sum() / 60.0
        day_sum = day_sum.rename(columns={'duration': 'value'})
        day_sum['date'] = day_sum.index
        day_sum = day_sum.reset_index(drop=True)
        day_sum = day_sum.to_dict(orient='records')
        data['day_sum'] = json.dumps(day_sum, indent=2)

        data['durations'] = json.dumps(durations, indent=2)

        conn.close() 
        return render_template('results.html', data=data)
