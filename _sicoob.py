from import_libs import *

class Mixin8:
    
    def output_sicoob(self,final_output):

        logo = np.array(self.pages[0])
        # Here I try to find the year of the balance document.
        try:
            year = re.findall('\d{4}',pytesseract.image_to_string(logo[500:580,450:1100,:],config=r'--oem 3 --psm 7'))[0]
        except:
            year = str(datetime.datetime.now().year)
        
        # dividing cells correctly
        final_array = re.split('([0-3][0-9]\/(0[1-9]|1[012]))', ''.join(final_output),0,1)[1:]

        # to json
        amounts = []
        balance = []

        for i in np.arange(2,len(final_array),3):
            
            log_day = final_array[i-2] + '/' + year
            line = self.remover_acentos(final_array[i])
            line = line.replace('€','C')
            
            #for balance
            if 'SALDO ANTERIOR' in line:
                try:
                    line = final_array[i].replace(';',' ')

                    money = re.findall('\d+\.\d+[\sC|\sCc|\sD|C|D]{1,2}',line.replace('.','').replace(',','.'))[0]

                    factor = 1
                    if 'D' in money:
                        factor = -1

                    day = {}
                    day['day'] = {
                        'date' : datetime.datetime.strptime(log_day, "%d/%m/%Y").strftime("%Y-%m-%d"),
                        'amount' : factor*float(re.findall('\d+\.\d+',money)[0])
                    }
                    balance.append(day)
                except:
                    exc_type, exc_obj, tb = sys.exc_info()
                    f = tb.tb_frame
                    lineno = tb.tb_lineno
                    filename = f.f_code.co_filename
                    linecache.checkcache(filename)
                    iline = linecache.getline(filename, lineno, f.f_globals)
                    error = ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, iline.strip(), exc_obj))
                    self.logger.error(error + ' on the line' + line)
            
            elif 'BLOQ.ANTERIOR' in line:
                # Here, I don`t wanna do anything with this line.
                pass
            
            elif 'SALDO DO DIA' in line:
                try:
                    
                    line = final_array[i].replace(';',' ') 

                    return_day_money = re.findall('SALDO DO DIA \d+\.\d+[\sC|\sCc|\sD|C|D]{1,2}',line.replace(';',' ').replace('.','').replace(',','.'))[0]
                    
                    day_money = re.findall('\d+\.\d+[\sC|\sCc|\sD|C|D]{1,2}',return_day_money)[0]

                    factor = 1
                    if 'D' in day_money:
                        factor = -1

                    day = {}
                    day['day'] = {
                        'date' : datetime.datetime.strptime(log_day, "%d/%m/%Y").strftime("%Y-%m-%d"),
                        'amount' : factor*float(re.findall('\d+\.\d+',day_money)[0])
                    }
                    balance.append(day)

                    # looking for amounts

                    line = re.sub('SALDO DO DIA \d+\.\d+[\sC|\sCc|\sD|C|D]{1,2}', '', line.replace('.','').replace(',','.'))

                    if 'RESUMO SALDO' in line:
                        line = re.sub('RESUMO SALDO.+' , '', line)

                    day_money = re.findall('\d+\.\d+[\sC|\sCc|\sD|C|D]{1,2}',line)[0]
                    
                    factor = 1
                    if 'D' in day_money:
                        factor = -1
                    
                
                    adict = {}

                    adict['transaction'] = {
                        'date'   : datetime.datetime.strptime(log_day, "%d/%m/%Y").strftime("%Y-%m-%d"),
                        'source' : line,
                        'type'   : ['CREDITO' if factor == 1 else 'DEBITO'][0],
                        'amount' : factor*float(re.findall('\d+\.\d+',day_money)[0])
                    }
                    amounts.append(adict)
                except Exception as e:
                    exc_type, exc_obj, tb = sys.exc_info()
                    f = tb.tb_frame
                    lineno = tb.tb_lineno
                    filename = f.f_code.co_filename
                    linecache.checkcache(filename)
                    iline = linecache.getline(filename, lineno, f.f_globals)
                    error = ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, iline.strip(), exc_obj))
                    self.logger.error(error + ' on the line' + line)
            
            else:
                try:
                    
                    line = final_array[i].replace(';',' ') 

                    line = line.replace('.','').replace(',','.')

                    day_money = re.findall('\d+\.\d+[\sC|\sCc|\sD|C|D]{1,2}',line)[0]
                    
                    factor = 1
                    if 'D' in day_money:
                        factor = -1
                        
                    adict = {}

                    adict['transaction'] = {
                        'date'   : datetime.datetime.strptime(log_day, "%d/%m/%Y").strftime("%Y-%m-%d"),
                        'source' : re.sub('\d+\.\d+[\sC|\sCc|\sD|C|D]{1,2}' , '', line),
                        'type'   : ['CREDITO' if factor == 1 else 'DEBITO'][0],
                        'amount' : factor*float(re.findall('\d+\.\d+',day_money)[0])
                    }
                    amounts.append(adict)
                except Exception as e:
                    exc_type, exc_obj, tb = sys.exc_info()
                    f = tb.tb_frame
                    lineno = tb.tb_lineno
                    filename = f.f_code.co_filename
                    linecache.checkcache(filename)
                    iline = linecache.getline(filename, lineno, f.f_globals)
                    error = ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, iline.strip(), exc_obj))
                    self.logger.error(error + ' on the line' + line)

                
        extrato = {}
        extrato['bank_statement'] = amounts
        extrato['balance'] = balance

        return extrato
    
    def output_sicoob(self,final_output):
        
        return {}
    
    def get_information_sicoob(self):
        
        pagez = np.array(self.pages[0])[400:600,400:2000,:]
        final_output = self.do_opencv_partially(pagez)
        name = ''
        branchCode = ''
        accountNumber = ''
        for line in final_output:
            line = self.remover_acentos(line.lower())
            try:
                name = re.findall('conta:.+\/\s+([^;]+)',line)[0]
            except:
                pass
            try:
                branchCode = re.findall('coop\.:\s(\d+-\d+)',line)[0]
            except:
                pass
            try:
                accountNumber = re.findall('conta:\s+([\d+\.\-]+)',line)[0]
            except:
                pass
        
        return name, branchCode, accountNumber
    
    def get_information_sicoobpj2(self):
        
        pagez = np.array(self.pages[0])[740:900,:,:]
        final_output = self.do_opencv_partially(pagez)
        name = ''
        branchCode = ''
        accountNumber = ''
        for line in final_output:
            line = self.remover_acentos(line.lower())
            try:
                name = re.findall('conta:.+-\s+?([^;]+)',line)[0]
            except:
                pass
            try:
                branchCode = re.findall('coop\.:\s(\d+-\d+)',line)[0]
            except:
                pass
            try:
                accountNumber = re.findall('conta:\s+([\d+\.\-]+)',line)[0]
            except:
                pass
        
        return name, branchCode, accountNumber
