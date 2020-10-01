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
    
    def output_sicoob_pj3(self,final_output):
        
        # to json
        amounts = []
        balance = []
        date = ''
        for line in final_output:

            line = self.remover_acentos(line.lower())

            if bool(re.search('\d{2}/\d{2}/\d{2}',line)):

                date = re.search('\d{2}/\d{2}/\d+',line).group()

                splited = line.split(';')

                try:
                    if ('saldo do dia' not in line) and ('saldo anterior' not in line):

                        factor = 1
                        if 'd' in splited[-2]:
                            factor = -1
                        adict = {}
                        adict['transaction'] = {
                            'date'   : datetime.datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d"),
                            'source' : ' '.join(splited[1:-2]),
                            'type'   : ['CREDITO' if factor == 1 else 'DEBITO'][0],
                            'amount' : factor*float(re.findall('\d+\.\d+',splited[-2].replace('.','').replace(',','.'))[0])
                        }
                        amounts.append(adict)

                    else:

                        day = {}
                        factor = 1
                        if 'd' in splited[-2]:
                            factor = -1
                        day['day'] = {
                                'date' : datetime.datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d"),
                                'amount' : factor*float(re.findall('\d+\.\d+',splited[-2].replace('.','').replace(',','.'))[0])
                        }
                        balance.append(day)

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

                splited = line.split(';')

                try:

                    if ('saldo do dia' in line) or ('saldo anterior' in line):

                        day = {}
                        factor = 1
                        if 'd' in splited[-2]:
                            factor = -1
                        day['day'] = {
                                'date' : datetime.datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d"),
                                'amount' : factor*float(re.findall('\d+\.\d+',splited[-2].replace('.','').replace(',','.'))[0])
                        }
                        balance.append(day)

                    elif 'resumo;' in line:

                        break

                    else:

                        amounts[-1]['transaction']['source'] = amounts[-1]['transaction']['source'] + line.replace(';',' ')


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
    
    def output_sicoob_pj4(self,final_output):
        
        fo = []
        for line in final_output:
            fo.append(line)
        fo.reverse()

        newArray = []
        buffer = ''
        for line in fo:

            if len(re.findall('\d{2}\/\d{2}',line)) == 0 and 'SALDO' not in line:
                buffer = line
            else:
                if buffer != '':
                    newArray.append(line+buffer)
                    buffer = ''
                else:
                    newArray.append(line+buffer)

        newArray.reverse()
        
        # to json
        amounts = []
        balance = []

        year = datetime.datetime.strptime(re.findall('(\d+\/\d+\/\d+)',final_output[0])[0], "%d/%m/%Y").year
        month = datetime.datetime.strptime(re.findall('(\d+\/\d+\/\d+)',final_output[0])[0], "%d/%m/%Y").month
        dday = datetime.datetime.strptime(re.findall('(\d+\/\d+\/\d+)',final_output[0])[0], "%d/%m/%Y").day

        for line in newArray:

            line = self.remover_acentos(line.lower())

            splited = line.split(';')

            try:

                if 'saldo' in line:

                    day = {}

                    factor = 1
                    if 'd' in re.findall('\;([\d\.,cd]+)\;',line)[0]:
                        factor = -1
                    day['day'] = {
                            'date' : datetime.datetime.strptime(str(dday).zfill(2)+'/'+str(month).zfill(2)+'/'+str(year), "%d/%m/%Y").strftime("%Y-%m-%d"),
                            'amount' : factor*float(re.findall('\;([\d\.,]+)',line)[0].replace('.','').replace(',','.'))
                    }

                    if len(balance) > 0 and balance[-1]['day']['date'] == day['day']['date']:
                        balance[-1]['day']['amount'] = day['day']['amount']
                    else:
                        balance.append(day)

                else:

                    if datetime.datetime.strptime(splited[0]+'/'+str(year), "%d/%m/%Y").month == 1 and month == 12:

                        year = year + 1

                    month = datetime.datetime.strptime(splited[0]+'/'+str(year), "%d/%m/%Y").month

                    dday = datetime.datetime.strptime(splited[0]+'/'+str(year), "%d/%m/%Y").day

                    factor = 1
                    if 'd' in re.findall('\;([\d\.,cd]+)\;',line)[0]:
                        factor = -1
                    adict = {}
                    adict['transaction'] = {
                        'date'   : datetime.datetime.strptime(splited[0]+'/'+str(year), "%d/%m/%Y").strftime("%Y-%m-%d"),
                        'source' : ' '.join(splited[1:]),
                        'type'   : ['CREDITO' if factor == 1 else 'DEBITO'][0],
                        'amount' : factor*float(re.findall('\;([\d\.,]+)',line)[0].replace('.','').replace(',','.'))
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
    
    def get_information_sicoob(self):
        
        pagez = np.array(convert_from_path(self.filenameWithPath,first_page=1,last_page=1,dpi=300)[0])[400:600,400:2000,:]
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
        
        pagez = np.array(convert_from_path(self.filenameWithPath,first_page=1,last_page=1,dpi=300)[0])[740:900,:,:]
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

    def get_information_sicoob_pj3(self):
        
        pagez = np.array(convert_from_path(self.filenameWithPath,first_page=1,last_page=1,dpi=300)[0])[335:460,100:2000,:]
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
                branchCode = re.findall('coop\.:?;?\s?(\d+-\d+)',line)[0]
            except:
                pass
            try:
                accountNumber = re.findall('conta:?;?\s?\s?\s?([\d+\.\-]+)',line)[0]
            except:
                pass

        return name, branchCode, accountNumber
    
    
    def get_information_sicoob_pj4(self):
        
        final_output = self.do_opencv_partially(np.array(convert_from_path(self.filenameWithPath,first_page=1,last_page=1,dpi=300)[0])[410:600,300:1500,:])

        name = ''
        branchCode = ''
        accountNumber = ''

        final_output = self.remover_acentos(' '.join(final_output).lower())

        try:
            name = re.findall('conta:?\s+[\d\.-]+\s+\/\s+([^;]+)',final_output)[0]
        except:
            pass
        try:
            for line in final_output:
                try:
                    branchCode = re.findall('coop.:?\s+([\d\.]+)',final_output)[0]
                except:
                    pass
                try:
                    accountNumber = re.findall('conta:?\s+([\d\.-]+)',final_output)[0]
                except:
                    pass
        except:
            pass


        return name, branchCode, accountNumber
