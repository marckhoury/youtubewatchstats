import os
import json
import httplib2
import threading

import googleapiclient.discovery
import googleapiclient.errors

class ApiClient:
    def __init__(self):
        self.api_service_name = "youtube"
        self.api_version = "v3"
        
        self.keys = json.loads(os.environ['API_KEYS'])
        self.current_key = 0

        self.client = googleapiclient.discovery.build(
                        self.api_service_name, 
                        self.api_version, 
                        developerKey=self.keys[self.current_key])
        
        self.lock = threading.Lock()

    def request_video_list(self, query):
        vids = ','.join(query)

        request = self.client.videos().list(
                    part="contentDetails",
                    id=vids
                )
        #httplib2, underlying google api client, is not thread safe
        #thus we create an http instance for each thread
        http = httplib2.Http()
        try: 
            response = request.execute(http=http)
        except googleapiclient.errors.HttpError as e:
            response = json.loads(e.content)
        #the code below is intended to rotate keys in a thread safe way
        #it looks like we waste an api call, since the result must be error to enter the loop
        #this is true for the first thread that enters the loop, but not true for subsequent threads
        #a thread must first acquire the lock then check if the current api client has not been 
        #updated by a different thread, and thus may be valid
        #once a thread has acquired the lock and confirmed that the client has reached quota
        #it can safely update the client key without worrying about other threads
        #once a successful key is found all subsequent threads execute the loop once to update response
        if 'error' in response:
            self.lock.acquire()
            attempted_keys = 0
            while 'error' in response:
                attempted_keys += 1
                request = self.client.videos().list(
                            part="contentDetails",
                            id=vids
                        )
                try:
                    response = request.execute(http=http)
                except googleapiclient.errors.HttpError as e:
                    response = json.loads(e.content)
                if 'error' in response:
                    if response['error']['errors'][0]['reason'] in ['quotaExceeded', 'dailyLimitExceeded']:
                        self.current_key = (self.current_key + 1) % len(self.keys)
                        self.client = googleapiclient.discovery.build(
                                    self.api_service_name, 
                                    self.api_version, 
                                    developerKey=self.keys[self.current_key])
                    else: #unknown error
                        self.lock.release()
                        return "UNKNOWN"

                if attempted_keys > len(self.keys):
                    self.lock.release()
                    return "QUOTA" 
            self.lock.release()
        return response


       
