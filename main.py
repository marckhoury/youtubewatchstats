import os
import sys
import math
import time
import datetime
import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import api
import utils
import database

from parser import YouTubeHistoryParser

def main():
    data = open('watch-history.html', 'r').read()
    
    parser = YouTubeHistoryParser()
    parser.feed(data)

    conn = database.create_connection('yt-data.db')
    database.create_table(conn)
  
    queries = set([]) 
    for vid in parser.video_ids:
        if database.select_video(conn, vid) == None:
            queries.add(vid)
    
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
    print('Total Hours = {0}'.format(total_seconds / 3600.0))
    
    df = pd.DataFrame(parser.datetimes, columns=['date'])
    df.groupby([df["date"].dt.year, df["date"].dt.month]).count().plot(kind="bar")
    plt.xlabel('date (month)')
    plt.ylabel('number of videos')
    plt.show()
    df.groupby([df["date"].dt.year, df["date"].dt.month, df['date'].dt.day]).count().plot(kind="bar")
    plt.xlabel('date')
    plt.ylabel('number of videos')
    plt.show()

    df = pd.DataFrame({'date': datetimes, 'duration': durations})
    (df.groupby([df["date"].dt.year, df["date"].dt.month]).sum() / 60.0).plot(kind='bar')
    plt.xlabel('date (month)')
    plt.ylabel('watch time (hours) ')
    plt.show()
    (df.groupby([df["date"].dt.year, df["date"].dt.month, df['date'].dt.day]).sum() / 60.0).plot(kind='bar')
    plt.xlabel('date')
    plt.ylabel('watch time (hours)')
    plt.show()
    
    df = pd.DataFrame({'duration': durations})
    df['duration'].hist(bins=math.ceil(max(durations)))
    plt.xlabel('time (min)')
    plt.ylabel('number of videos')
    plt.show()

    conn.close() 

if __name__ == "__main__":
    main()