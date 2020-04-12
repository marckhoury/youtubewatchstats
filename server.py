from flask import Flask
from flask import render_template, request
from werkzeug.utils import secure_filename
from logging.config import dictConfig
from rq import Queue 

from worker import redis_conn
from process import process_watch_history

app = Flask(__name__)

q = Queue(connection=redis_conn)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results/<job_id>', methods=['GET'])
@app.route('/results', methods=['GET', 'POST'])
def results(job_id=None):
    if request.method == 'GET':
        if job_id != None:
            job = q.fetch_job(job_id)
            if job.get_status() == 'finished':
                return job.result
            else:
                return 'None'
        else:
            return render_template('index.html') 
    else: # request.method == 'POST'
        import sys
        f = request.files['watchHistoryFile']
        data = f.read()
        job = q.enqueue(process_watch_history, args=(data,), timeout='5m')
        return render_template('results.html', data=None, job_id=job.get_id())
