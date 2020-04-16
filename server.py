import os
import sys
import gzip 
import psycopg2

from flask import Flask
from flask import render_template, request, url_for, redirect
from werkzeug.utils import secure_filename
from logging.config import dictConfig
from rq import Queue 

from worker import redis_conn
from process import process_watch_history

app = Flask(__name__)

q = Queue(connection=redis_conn, default_timeout=3600)

ALLOWED_EXTENSIONS = {'html', 'txt'}
DATABASE_URL = os.environ["DATABASE_URL"]
        
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
                print('result returned')
                if type(job.result) == str: # in this case an error occured
                    return job.result
                else: #a correct result will be of type byte array
                    return gzip.decompress(job.result).decode()
            else:
                return 'None'
        else:
            return redirect(url_for('index')) 
    else: # request.method == 'POST'
        f = request.files['watchHistoryFile']
        if not (f and allowed_file(f.filename)):
            return redirect(url_for('index'))
    
        file_bytes = f.read()
        if len(file_bytes) == 0:
            return redirect(url_for('index'))

        data = gzip.compress(file_bytes)

        file_size = sys.getsizeof(file_bytes) * 1E-6 # in MB
        compressed_file_size = sys.getsizeof(data) * 1E-6
        savings = file_size - compressed_file_size 
        print('original file {0:.1f} MB, compressed {1:.1f} MB, savings {2:.1f} MB ({3:.1f} %)'.format(file_size, compressed_file_size, savings, savings / file_size * 100))

        job = q.enqueue(process_watch_history, args=(data,))
        return render_template('results.html', data=None, job_id=job.get_id())

@app.route('/errors', methods=['GET', 'POST'])
def errors():
    if request.method == 'GET':
        return redirect(url_for('index')) 
    else: # request.method == 'POST'
        f = request.files['watchHistoryFile']
        if not (f and allowed_file(f.filename)):
            return render_template('thanks.html')

        file_bytes = f.read()
        if len(file_bytes) == 0:
            return render_template('thanks.html')

        data = gzip.compress(file_bytes)

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        cmd = "INSERT INTO errors (file) VALUES (%s)"
        
        cursor.execute(cmd, (data,))
        conn.commit()
        cursor.close()
        conn.close()
        return render_template('thanks.html')
