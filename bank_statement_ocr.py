from pdf2image import convert_from_path
from unicodedata import normalize
import matplotlib.pyplot as plt
from imutils import contours
import pytesseract
import numpy as np
import linecache
import operator
import datetime
import imutils
import logging
import json
import cv2
import sys
import re
import gc

# Importing Mixin classes
import _bb
import _bradesco
import _caixa
import _inter
import _itau
import _open_cv_stuff
import _original
import _santander
import _sicoob
import _sicredi
import _safra

class bank_statement_ocr(_open_cv_stuff.Mixin,_bb.Mixin1,_bradesco.Mixin2,
                         _inter.Mixin3,_itau.Mixin4,_caixa.Mixin5,
                         _original.Mixin6,_santander.Mixin7,_sicoob.Mixin8,
                         _sicredi.Mixin9,_safra.Mixin10):
    
    def __init__(self,filename,file_id='',number=-1):
        
        self.filename = filename
        # transforming bank statement into a image
        self.pages = convert_from_path(filename, 300)
        self.fullpicture = None
        self.bank = None
        self.number = number
        self.file_id = file_id
        self.statement = None
        self.name = None
        self.branchCode = None
        self.AccountNumber = None
        #logging errors, infos etc.
        self.logger = logging.getLogger('OCR')
        self.hdlr = logging.FileHandler('/var/tmp/OCR.log')
        self.formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        self.hdlr.setFormatter(self.formatter)
        self.logger.addHandler(self.hdlr) 
        self.logger.setLevel(logging.INFO)
    
    def remover_acentos(self,txt):
        
        return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')
    
    def check_bank(self):
        
        dict_logos = {
            'inter' : (300,500,200,650,'inter','inter'),
            'sicoob' : (150,200,1100,1400,'SICOOB','SICOOB'),
            'santander' : (180,270,220,490,'Santander','Santander'),
            'bradesco' : (180,400,300,550,'bradesco','bradesco'),
            'bradesco2' : (340,400,300,530,'bradesco','bradesco2'),
            'original' : (380,470,1830,2120,'ORIGINAL','ORIGINAL'),
            'original2' : (100,400,1900,2300,'ORIGINAL','ORIGINAL2'),
            'caixa' : (150,300,100,600,'CAIXA','CAIXA'),
            'itau' : (50,230,2000,2400,'ItauEmpresas','ItauEmpresas'),
            'itaupj2' :(300,500,200,600,'ItadEmpresas','ItadEmpresas'),
            'bb' : (300,350,250,450,'EMPRESA','EMPRESA'),
            'bb2' : (370,430,200,320,'EMPRESA','EMPRESA'),
            'bbpj2' : (160,234,550,1265,'SISBB - Sistema de Informag6es Banco do Brasil','SISBB - Sistema de Informag6es Banco do Brasil'),
            'sicredi' : (160,400,330,900,'Sicredi','Sicredi'),
            'safra' : (100,250,250,570,'Safra','Safra')
        }
        
        logo = np.array(self.pages[0])
        
        ocr_result = ''
        
        for bk in dict_logos.keys():
            
            x , h, y , w , result, result_dup = dict_logos[bk]
            
            try: 
                ocr_result = pytesseract.image_to_string(logo[x:h,y:w,:],config=r'--oem 3 --psm 7')
            except:
                ocr_result = None
                
            if ocr_result == result:
                
                return result_dup
            
        return None
    
    def start_analysis(self):
        
        self.logger.info('OCR starting for filename: ' + self.filename)
        
        pdfbank = self.check_bank()
        
        if pdfbank is None:
            self.logger.error("OCR couldn`t find bank name on the statement. Filename:" + self.filename)
            return ['{Error: "OCR couldn`t find bank name on the statement."}']
        else:
            self.bank = pdfbank
        # udpate classe picture of pages 
        self.return_document_picture(pdfbank)
        
        if self.fullpicture is None:
            self.logger.error("Couldn`t transform PDF to image. Filename:" + self.filename)
            return ['{Error : "Couldn`t transform PDF to image."}']
        
        # getting output
        final_output = self.do_opencv_stuff()
        
        # parsing output
        if pdfbank == 'inter':
            
            self.statement = self.output_inter(final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_inter()
        
        elif pdfbank == 'SICOOB':
            
            self.statement = self.output_sicoob(final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_sicoob()
        
        elif pdfbank == 'Santander':
            
            self.statement = self.output_santander(final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_santander()
        
        elif pdfbank == 'bradesco':
            
            if pytesseract.image_to_string(np.array(self.pages[0])[150:230,600:1300,:],config=r'--oem 3 --psm 7') == 'Extrato Mensal / Por Periodo':
                
                self.statement = self.output_bradescopj2(final_output)
                
                self.name, self.branchCode, self.accountNumber = self.get_information_bradesco()
            
            elif pytesseract.image_to_string(np.array(self.pages[0])[150:250,600:1300,:],config=r'--oem 3 --psm 7') == 'Extrato (Ultimos Lancamentos)':
            
                self.statement = self.output_bradescopj2(final_output)
                
                self.name, self.branchCode, self.accountNumber = self.get_information_bradesco()
            
            else:
                
                self.statement = self.output_bradesco(final_output)
                
                self.name, self.branchCode, self.accountNumber = self.get_information_bradesco()
            
        elif pdfbank == 'bradesco2':
            
            if pytesseract.image_to_string(np.array(self.pages[0])[150:250,600:1300,:],config=r'--oem 3 --psm 7') == 'Extrato Mensal / Por Periodo':
                
                self.statement = self.output_bradescopj2(final_output)
                
                self.name, self.branchCode, self.accountNumber = self.get_information_bradesco()
            
            else:
                
                self.statement = self.output_bradesco(final_output)
                
                self.name, self.branchCode, self.accountNumber = self.get_information_bradesco()
        
        elif pdfbank == 'ORIGINAL':
            
            self.statement = self.output_original(final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_original()
        
        elif pdfbank == 'ORIGINAL2':
            
            self.statement = self.output_original(final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_original()
            
        elif pdfbank == 'CAIXA':
            
            self.statement = self.output_caixa(final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_caixa()
        
        elif pdfbank == 'ItauEmpresas':
            
            self.statement = self.output_itau(final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_itau()
        
        elif pdfbank == 'ItadEmpresas':
            
            self.statement = self.output_itaupj2(final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_itaupj2()
        
        elif pdfbank == 'EMPRESA':
            
            self.statement = self.output_bancobrasil(final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_bb()
        
        elif pdfbank == 'SISBB - Sistema de Informag6es Banco do Brasil':
            
            self.statement = self.output_bancobrasilpj2(final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_bbpj2()
        
        elif pdfbank == 'Sicredi':
            
            self.statement = self.output_sicredi(final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_sicredi()
            
        elif pdfbank == 'Safra':
            
            self.statement = self.output_safra(final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_safra()
            
        else:
            
            self.statement = None
        
        #Adding Content
        
        self.statement['number'] = self.number
        
        self.statement['_id'] = self.file_id
        
        self.statement['name'] = self.name
        
        self.statement['branchCode'] = self.branchCode
        
        self.statement['accountNumber'] = self.accountNumber
        
        #loggin info
        self.logger.info('End of OCR transform. filename: ' + self.filename)
        
        return self.statement
        
    def return_document_picture(self,bank):
        
        if self.bank == 'inter':
            
            pagez = np.array(self.pages[0])[1170:-380,:,:]
            for i in np.arange(1,len(self.pages)):
                pagez = np.concatenate((pagez,np.array(self.pages[i])[340:-380,:,:]))
            # zeroing margins
            pagez[:,200:300,:] = 255
            pagez[:,2140:2500,:] = 255
            pagez[:,470:485,:] = 255
            pagez[:,1645:1680,:] = 255
            
            self.fullpicture = pagez
            
        elif self.bank == 'SICOOB':
            
            pagez = np.array(self.pages[0])[700:-110,:,:]
            for i in np.arange(1,len(self.pages)):
                pagez = np.concatenate((pagez,np.array(self.pages[i])[110:-110,:,:]))
                
            self.fullpicture = pagez
    
        elif self.bank == 'Santander':
            
            pagez = np.array(self.pages[0])[1020:-110,:,:]
            for i in np.arange(1,len(self.pages)):
                pagez = np.concatenate((pagez,np.array(self.pages[i])[110:-110,:,:]))
            
            self.fullpicture = pagez
            
        elif self.bank == 'bradesco' or self.bank == 'bradesco2':
            
            if pytesseract.image_to_string(np.array(self.pages[0])[150:230,600:1300,:],config=r'--oem 3 --psm 7') == 'Extrato Mensal / Por Periodo':
                
                pagez = np.array(self.pages[0])[900:-110,:,:]
                for i in np.arange(1,len(self.pages)):
                    pagez = np.concatenate((pagez,np.array(self.pages[i])[110:-110,:,:]))
                    
            elif pytesseract.image_to_string(np.array(self.pages[0])[150:250,600:1300,:],config=r'--oem 3 --psm 7') == 'Extrato Mensal / Por Periodo':
                
                pagez = np.array(self.pages[0])[900:-110,:,:]
                for i in np.arange(1,len(self.pages)):
                    pagez = np.concatenate((pagez,np.array(self.pages[i])[110:-110,:,:]))
                    
            else:
                
                pagez = np.array(self.pages[0])[836:-110,:,:]
                for i in np.arange(1,len(self.pages)):
                    pagez = np.concatenate((pagez,np.array(self.pages[i])[110:-110,:,:]))
            
            self.fullpicture = pagez
            
        elif self.bank == 'ORIGINAL':
            
            pagez = np.array(self.pages[0])[900:-110,:,:]
            for i in np.arange(1,len(self.pages)):
                pagez = np.concatenate((pagez,np.array(self.pages[i])[110:-110,:,:]))
            pagez[:,340:355,:] = 255
            pagez[:,2140:2155,:] = 255
            
            self.fullpicture = pagez
            
        elif self.bank == 'ORIGINAL2':
            
            pagez = np.array(self.pages[0])[900:-110,:,:]
            for i in np.arange(1,len(self.pages)):
                pagez = np.concatenate((pagez,np.array(self.pages[i])[110:-110,:,:]))
            pagez[:,200:250,:] = 255
            pagez[:,2240:2355,:] = 255
            
            self.fullpicture = pagez
            
        elif self.bank == 'CAIXA':
            
            pagez = np.array(self.pages[0])[1050:-100,:,:]
            for i in np.arange(1,len(self.pages)):
                pagez = np.concatenate((pagez,np.array(self.pages[i])[100:-100,:,:]))
            
            self.fullpicture = pagez
            
        elif self.bank == 'ItauEmpresas':
            
            pagez = np.array(self.pages[0])[2500:-100,500:2400,:]
            for i in np.arange(1,len(self.pages)):
                pagez = np.concatenate((pagez,np.array(self.pages[i])[440:-100,500:2400,:]))
            pagez[:,0:100,:] = 255
            self.fullpicture = pagez
            
        elif self.bank == 'ItadEmpresas':
            
            pagez = np.array(self.pages[0])[1000:-100,50:2400,:]
            for i in np.arange(1,len(self.pages)):
                pagez = np.concatenate((pagez,np.array(self.pages[i])[100:-100,50:2400,:]))
            
            self.fullpicture = pagez
            
        elif self.bank == 'EMPRESA':
            
            pagez = np.array(self.pages[0])[900:-110,:,:]
            for i in np.arange(1,len(self.pages)):
                pagez = np.concatenate((pagez,np.array(self.pages[i])[110:-110,:,:]))
            
            self.fullpicture = pagez
            
        elif self.bank == 'SISBB - Sistema de Informag6es Banco do Brasil':
            
            pagez = np.array(self.pages[0])[400:-110,:,:]
            for i in np.arange(1,len(self.pages)):
                pagez = np.concatenate((pagez,np.array(self.pages[i])[110:-110,:,:]))
                
            self.fullpicture = pagez
            
        elif self.bank == 'Sicredi':
            
            pagez = np.array(self.pages[0])[1550:-110,:,:]
            for i in np.arange(1,len(self.pages)):
                pagez = np.concatenate((pagez,np.array(self.pages[i])[110:-110,:,:]))
            
            # zeroing margins
            pagez[:,2000:2600,:] = 255
            pagez[:,50:200,:] = 255
            
            self.fullpicture = pagez
            
        elif self.bank == 'Safra':
            
            pagez = np.array(self.pages[0])[1070:-370,50:2500,:]
            for i in np.arange(1,len(self.pages)):
                pagez = np.concatenate((pagez,np.array(self.pages[i])[600:-370,50:2500,:]))
                
            self.fullpicture = pagez
            
        else:
            
            self.fullpicture = None