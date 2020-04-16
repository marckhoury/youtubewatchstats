import os
import json
import httplib2

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

    def request_video_list(self, query):
        vids = ','.join(query)

        request = self.client.videos().list(
                    part="contentDetails",
                    id=vids
                )

        #httplib2, underlying google api client, is not thread safe
        #thus we create an http instance for each thread
        http = httplib2.Http()
        response = request.execute(http=http)

        attempted_keys = 1
        while 'error' in response:
            if attempted_keys == len(self.keys):
                return "QUOTA" 

            if response['error']['errors'][0]['reason'] == 'quotaExceeded':
                self.current_key = (self.current_key + 1) % len(self.keys)
                self.client = googleapiclient.discovery.build(
                                self.api_service_name, 
                                self.api_version, 
                                developerKey=self.keys[self.current_key])
                    
                request = self.client.videos().list(
                            part="contentDetails",
                            id=vids
                        )
                response = request.execute(http=http)
                attempted_keys += 1
            else: #unknown error
                return "UNKNOWN"
        return response


       
