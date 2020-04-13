import sys
import gzip 

from flask import Flask
from flask import render_template, request
from werkzeug.utils import secure_filename
from logging.config import dictConfig
from rq import Queue 

from worker import redis_conn
from process import process_watch_history

app = Flask(__name__)

q = Queue(connection=redis_conn, default_timeout=3600)

ALLOWED_EXTENSIONS = {'html', 'txt'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
                return gzip.decompress(job.result).decode()
            else:
                return 'None'
        else:
            return render_template('index.html') 
    else: # request.method == 'POST'
        f = request.files['watchHistoryFile']
        if not (f and allowed_file(f.filename)):
            return render_template('index.html')
    
        file_bytes = f.read()
        if len(file_bytes) == 0:
            return render_template('index.html') 

        data = gzip.compress(file_bytes)

        file_size = sys.getsizeof(file_bytes) * 1E-6 # in MB
        compressed_file_size = sys.getsizeof(data) * 1E-6
        savings = file_size - compressed_file_size 
        print('original file {0:.1f} MB, compressed {1:.1f} MB, savings {2:.1f} MB ({3:.1f} %)'.format(file_size, compressed_file_size, savings, savings / file_size * 100))

        job = q.enqueue(process_watch_history, args=(data,))
        return render_template('results.html', data=None, job_id=job.get_id())
