from pdf2image import convert_from_path
from unicodedata import normalize
from PyPDF2 import PdfFileReader
from datetime import datetime
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
import _stone
import _c6
import _bs2
import _neon
import _nubank

class bank_statement_ocr(_open_cv_stuff.Mixin,_bb.Mixin1,_bradesco.Mixin2,
                         _inter.Mixin3,_itau.Mixin4,_caixa.Mixin5,
                         _original.Mixin6,_santander.Mixin7,_sicoob.Mixin8,
                         _sicredi.Mixin9,_safra.Mixin10,_stone.Mixin11,
                         _c6.Mixin12,_bs2.Mixin13,_neon.Mixin14,_nubank.Mixin15):
    
    def __init__(self,filename,file_id=''):
        
        self.filenameWithPath = filename
        self.filename = filename.split('/')[-1]
        # Number o pages in the pdf
        self.pageNumber = self.countPages(filename)
        # transforming bank statement into a image
        # self.pages = convert_from_path(filename, 300) # uses too much memory on the server.
        #self.fullpicture = None
        self.final_output = None
        self.bank = None
        self.file_id = file_id
        self.statement = None
        self.name = None
        self.branchCode = None
        self.AccountNumber = None
        self.bankname = None
        #logging errors, infos etc.
        self.logger = logging.getLogger('OCR')
        self.hdlr = logging.FileHandler('./OCR.log')
        self.formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        self.hdlr.setFormatter(self.formatter)
        self.logger.addHandler(self.hdlr) 
        self.logger.setLevel(logging.INFO)
    
    def countPages(self,filename):
        
        try:
            return PdfFileReader(open(filename,'rb')).getNumPages()
        except:
            return 0
    
    def remover_acentos(self,txt):
        
        return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')
    
    def check_bank(self):
        
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
        
        logo = np.array(convert_from_path(self.filenameWithPath,first_page=1,last_page=1,dpi=300)[0])
        
        ocr_result = ''
        
        for bk in dict_logos.keys():
            
            x , h, y , w , result, result_dup = dict_logos[bk]
            
            try: 
                ocr_result = pytesseract.image_to_string(logo[x:h,y:w,:],config=r'--oem 3 --psm 7')
            except:
                ocr_result = None
                
            if ocr_result == result:
                
                return result_dup, bk
            
        return None
    
    # Here we work with OpenCV and Tesseract to transform the image into data.
    def process_document(self,bank):
        
        if self.bank == 'inter':
            
            final_output = []
            
            for i in np.arange(0,self.pageNumber):
                if i == 0:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[1170:-380,:,:]
                else:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[340:-380,:,:]
                # zeroing margins
                page[:,200:300,:] = 255
                page[:,2140:2500,:] = 255
                page[:,470:485,:] = 255
                page[:,1645:1680,:] = 255
                
                try:
                    final_output = final_output + self.do_opencv_stuff(page)
                except:
                    #Case pdf page is null
                    pass

            self.final_output = final_output
            
            self.statement = self.output_inter(self.final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_inter()
            
        elif self.bank == 'SICOOB':
            
            final_output = []
            
            for i in np.arange(0,self.pageNumber):
                if i == 0:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[700:-110,:,:]
                else:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[110:-110,:,:]
                
                try:
                    final_output = final_output + self.do_opencv_stuff(page)
                except:
                    #Case pdf page is null
                    pass
                
            self.final_output = final_output
            
            self.statement = self.output_sicoob(self.final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_sicoob()
        
        elif self.bank == 'SICOOB2':
            
            final_output = []
            
            for i in np.arange(0,self.pageNumber):
                if i == 0:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[1100:-110,:,:]
                else:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[110:-110,:,:]
                
                try:
                    final_output = final_output + self.do_opencv_stuff(page)
                except:
                    #Case pdf page is null
                    pass
                
            self.final_output = final_output
            
            self.statement = self.output_sicoobpj2(self.final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_sicoobpj2()
        
        elif self.bank == 'SICOOB3':
            
            final_output = []
            
            for i in np.arange(0,self.pageNumber):
                if i == 0:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[500:-110,150:2350,:]
                else:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[110:-110,150:2350,:]
                
                try:
                    final_output = final_output + self.do_opencv_stuff(page)
                except:
                    #Case pdf page is null
                    pass
                
            self.final_output = final_output
            
            self.statement = self.output_sicoob_pj3(self.final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_sicoob_pj3()
            
        elif self.bank == 'SICOOB4':
            
            final_output = []
            
            for i in np.arange(0,self.pageNumber):
                if i == 0:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[525:-10,380:2200,:]
                else:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[670:-10,380:2200,:]
                
                try:
                    final_output = final_output + self.do_opencv_stuff(page)
                except:
                    #Case pdf page is null
                    pass
                
            self.final_output = final_output
            
            self.statement = self.output_sicoob_pj4(self.final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_sicoob_pj4()
            
        elif self.bank == 'Santander':
            
            final_output = []
            
            for i in np.arange(0,self.pageNumber):
                if i == 0:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[1020:-110,:,:]
                else:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[110:-110,:,:]
                
                try:
                    final_output = final_output + self.do_opencv_stuff(page)
                except:
                    #Case pdf page is null
                    pass
            
            self.final_output = final_output
            
            self.statement = self.output_santander(self.final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_santander()

        elif self.bank == 'Santander2':
            
            final_output = []
            
            for i in np.arange(0,self.pageNumber):
                if i == 0:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[780:-110,:,:]
                else:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[110:-110,:,:]
                # zeroing margins
                page[:,200:300,:] = 255
                page[:,2255:2500,:] = 255
                
                try:
                    final_output = final_output + self.do_opencv_stuff(page)
                except:
                    #Case pdf page is null
                    pass
                
            self.final_output = final_output
            
            self.statement = self.output_santander(self.final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_santander2()
            
        elif self.bank == 'bradesco' or self.bank == 'bradesco2':
            
            final_output = []
            
            if pytesseract.image_to_string(np.array(convert_from_path(self.filenameWithPath,first_page=1,last_page=1,dpi=300)[0])[150:230,600:1300,:],config=r'--oem 3 --psm 7') == 'Extrato Mensal / Por Periodo':
                
                for i in np.arange(0,self.pageNumber):
                    if i == 0:
                        page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[900:-110,:,:]
                    else:
                        page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[110:-110,:,:]

                    try:
                        final_output = final_output + self.do_opencv_stuff(page)
                    except:
                        #Case pdf page is null
                        pass
                    
                    self.final_output = final_output
                    
                    self.statement = self.output_bradescopj2(self.final_output)
                
                    self.name, self.branchCode, self.accountNumber = self.get_information_bradesco()
                    
            elif pytesseract.image_to_string(np.array(convert_from_path(self.filenameWithPath,first_page=1,last_page=1,dpi=300)[0])[150:250,600:1300,:],config=r'--oem 3 --psm 7') == 'Extrato (Ultimos Lancamentos)':
                
                for i in np.arange(0,self.pageNumber):
                    if i == 0:
                        page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[900:-110,:,:]
                    else:
                        page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[110:-110,:,:]

                    try:
                        final_output = final_output + self.do_opencv_stuff(page)
                    except:
                        #Case pdf page is null
                        pass
                    
                    self.final_output = final_output
                    
                    self.statement = self.output_bradescopj2(self.final_output)
                
                    self.name, self.branchCode, self.accountNumber = self.get_information_bradesco()
            else:
                
                for i in np.arange(0,self.pageNumber):
                    if i == 0:
                        page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[836:-110,:,:]
                    else:
                        page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[110:-110,:,:]

                    try:
                        final_output = final_output + self.do_opencv_stuff(page)
                    except:
                        #Case pdf page is null
                        pass
                    
                    self.final_output = final_output
                    
                    self.statement = self.output_bradesco(self.final_output)
                
                    self.name, self.branchCode, self.accountNumber = self.get_information_bradesco()
                    
        elif self.bank == 'bradesco3':
            
            final_output = []
            
            for i in np.arange(0,self.pageNumber):
                if i == 0:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[560:-300,:,:]
                else:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[260:-300,:,:]
                
                try:
                    final_output = final_output + self.do_opencv_stuff(page)
                except:
                    #Case pdf page is null
                    pass
                
            self.final_output = final_output
            
            self.statement = self.output_bradescopj3(self.final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_bradesco_pj3()
            
        elif self.bank == 'ORIGINAL':
            
            final_output = []
            
            for i in np.arange(0,self.pageNumber):
                if i == 0:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[900:-110,:,:]
                else:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[110:-110,:,:]
                # zeroing margins
                page[:,340:355,:] = 255
                page[:,2140:2155,:] = 255
                
                try:
                    final_output = final_output + self.do_opencv_stuff(page)
                except:
                    #Case pdf page is null
                    pass
                
            self.final_output = final_output
            
            self.statement = self.output_original(self.final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_original()
            
        elif self.bank == 'ORIGINAL2':
            
            final_output = []
            
            for i in np.arange(0,self.pageNumber):
                if i == 0:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[900:-110,:,:]
                else:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[110:-110,:,:]
                # zeroing margins
                page[:,200:250,:] = 255
                page[:,2240:2355,:] = 255
                
                try:
                    final_output = final_output + self.do_opencv_stuff(page)
                except:
                    #Case pdf page is null
                    pass
                
            self.final_output = final_output
            
            self.statement = self.output_original(self.final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_original()
            
        elif self.bank == 'CAIXA':
            
            final_output = []
            
            for i in np.arange(0,self.pageNumber):
                if i == 0:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[1050:-100,:,:]
                else:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[100:-100,:,:]
                
                try:
                    final_output = final_output + self.do_opencv_stuff(page)
                except:
                    #Case pdf page is null
                    pass
            
            self.final_output = final_output
            
            self.statement = self.output_caixa(self.final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_caixa()
            
        elif self.bank == 'ItauEmpresas':
            
            final_output = []
            
            for i in np.arange(0,self.pageNumber):
                if i == 0:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[2500:-100,500:2400,:]
                else:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[440:-100,500:2400,:]
                # zeroing margins
                page[:,0:100,:] = 255
                
                try:
                    final_output = final_output + self.do_opencv_stuff(page)
                except:
                    #Case pdf page is null
                    pass
                
            self.final_output = final_output
            
            self.statement = self.output_itau(self.final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_itau()
            
        elif self.bank == 'ItadEmpresas':
            
            final_output = []
            
            for i in np.arange(0,self.pageNumber):
                if i == 0:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[1000:-100,50:2400,:]
                else:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[100:-100,50:2400,:]
                
                try:
                    final_output = final_output + self.do_opencv_stuff(page)
                except:
                    #Case pdf page is null
                    pass
            
            self.final_output = final_output
            
            self.statement = self.output_itaupj2(self.final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_itaupj2()
            
        elif self.bank == 'ItauEmpresas2':
            
            final_output = []
            
            for i in np.arange(0,self.pageNumber):
                if i == 0:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[1250:-100,450:2400,:]
                else:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[100:-100,450:2400,:]
                # zeroing margins
                page[:,:30,:] = 255
                
                try:
                    final_output = final_output + self.do_opencv_stuff(page)
                except:
                    #Case pdf page is null
                    pass
                
            self.final_output = final_output
            
            self.statement = self.output_itaupj3(self.final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_itaupj3()
            
        elif self.bank == 'ItauEmpresas4':
            
            final_output = []
            
            for i in np.arange(0,self.pageNumber):
                if i == 0:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[450:-50,:,:]
                else:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[230:-50,:,:]
                # zeroing margins
                page[:,:30,:] = 255
                
                try:
                    final_output = final_output + self.do_opencv_stuff(page)
                except:
                    #Case pdf page is null
                    pass
                
            self.final_output = final_output
            
            self.statement = self.output_itaupj4(self.final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_itaupj4()
            
        elif self.bank == 'EMPRESA':
            
            final_output = []
            
            for i in np.arange(0,self.pageNumber):
                if i == 0:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[900:-110,:,:]
                else:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[110:-110,:,:]
                
                try:
                    final_output = final_output + self.do_opencv_stuff(page)
                except:
                    #Case pdf page is null
                    pass
            
            self.final_output = final_output
            
            self.statement = self.output_bancobrasil(self.final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_bb()
            
        elif 'SISBB' in self.bank:
            
            final_output = []
            
            for i in np.arange(0,self.pageNumber):
                if i == 0:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[400:-110,:,:]
                else:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[110:-110,:,:]
                
                try:
                    final_output = final_output + self.do_opencv_stuff(page)
                except:
                    #Case pdf page is null
                    pass
            
            self.final_output = final_output
            
            self.statement = self.output_bancobrasilpj2(self.final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_bbpj2()
            
        elif self.bank == 'Sicredi':
            
            final_output = []
            
            for i in np.arange(0,self.pageNumber):
                if i == 0:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[1550:-110,:,:]
                else:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[110:-110,:,:]
                # zeroing margins
                page[:,2000:2600,:] = 255
                page[:,50:200,:] = 255
                
                try:
                    final_output = final_output + self.do_opencv_stuff(page)
                except:
                    #Case pdf page is null
                    pass
                
            self.final_output = final_output
            
            self.statement = self.output_sicredi(self.final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_sicredi()
            
        elif self.bank == 'Safra':
            
            final_output = []
            
            for i in np.arange(0,self.pageNumber):
                if i == 0:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[1070:-370,50:2500,:]
                else:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[600:-370,50:2500,:]
                
                try:
                    final_output = final_output + self.do_opencv_stuff(page)
                except:
                    #Case pdf page is null
                    pass
            
            self.final_output = final_output
            
            self.statement = self.output_safra(self.final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_safra()
            
        elif self.bank == 'stone':
            
            final_output = []
            
            for i in np.arange(0,self.pageNumber):
                if i == 0:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[850:-100,:,:]
                else:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[250:-100,:,:]
                
                try:
                    final_output = final_output + self.do_opencv_stuff(page)
                except:
                    #Case pdf page is null
                    pass
            
            self.final_output = final_output
            
            self.statement = self.output_stone(self.final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_stone()
            
        elif self.bank == 'C6BANK':
            
            final_output = []
            
            for i in np.arange(0,self.pageNumber):
                if i == 0:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[1000:-500,:,:]
                else:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[670:-500,:,:]
                
                try:
                    for i in range(page.shape[0]):
                        for j in range(page.shape[1]):
                            if page[i,j,0] == 192 and page[i,j,1] == 192 and page[i,j,2] == 192:
                                page[i,j,0] = 255
                                page[i,j,1] = 255
                                page[i,j,2] = 255
                                
                    final_output = final_output + self.do_opencv_stuff(page)
                except:
                    #Case pdf page is null
                    pass
            
            self.final_output = final_output
            
            self.statement = self.output_c6(self.final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_c6()
            
        elif self.bank == 'bs2':
            
            final_output = []
            
            for i in np.arange(0,self.pageNumber):
                if i == 0:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[650:-630,:,:]
                else:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[150:-630,:,:]
                
                try:
                    for i in range(page.shape[0]):
                        for j in range(page.shape[1]):
                            if page[i,j,0] == 192 and page[i,j,1] == 192 and page[i,j,2] == 192:
                                page[i,j,0] = 255
                                page[i,j,1] = 255
                                page[i,j,2] = 255
                                
                    final_output = final_output + self.do_opencv_stuff(page)
                except:
                    #Case pdf page is null
                    pass
            
            self.final_output = final_output
            
            self.statement = self.output_bs2(self.final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_bs2()
            
        elif self.bank == 'NEON':
            
            final_output = []
            
            for i in np.arange(0,self.pageNumber):
                if i == 0:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[800:-50,90:-90,:]
                else:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[55:-50,90:-90,:]
                
                try:
                    
                    page = self.neon_process_page(page)
                    
                    final_output = final_output + self.do_opencv_stuff(page)
                except:
                    #Case pdf page is null
                    pass
            
            self.final_output = final_output
            
            self.statement = self.output_neon(self.final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_neon()
            
        elif self.bank == 'nubank':
            
            final_output = []
            
            for i in np.arange(0,self.pageNumber):
                
                if i == 0:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[400:-50,:,:]
                else:
                    page = np.array(convert_from_path(self.filenameWithPath,first_page=i+1,last_page=i+1,dpi=300)[0])[600:-50,:,:]
                
                try:
                    
                    final_output = final_output + self.do_opencv_stuff(page)
                    
                except Exception as e:
                    #Case pdf page is null
                    pass
            
            self.final_output = final_output
            
            self.statement = self.output_nubank(self.final_output)
            
            self.name, self.branchCode, self.accountNumber = self.get_information_nubank()
            
        else:
            
            self.final_output = None
            
    # Actual text Processing Analysis.
    def start_analysis(self):
        
        self.logger.info('OCR starting for filename: ' + self.filename)
        
        pdfbank, bankname = self.check_bank()
        
        self.bankname = bankname
        
        final_output = ''
        
        if pdfbank is None:
            self.logger.error("OCR couldn`t find bank name on the statement. Filename:" + self.filename)
            self.statement = {'Error': "OCR couldn`t find bank name on the statement."}
        else:
            self.bank = pdfbank
            # udpate classe picture of pages 
            self.process_document(pdfbank)

            if self.pageNumber == 0 or self.pageNumber is None:
                
                self.logger.error("Couldn`t transform PDF to image. Filename:" + self.filename)
                self.statement = {'Error' : "Couldn`t transform PDF to image."}
                
            elif len(self.final_output) == 0 or self.final_output is None:
                
                self.logger.error("Couldn`t transform Image to Character Array. Filename:" + self.filename)
                self.statement = {'Error' : "Couldn`t transform Image to Character Array."}
                
            elif self.statement is None:
                
                self.logger.error("Processing Statement Error.. Filename:" + self.filename)
                self.statement = {'Error' : "Processing Statement Error."}
            
        #Adding Content
            
        try:    
            self.statement['_id'] = self.file_id
        except:
            self.logger.error("No Number on _id:" + self.filename)
            
        try:    
            self.statement['name'] = str(self.name)
        except:
            self.logger.error("No Name on Filename:" + self.filename)
            
        try:    
            self.statement['branchCode'] = self.branchCode
        except:
            self.logger.error("No BranchCode on Filename:" + self.filename)
            
        try:    
            self.statement['accountNumber'] = self.accountNumber
        except:
            self.logger.error("No accountNumber on Filename:" + self.filename)
            
        try:
            self.statement['filename'] = self.filename
        except:
            self.logger.error("No filename on Filename:" + self.filename)
            
        try:
            self.statement['bankname'] = self.bankname
        except:
            self.statement['bankname'] = 'No Bank Found'
            self.logger.error("No bankname found on Filename:" + self.filename)
            
        #loggin info
        self.logger.info('End of OCR transform. filename: ' + self.filename)
        
        return self.statement