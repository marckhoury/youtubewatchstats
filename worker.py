import os
import urllib.parse

import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

url = urllib.parse.urlparse(os.environ.get('REDISCLOUD_URL'))
redis_conn = redis.Redis(host=url.hostname, port=url.port, password=url.password)

if __name__ == '__main__':
    with Connection(redis_conn):
        worker = Worker(map(Queue, listen))
        worker.work()
