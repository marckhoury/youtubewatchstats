import os

import googleapiclient.discovery
import googleapiclient.errors

def create_youtube_api_client():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    developer_key = os.environ['API_KEY']    
 
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=developer_key)

    return youtube

def request_video_list(youtube, query):
    vids = ','.join(query)

    request = youtube.videos().list(
                part="snippet,contentDetails",
                id=vids
    )
    response = request.execute()
    return response 
