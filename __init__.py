from flask import Flask, request, redirect, url_for, flash, jsonify, abort
from functions_imports import *
from checkBank import *
from flask_cors import CORS
from worker import conn
from redis import Redis
from rq.job import Job
from rq import Queue

#Redis Queue
#initializing worker
#Be sure to initiliaze more than 1 worker
q = Queue(connection=conn)

#q2 = Queue(connection=conn)
queueBoolean = True

app = Flask(__name__)
CORS(app) #Prevents CORS errors

@app.route('/')
def works():
    return abort(400, 'Bad Request')

"""
# Example
{
    "number" : 436,
    "statement_id" : "zEOOBzwtAA",
    "environment" : "PRODUCTION",
    "filename" : "28ffdabdee92fd92faa04910e2a42507_comprovanteibe63E698049B69498395763D94A7F391A1.pdf"
}
#curl --insecure -d '{"number" : 100,"statement_id" : "LvY5isEePI", "environment" : "PRODUCTION"}' -H "content-type: application/json" -X POST https://URL/api/ocr
"""
@app.route('/api/ocr', methods=['POST'])
def process_statement():
    
    global queueBoolean
    
    gc.collect()

    data = request.get_json()
    
    if data['statement_id'] is not None and data['environment'] in ['PRODUCTION','SANDBOX'] and data['filename'] is not None:
            
        job = q.enqueue(return_statement_OCRd,args=(data['statement_id'],data['environment'],data['filename'],),max_retries=3,job_timeout='20m')

        return jsonify({'Message':'Request received', 'Job id' : job.get_id()})

    else:

        gc.collect()

        abort(400, 'Bad Request')
        
@app.route('/api/ocr', methods=['GET'])
def process_statement_get():
    
    global queueBoolean
    
    number = int(request.args.get('number'))
        
    statement_id = request.args.get('statement_id')
        
    environment = request.args.get('environment')
        
    filename = request.args.get('filename')
    
    gc.collect()

    if statement_id is not None and environment in ['PRODUCTION','SANDBOX'] and filename is not None:
            
        job = q.enqueue(return_statement_OCRd,args=(statement_id,environment,filename,),max_retries=3,job_timeout='20m')

        return jsonify({'Message':'Request received', 'Job id' : job.get_id()})

    else:

        gc.collect()

        abort(400, 'Bad Request')
        
@app.route("/results", methods=['GET'])
def get_results():
    
    job_key = request.args.get('jobKey')
    
    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        return jsonify({'result' : str(job.result), 'enqueued_at' : str(job.enqueued_at), 'started_at' : str(job.started_at), 'endend_at' : str(job.ended_at) }), 200
    else:
        return "Job still waiting or working on it!", 202
    
    
@app.route('/api/ocrValidation', methods=['GET'])
def checkIfValid():
           
    filename = request.args.get('filename')
    
    gc.collect()

    if filename is not None:

        return checkBank(filename)

    else:

        gc.collect()

        abort(400, 'Bad Request')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
