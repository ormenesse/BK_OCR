import pymongo
import pandas as pd
import numpy as np
import base64
import datetime
import requests

def generateClient():
    
    return pymongo.MongoClient(base64.b64decode('bW9uZ29kYitzcnY6Ly92b3JtZW5lc3NlOkd5cmEyMDE5IUBneXJhbWFpcy1wcm9kdWN0aW9uLWxod3RiLm1vbmdvZGIubmV0L3Rlc3Q/cmV0cnlXcml0ZXM9dHJ1ZSZ3PW1ham9yaXR5').decode(), ssl=True)


def main():

    time_diff = datetime.datetime.now() - datetime.timedelta(hours=1)
    
    query = [

        {
            '$match' : 
            { 
                '_created_at' : {'$gte' : time_diff },
                'mimetype' : 'application/pdf',
                'parent.className' : 'BankAccount',
                'parent.column' : 'statement'
            }
        },
        {
            '$project' : {
                '_id' : 1,
                'file' : 1,
                'parent.id' : 1

            }
        },
        {
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
        }, 
        {
            '$unwind': {
                'path': '$BankAccount', 
                'preserveNullAndEmptyArrays': True
            }
        }, 
        {
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
                        '$match': 
                        {
                            '$expr': 
                            {
                                '$eq': 
                                [
                                    '$_id', '$$type_splited'
                                ]
                            }
                        }
                    }
                ], 
                'as': 'business'
            }
        }, 
        {
            '$unwind': 
            {
                'path': '$business', 
                'preserveNullAndEmptyArrays': True
            }
        }
    ]


    client = generateClient()

    res = list(client['gyramais']['File'].aggregate(query))

    if len(res) > 0:

        res = pd.json_normalize(res)[['business.number', '_id','file']]

        res["environment"] = 'PRODUCTION'

        res.columns = ['number', 'statement_id', 'filename', 'environment']

        for i in res.to_dict(orient='records'):

            response = requests.post('https://ocr.gyramais.com.br/api/ocr', json=i)

            print(response.text)

        
if __name__ == "__main__":
    
    main()
