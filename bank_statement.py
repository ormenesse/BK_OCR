from pdf2image import convert_from_path
from unicodedata import normalize
import matplotlib.pyplot as plt
from imutils import contours
import pytesseract
import numpy as np
import operator
import datetime
import imutils
import json
import cv2
import re
import gc


class bank_statement_ocr:
    
    def __init__(self,filename):
        
        self.filename = filename
        # transforming bank statement into a image
        self.pages = convert_from_path(filename, 300)
        self.fullpicture = None
        self.bank = None
    
    def remover_acentos(self,txt):
        
        return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')
    
    def check_bank(self):
        
        dict_logos = {
            'inter' : (300,500,200,650,'inter'),
            'sicoob' : (150,200,1100,1400,'SICOOB'),
            'santander' : (180,270,220,490,'Santander'),
            'bradesco' : (180,400,300,550,'bradesco'),
            'original' : (380,470,1830,2120,'ORIGINAL'),
            'caixa' : (150,300,100,600,'CAIXA'),
            'itau' : (50,230,2000,2400,'ItauEmpresas'),
            'bb' : (300,350,250,450,'EMPRESA')
        }
        
        logo = np.array(self.pages[0])
        
        ocr_result = ''
        
        for bk in dict_logos.keys():
            
            x , h, y , w , result = dict_logos[bk]
            
            ocr_result = pytesseract.image_to_string(logo[x:h,y:w,:],config=r'--oem 3 --psm 7')
            
            if ocr_result == result:
                
                return ocr_result
            
        return None
    
    def start_analysis(self):
        
        pdfbank = self.check_bank()
        
        if pdfbank is None:
            return '{Error: "OCR couldn`t find bank name on the statement."}'
        else:
            self.bank = pdfbank
        # udpate classe picture of pages 
        self.return_document_picture(pdfbank)
        
        if self.fullpicture is None:
            return '{Error : "Couldn`t transform PDF to image."}'
        
        # getting output
        final_output = self.do_opencv_stuff()
        
        # parsing output
        if pdfbank == 'inter':
            
            return self.output_inter(final_output)
        
        elif pdfbank == 'SICOOB':
            
            return self.output_sicoob(final_output)
        
        elif pdfbank == 'Santander':
            
            return self.output_santander(final_output)
        
        elif pdfbank == 'bradesco':
            
            return self.output_bradesco(final_output)
        
        elif pdfbank == 'ORIGINAL':
            
            return self.output_original(final_output)
        
        elif pdfbank == 'CAIXA':
            
            return self.output_caixa(final_output)
        
        elif pdfbank == 'ItauEmpresas':
            
            return self.output_itau(final_output)
        
        elif pdfbank == 'EMPRESA':
            
            return self.output_bancobrasil(final_output)
        
        
    def return_document_picture(self,bank):
        
        if self.bank == 'inter':
            
            pagez = np.array(self.pages[0])[1170:-380,:,:]
            for i in np.arange(1,len(self.pages)):
                pagez = np.concatenate((pagez,np.array(pages[i])[340:-380,:,:]))
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
            
        elif self.bank == 'bradesco':
            
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
            
        elif self.bank == 'EMPRESA':
            
            pagez = np.array(self.pages[0])[900:-110,:,:]
            for i in np.arange(1,len(self.pages)):
                pagez = np.concatenate((pagez,np.array(self.pages[i])[110:-110,:,:]))
            
            self.fullpicture = pagez
            
        else:
            
            self.fullpicture = None
        
    def do_opencv_stuff(self):
        
        #turn my page into gray
        gray = cv2.cvtColor(self.fullpicture, cv2.COLOR_RGB2GRAY)
        #inverting black and white
        _ , binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        #intializing some structures
        rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 2)) #key structure
        sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)) # key structure
        # apply a tophat (whitehat) morphological operator to find light
        # regions against a dark background (i.e., the credit card numbers)
        tophat = cv2.morphologyEx(binary, cv2.MORPH_TOPHAT, rectKernel)
        # compute the Scharr gradient of the tophat image, then scale
        # the rest back into the range [0, 255]
        gradX = cv2.Sobel(tophat, ddepth=cv2.CV_32F, dx=1, dy=0,ksize=-1)
        gradX = np.absolute(gradX)
        (minVal, maxVal) = (np.min(gradX), np.max(gradX))
        gradX = (255 * ((gradX - minVal) / (maxVal - minVal)))
        gradX = gradX.astype("uint8")
        # apply a closing operation using the rectangular kernel to help
        # cloes gaps in between credit card number digits, then apply
        # Otsu's thresholding method to binarize the image
        gradX = cv2.morphologyEx(gradX, cv2.MORPH_CLOSE, rectKernel)
        thresh = cv2.threshold(gradX, 0, 255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        # apply a second closing operation to the binary image, again
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, sqKernel)
        # find contours in the thresholded image, then initialize the
        # list of digit locations
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        locs = []

        #here I will choose wich contour I will use
        # loop over the contours
        for (i, c) in enumerate(cnts):
            # compute the bounding box of the contour, then use the
            # bounding box coordinates to derive the aspect ratio
            (x, y, w, h) = cv2.boundingRect(c)

            #working only with minimum size squares
            if w > 20 and h > 20 :
                # append the bounding box region of the digits group
                # to our locations list
                locs.append((x, y, w, h))

        # making a copy of the final result
        copylocs = locs.copy()
        # most contours are not in a rounded pixel, here I am trying to make every line countour stay together\
        # I need the countours to be aligned in orther to put everything in the exact place in my future csv, txt.
        locs = []
        for i in np.arange(0,len(copylocs)):
            x = int(np.round(copylocs[i][0]/10)*10)
            y = int(np.round(copylocs[i][1]/10)*10)
            w = int(np.round(copylocs[i][2]/10)*10)
            h = int(np.round(copylocs[i][3]/10)*10)
            locs.append((x, y, w, h))
        # sort the square locations 
        locs = sorted(locs, key=operator.itemgetter(1, 0))
        # diff to find the lines.
        diff= []
        for i in np.arange(0,len(locs)-1):
            # number 6 is just a threshold I decided 
            if locs[i+1][1]-locs[i][1] > 6:
                diff.append((locs[i+1][1]-locs[i][1]))
        # average line space
        linespace = int(np.mean(diff))
        linestd = int(np.std(diff)/2)
        #Apply TESSERACT in the image - it works really well when set for straight line.
        final_output = []
        output = ''
        support_string = []
        y = locs[0][1]
        
        threshold = linespace-linestd
        if self.bank == 'inter':
            threshold = linespace+linestd
        
        for location in locs:
            output_text = pytesseract.image_to_string(self.fullpicture[location[1]-10:location[1]+7+location[3],
                                                      location[0]-12:location[0]+15+location[2],:],lang='por',
                                                      config=r'--oem 3 --psm 7')
            #looking for almost the same line
            if np.abs(location[1] - y) < threshold:
                support_string.append((location[0],output_text))
            else:
                y = location[1]
                support_string = sorted(support_string,key=lambda x: x[0])
                for (x,string) in support_string:
                    output = output + string + ';'
                support_string = [(location[0],output_text)]
                output = output + '\n'
        #final output
        final_output = output.split('\n')
        
        return final_output
    
    # Returning Output into a JSON method
    
    def output_inter(self,final_output):
        
        # to json
        amounts = []
        balance = []
        for i,line in enumerate(final_output):
            try:
                splt_line = line.split(';')

                adict = {}

                factor = 1
                if '-' in splt_line[-3]:
                    factor = -1

                adict['transaction'] = {
                    'date'   : datetime.datetime.strptime(splt_line[0], "%d/%m/%Y").strftime("%Y-%m-%d"),
                    'source' : self.remover_acentos(line[  : len(line)-len(''.join(splt_line[-3:])) ].replace(';',' ')),
                    'type'   : ['CREDITO' if factor == 1 else 'DEBITO'][0],
                    'amount' : factor*float(re.findall('\d+\.\d+',splt_line[-3].replace('.','').replace(',','.'))[0])
                }
                amounts.append(adict)

                if '-' in splt_line[-2]:
                    factor = -1

                day = {}
                day['day'] = {
                        'date'   : datetime.datetime.strptime(splt_line[0], "%d/%m/%Y").strftime("%Y-%m-%d"),
                        'amount' : factor*np.round(float(''.join(re.findall('[\-\d+]',splt_line[-2])))/100,2)
                }
                balance.append(day)
            except:
                pass

        extrato = {}
        extrato['bank_statement'] = amounts
        extrato['balance'] = balance
        
        return extrato
    
    def output_bradesco(self,final_output):
        
        # to json
        amounts = []

        for i,line in enumerate(final_output):
            splt_line = line.split(';')
            if len(splt_line) > 4:
                adict = {}

                factor = 1
                if '-' in splt_line[-2]:
                    factor = -1

                str_date = splt_line[0][:10]

                adict['transaction'] = {
                    'date'   : datetime.datetime.strptime(str_date, "%d/%m/%Y").strftime("%Y-%m-%d"),
                    'source' : self.remover_acentos(line[ 10 : len(line)-len(''.join(splt_line[-2:])) ].replace(';',' ')),
                    'type'   : ['CREDITO' if factor == 1 else 'DEBITO'][0],
                    'amount' : factor*float(re.findall('\d+\.\d+',splt_line[-2].replace('.','').replace(',','.'))[0])
                }
                amounts.append(adict)

        extrato = {}
        extrato['bank_statement'] = amounts
        
        return extrato
    
    def output_caixa(self,final_output):
        
        # to json
        amounts = []
        balance = []
        for i,line in enumerate(final_output):
            try:
                line.replace('€','C')
                splt_line = line.split(';')

                adict = {}

                factor = 1
                if 'D' in splt_line[-3]:
                    factor = -1

                adict['transaction'] = {
                    'date'   : datetime.datetime.strptime(splt_line[0], "%d/%m/%Y").strftime("%Y-%m-%d"),
                    'source' : self.remover_acentos(line[ 10 : len(line)-len(''.join(splt_line[-3:])) ].replace(';',' ')),
                    'type'   : ['CREDITO' if factor == 1 else 'DEBITO'][0],
                    'amount' : factor*float(re.findall('\d+\.\d+',splt_line[-3].replace('.','').replace(',','.'))[0])
                }
                amounts.append(adict)

                if 'D' in splt_line[-2]:
                    factor = -1

                day = {}
                day['day'] = {
                        'date'   : datetime.datetime.strptime(splt_line[0], "%d/%m/%Y").strftime("%Y-%m-%d"),
                        'amount' : factor*np.round(float(''.join(re.findall('[\-\d+]',splt_line[-2])))/100,2)
                }
                balance.append(day)
            except:
                pass

        extrato = {}
        extrato['bank_statement'] = amounts
        extrato['balance'] = balance
        
        return extrato
    
    def output_bancobrasil(self,final_output):
        
        splited = []
        for line in final_output[:-9]:
            splited.append(len(line.split(';')))
            
        # organizing document
        final_array = []
        for i,n in enumerate(splited):
            if n == 2:
                string = final_array.pop()
                string = string.split(';')
                string[2] = string[2] + ' ' + final_output[i].split(';')[0]
                final_array.append(';'.join(string))
            elif n == 6:
                line = final_output[i].split(';')
                line[2] = line[2]+' '+line[3]
                line[3] = line[4]
                line[4] = ''
                final_array.append(';'.join(line[:4]))
            else:
                final_array.append(';'.join(final_output[i].split(';')[:4]))
         
        # to json
        amounts = []
        balance = []
        for line in final_array:

            line.replace('€','C')

            splt_line = line.split(';')
            adict = {}

            check_if_balance = re.findall('[0-9\.]{1,20}\,\d+[\sC|\sD|C|D]{1,2}',splt_line[3])
            check_if_balance = [x.replace('.','').replace(',','.') for x in check_if_balance]

            if len(check_if_balance) == 2:
                day = {}
                factor = 1
                if 'D' in check_if_balance[1]:
                    factor = -1
                day['day'] = {
                        'date' : datetime.datetime.strptime(splt_line[0], "%d/%m/%Y").strftime("%Y-%m-%d"),
                        'amount' : factor*float(re.findall('\d+\.\d+',check_if_balance[1])[0])
                }
                balance.append(day)

            factor = 1
            if 'D' in check_if_balance[0]:
                factor = -1

            adict['transaction'] = {
                'date'   : datetime.datetime.strptime(splt_line[0], "%d/%m/%Y").strftime("%Y-%m-%d"),
                'source' : self.remover_acentos(splt_line[1]+ ' ' + splt_line[2]),
                'type'   : ['CREDITO' if 'D' not in check_if_balance[0] else 'DEBITO'][0],
                'amount' : factor*float(re.findall('\d+\.\d+',check_if_balance[0])[0])
            }
            if 'SALDO' not in adict['transaction']['source']:
                amounts.append(adict)

        extrato = {}
        extrato['bank_statement'] = amounts
        extrato['balance'] = balance
        
        return extrato
    
    def output_itau(self,final_output):
        
        final_line = len(final_output)
        for i,line in enumerate(final_output):
            if 'Saldo final' in line:
                final_line = i
                break
                
        final_output = final_output[:final_line+1]
        
        final_array = re.split('([0-3][0-9]\/(0[1-9]|1[012]))', ''.join(final_output),0,1)[1:]
        
        # Here I try to find the year of the balance document.
        try:
            year = '20' + re.findall('\d{2}\/\d{2}\/\d{2}',pytesseract.image_to_string(logo[1340:1390,1700:2300,:],config=r'--oem 3 --psm 7'))[0][-2:]
        except:
            year = str(datetime.datetime.now().year)
        
        # to json
        amounts = []
        balance = []
        for i in np.arange(2,len(final_array),3):

            log_day = final_array[i-2] + '/' + year
            line = self.remover_acentos(final_array[i])
            #for balance
            if 'Saldo anterior' in line:

                line = final_array[i].replace(';',' ')

                factor = 1
                if '-' in line_saldo:
                    factor = -1

                day = {}
                day['day'] = {
                    'date' : datetime.datetime.strptime(log_day, "%d/%m/%Y").strftime("%Y-%m-%d"),
                    'amount' : factor*float(re.findall('\d+\.\d+',line.replace(',','.'))[0])
                }
                balance.append(day)

            else:

                line_saldo = line.split(';')[-2]

                factor = 1
                if '-' in line_saldo:
                    factor = -1

                day = {}
                day['day'] = {
                    'date' : datetime.datetime.strptime(log_day, "%d/%m/%Y").strftime("%Y-%m-%d"),
                    'amount' : factor*float(re.findall('\d+\.\d+',line_saldo.replace('.','').replace(',','.'))[0])
                }
                balance.append(day)

                # removing what I don`t want
                #print(' | '.join(line.replace('.','').replace(',','.').split(';')[1:-2]))

                for sub_line in re.findall( '([^\|]+\|\s\d+\.\d+(-|))' ,  ' | '.join(line.replace('.','').replace(',','.').split(';')[1:-2]) ):

                    sub_line = sub_line[0]

                    if 'Saldo' not in sub_line:

                        money = re.findall('\d+\.\d+.+',sub_line)[0]

                        factor = 1

                        if '-' in money:
                            factor=-1

                        try:
                            adict = {}

                            adict['transaction'] = {
                                'date'   : datetime.datetime.strptime(log_day, "%d/%m/%Y").strftime("%Y-%m-%d"),
                                'source' : re.sub('\|\s+\d+\.\d+[-\s]', '', sub_line),
                                'type'   : ['CREDITO' if factor == 1 else 'DEBITO'][0],
                                'amount' : factor*float(re.findall('\d+\.\d+',money)[0])
                            }
                            amounts.append(adict)
                        except Exception as e:
                            print(log_day,money, sub_line, e)
                            #pass

        extrato = {}
        extrato['bank_statement'] = amounts
        extrato['balance'] = balance
        
        return extrato
    
    def output_original(self,final_output):
        
        splited = []
        for line in final_output[:-6]:
            splited.append(len(line.split(';')))
            
        # organizing document
        final_array = []
        for i,n in enumerate(splited):
            if n == 2:
                string = final_array.pop()
                string = string.split(';')
                string[1] = string[1] + ' ' + final_output[i].split(';')[0]
                final_array.append(';'.join(string))
            elif n == 3 and 'Saldo' not in final_output[i]:
                string = final_array.pop()
                string = string.split(';')
                string[1] = string[1] + ' ' + final_output[i].split(';')[0]
                final_array.append(';'.join(string))
            else:
                final_array.append(final_output[i])
        
        
        # to json
        amounts = []
        balance = []
        for line in final_array:
            splt_line = line.split(';')
            adict = {}
            if len(splt_line) == 3:
                day = {}
                day['day'] = {
                    'date' : datetime.datetime.strptime(splt_line[0], "%d/%m/%Y").strftime("%Y-%m-%d"),
                    'amount' : float(re.findall('\d+\.\d+',splt_line[1].replace(',','.'))[0])
                }
                balance.append(day)
            elif len(splt_line) == 5:
                factor = 1
                if '-' in splt_line[3]:
                    factor = -1

                adict['transaction'] = {
                    'date'   : datetime.datetime.strptime(splt_line[0], "%d/%m/%Y").strftime("%Y-%m-%d"),
                    'source' : self.remover_acentos(splt_line[1]),
                    'type'   : self.remover_acentos(splt_line[2]),
                    'amount' : factor*float(re.findall('\d+\.\d+',splt_line[3].replace(',','.'))[0])
                }
                amounts.append(adict)

        extrato = {}
        extrato['bank_statement'] = amounts
        extrato['balance'] = balance
        
        return extrato
    
    def output_santander(self,final_output):
        
        # to json
        amounts = []
        balance = []
        for line in final_output:
            splt_line = line.split(';')
            adict = {}
            try:
                if len(splt_line) == 6:
                    day = {}
                    day['day'] = {
                            'date'   : datetime.datetime.strptime(splt_line[0], "%d/%m/%Y").strftime("%Y-%m-%d"),
                            'amount' : np.round(float(''.join(re.findall('[\-\d+]',splt_line[4])))/100,2)
                    }
                    adict['transaction'] = {
                        'date'   : datetime.datetime.strptime(splt_line[0], "%d/%m/%Y").strftime("%Y-%m-%d"),
                        'source' : self.remover_acentos(splt_line[1]),
                        'type'   : ['CREDITO' if '-' not in splt_line[3] else 'DEBITO'][0],
                        'amount' : np.round(float(''.join(re.findall('[\-\d+]',splt_line[3])))/100,2)
                    }
                    balance.append(day)
                    amounts.append(adict)
                elif len(splt_line) == 5:

                    adict[datetime.datetime.strptime(splt_line[0], "%d/%m/%Y").strftime("%Y-%m-%d")] = {
                        'source' : self.remover_acentos(splt_line[1]),
                        'type'   : ['CREDITO' if '-' not in splt_line[3] else 'DEBITO'][0],
                        'amount' : np.round(float(''.join(re.findall('[\-\d+]',splt_line[3])))/100,2)
                    }
                    amounts.append(adict)
            except:
                pass

        extrato = {}
        extrato['bank_statement'] = amounts
        extrato['balance'] = balance
        
        return extrato
    
    def output_sicoob(self,final_output):
        
        final_array = re.split('(\d+\/\d+)', ''.join(final_output[:-9]))[1:]
        
        # Here I try to find the year of the balance document.
        try:
            year = re.findall('\d{4}',pytesseract.image_to_string(logo[500:580,450:1100,:],config=r'--oem 3 --psm 7'))[0]
        except:
            year = str(datetime.datetime.now().year)
        
        # to json
        amounts = []
        balance = []
        for i in np.arange(1,len(final_array),2):

            log_day = final_array[i-1] + '/' + year

            line = self.remover_acentos(final_array[i].replace(';',' '))

            #for balance
            if 'SALDO ANTERIOR' in line:

                line_saldo = re.findall('(SALDO\sANTERIOR\s+\d+.\d+(Cc|C|D|\s+D|\s+C))',line.replace('.','').replace(',','.'))[0][0]

                factor = 1
                if 'D' in line_saldo:
                    factor = -1

                day = {}
                day['day'] = {
                    'date' : datetime.datetime.strptime(log_day, "%d/%m/%Y").strftime("%Y-%m-%d"),
                    'amount' : factor*float(re.findall('\d+\.\d+',line_saldo.replace(',','.'))[0])
                }
                balance.append(day)

            elif 'SALDO DO DIA' in line:

                line_saldo = re.findall('(SALDO\sDO\sDIA\s+\d+.\d+(Cc|C|D|\s+D|\s+C))',line.replace('.','').replace(',','.'))[0][0]

                factor = 1
                if 'D' in line_saldo:
                    factor = -1

                day = {}
                day['day'] = {
                    'date' : datetime.datetime.strptime(log_day, "%d/%m/%Y").strftime("%Y-%m-%d"),
                    'amount' : factor*float(re.findall('\d+\.\d+',line_saldo.replace(',','.'))[0])
                }
                balance.append(day)

                # removing what I don`t want
                line = re.sub('(SALDO\sDO\sDIA\s+\d+.\d+(Cc|C|D|\s+D|\s+C))', '', line.replace('.','').replace(',','.'))

                fator = 1

                if 'D' in line:
                    factor=-1

                try:
                    adict = {}

                    adict['transaction'] = {
                        'date'   : datetime.datetime.strptime(log_day, "%d/%m/%Y").strftime("%Y-%m-%d"),
                        'source' : re.sub('(SALDO\sDO\sDIA\s+\d+.\d+(Cc|C|D|\s+D|\s+C))', '', line),
                        'type'   : ['CREDITO' if factor == 1 else 'DEBITO'][0],
                        'amount' : factor*float(re.findall('\d+\.\d+',line)[0])
                    }
                    amounts.append(adict)
                except:
                    pass

            else:

                line = line.replace('.','').replace(',','.')

                fator = 1

                if 'D' in line:
                    factor=-1

                try:
                    adict = {}

                    adict['transaction'] = {
                        'date'   : datetime.datetime.strptime(log_day, "%d/%m/%Y").strftime("%Y-%m-%d"),
                        'source' : re.sub('(\s+\d+.\d+(Cc|C|D|\s+D|\s+C))', '', line),
                        'type'   : ['CREDITO' if factor == 1 else 'DEBITO'][0],
                        'amount' : factor*float(re.findall('\d+\.\d+',line)[0])
                    }
                    amounts.append(adict)
                except:
                    pass

        extrato = {}
        extrato['bank_statement'] = amounts
        extrato['balance'] = balance
        
        return extrato
        
    
