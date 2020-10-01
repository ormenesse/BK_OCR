from pdf2image import convert_from_path
from configparser import ConfigParser
import pytesseract
import numpy as np
import boto3

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

def checkBank(filename):

    inifile = config(section='PRODUCTION')
    
    #connecting to boto3
    s3 = boto3.client('s3',
                      aws_access_key_id = inifile['aws_access_key_id'],
                      aws_secret_access_key = inifile['aws_secret_access_key'],
                      region_name = inifile['region_name']
                      )
    try:
    
        s3.download_file(Bucket=inifile['bucket'], Key=filename,Filename='./Downloads/'+filename)
    
        
        # Logo analysis
        
        dict_logos = {
            'inter' : (300,500,200,650,'inter','inter'),
            'sicoob' : (150,200,1100,1400,'SICOOB','SICOOB'),
            'sicoob2' : (330,380,600,830,'SICOOB','SICOOB2'),
            'sicoob3' : (170,230,680,860,'SICOOB','SICOOB3'),
            'sicoob4' : (100,180,1120,1350,'SICOOB','SICOOB4'),
            'santander' : (180,270,220,490,'Santander','Santander'),
            'santander2' : (250,370,320,650,'Santander','Santander2'),
            'bradesco' : (180,400,300,550,'bradesco','bradesco'),
            'bradesco2' : (340,400,300,530,'bradesco','bradesco2'),
            'bradesco3' : (200,250,400,900,'Bradesco Net Empresa','bradesco3'),
            'original' : (380,470,1830,2120,'ORIGINAL','ORIGINAL'),
            'original2' : (100,400,1900,2300,'ORIGINAL','ORIGINAL2'),
            'caixa' : (150,300,100,600,'CAIXA','CAIXA'),
            'itau' : (50,230,2000,2400,'ItauEmpresas','ItauEmpresas'),
            'itaupj2' :(300,500,200,600,'ItadEmpresas','ItadEmpresas'),
            'itaupj3' :(200,350,400,900,'ItauEmpresas','ItauEmpresas2'),
            'itaupj4' :(50,170,990,1480,'ItauEmpresas','ItauEmpresas4'),
            'bb' : (300,350,250,450,'EMPRESA','EMPRESA'),
            'bb2' : (370,430,200,320,'EMPRESA','EMPRESA'),
            'bbpj2' : (160,234,550,670,'SISBB','SISBB'), #- Sistema de Informag6es Banco do Brasil','SISBB - Sistema de Informag6es Banco do Brasil'),
            'sicredi' : (160,400,330,900,'Sicredi','Sicredi'),
            'safra' : (100,250,250,570,'Safra','Safra'),
            'stone' : (100,300,2000,2350,'stone','stone'),
            'c6bank' : (180,300,100,500, 'C6BANK','C6BANK'),
            'bs2' : (100,250,200,430, 'bs2','bs2'),
            'neon' : (0,180,50,500, 'QNCON','NEON'),
            'nubank' : (180,350,160,540, 'MU bank','nubank'),
        }

        logo = np.array(convert_from_path(pdf_path='./Downloads/'+filename,first_page=1,last_page=1,dpi=300)[0])

        ocr_result = ''

        for bk in dict_logos.keys():

            x , h, y , w , result, result_dup = dict_logos[bk]

            try:
                
                ocr_result = pytesseract.image_to_string(logo[x:h,y:w,:],config=r'--oem 3 --psm 7')
                
            except:
                
                ocr_result = None
            
            if ocr_result == result:
            
                return { 'Bank' : bk }

        return { 'Bank' : 'None' }
    
    except Exception as e:
        
        print(e)
        
        return { 'Bank' : 'None' }