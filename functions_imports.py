from pdf2image import convert_from_path
from configparser import ConfigParser
from unicodedata import normalize
from bank_statement_ocr import *
from imutils import contours
from flask import jsonify
import pytesseract
import numpy as np
import linecache
import operator
import datetime
import requests
import imutils
import pymongo
import logging
import boto3
import json
import cv2
import sys
import re
import gc
import os

def return_query_file(i):

    query_file = [
        {
            '$match': {
                '_id' : i
            }
        }, {
            '$lookup': {
                'from': 'BankAccount', 
                'let': {
                    'type_splited': '$parent.id'
                }, 
                'pipeline': [
                    {
                        '$project': {
                            '_id': '$_id', 
                            '_p_business': {
                                '$substr': [
                                    '$_p_business', 9, -1
                                ]
                            }
                        }
                    }, {
                        '$match': {
                            '$expr': {
                                '$eq': [
                                    '$_id', '$$type_splited'
                                ]
                            }
                        }
                    }
                ], 
                'as': 'BankAccount'
            }
        }, {
            '$unwind': {
                'path': '$BankAccount', 
                'preserveNullAndEmptyArrays': True
            }
        }, {
            '$lookup': {
                'from': 'Business', 
                'let': {
                    'type_splited': '$BankAccount._p_business'
                }, 
                'pipeline': [
                    {
                        '$project': {
                            'number': '$number'
                        }
                    }, {
                        '$match': {
                            '$expr': {
                                '$eq': [
                                    '$_id', '$$type_splited'
                                ]
                            }
                        }
                    }
                ], 
                'as': 'business'
            }
        }, {
            '$unwind': {
                'path': '$business', 
                'preserveNullAndEmptyArrays': True
            }
        }, {
            '$project': {
                '_id': True, 
                'businessNumber': '$business.number',
                'file' : True
            }
        }
    ]
    return query_file

def config(filename='./database.ini', section='posturl'):
    parser = ConfigParser()
    parser.read(filename)
    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return db

def return_statement_OCRd(state_id,environment,filename):
    
    inifile = config(section=environment)
    
    if os.path.isfile('./Downloads/'+filename):
       
        try:
            
            # Analyze Documents
            analysis = bank_statement_ocr('./Downloads/'+filename,state_id)

            statement = analysis.start_analysis()

            with open('./JSONS/'+filename+'.json', 'w') as f:
                json.dump(statement, f)

        except:

            statement = {}

            statement['Error'] = "File not found on boto3."

            statement['_id'] = state_id

        response = requests.post(inifile['url'],json=statement, timeout=60)
    
    else:
        #connecting to boto3
        s3 = boto3.client('s3',
                          aws_access_key_id = inifile['aws_access_key_id'],
                          aws_secret_access_key = inifile['aws_secret_access_key'],
                          region_name = inifile['region_name']
                          )
        try:

            s3.download_file(Bucket=inifile['bucket'], Key=filename,Filename='./Downloads/'+filename)

            # Analyze Documents
            analysis = bank_statement_ocr('./Downloads/'+filename,state_id)

            statement = analysis.start_analysis()

            with open('./JSONS/'+filename+'.json', 'w') as f:
                json.dump(statement, f)

        except:

            statement = {}

            statement['Error'] = "File not found on boto3."

            statement['_id'] = state_id

        response = requests.post(inifile['url'],json=statement, timeout=60)

    gc.collect()
    
    return response.text