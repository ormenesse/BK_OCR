from import_libs import *

class Mixin4:
    
    def output_itau(self,final_output):
        
        final_line = len(final_output)
        for i,line in enumerate(final_output):
            if 'Saldo final' in line:
                final_line = i
                break
                
        final_output = final_output[:final_line+1]
        
        final_array = re.split('([0-3][0-9]\/(0[1-9]|1[012]))', ''.join(final_output),0,1)[1:]
        
        # Here I try to find the year of the balance document.
        logo = np.array(self.pages[0])
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

                try:
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

                except Exception as e:
                    exc_type, exc_obj, tb = sys.exc_info()
                    f = tb.tb_frame
                    lineno = tb.tb_lineno
                    filename = f.f_code.co_filename
                    linecache.checkcache(filename)
                    iline = linecache.getline(filename, lineno, f.f_globals)
                    error = ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, iline.strip(), exc_obj))
                    self.logger.error(error + ' on the line' + line)

                # removing what I don`t want
                #print(' | '.join(line.replace('.','').replace(',','.').split(';')[1:-2]))

                for sub_line in re.findall( '([^\|]+\|\s\d+\.\d+(-|))' ,  ' | '.join(line.replace('.','').replace(',','.').split(';')[1:-2]) ):

                    sub_line = sub_line[0]

                    if 'Saldo' not in sub_line:
                        
                        try:

                            money = re.findall('\d+\.\d+.+',sub_line)[0]

                            factor = 1

                            if '-' in money:
                                factor=-1

                        
                            adict = {}

                            adict['transaction'] = {
                                'date'   : datetime.datetime.strptime(log_day, "%d/%m/%Y").strftime("%Y-%m-%d"),
                                'source' : re.sub('\|\s+\d+\.\d+[-\s]', '', sub_line),
                                'type'   : ['CREDITO' if factor == 1 else 'DEBITO'][0],
                                'amount' : factor*float(re.findall('\d+\.\d+',money)[0])
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
    
    def output_itaupj2(self,final_output):
        
        #itau doesnt work with numbers in months
        dict_transf_mes = {
        'jan' : 1,
        'fev' : 2,
        'mar' : 3,
        'abr' : 4,
        'mai' : 5,
        'jun' : 6,
        'jul' : 7,
        'ago' : 8,
        'set' : 9,
        'out' : 10,
        'nov' : 11,
        'dez' : 12
        }
        
        # Ano atual
        year = datetime.datetime.now().year
        
        meses = set([])
        for i in final_output:
            try:
                
                meses.add(re.findall('(jan$|fev$|mar$|abr$|mai$|jun$|jul$|ago$|set$|out$|nov$|dez$)',i.split(';')[0])[0])
            
            except:
                
                pass
                
        meses = list(meses)
        meses.reverse()
        #alocating year in the analysis.
        new_dict_months = {}
        for i,j in enumerate(meses):
            if i == 0 :
                new_dict_months[j] = str(dict_transf_mes[j])+'/'+str(year)
            else:
                if dict_transf_mes[meses[i-1]] == 12 and dict_transf_mes[meses[i]] == 1:
                    year = year + 1
                new_dict_months[j] = str(dict_transf_mes[j])+'/'+str(year)
                
        # to json
        amounts = []
        balance = []
        for line in final_output:
            line = self.remover_acentos(line)
            splited = line.split(';')

            if len(splited) >= 4 and len(splited) <= 5:

                try:
                    log_day = splited[0][:2] + '/' + new_dict_months[splited[0][-3:]]

                    #for balance
                    #'21/01/2020;SALDO DO DIA;2.636,75;',
                    if 'SALDO DO DIA' in line:

                        factor = 1
                        if '-' in splited[-2]:
                            factor = -1

                        day = {}
                        day['day'] = {
                            'date' : datetime.datetime.strptime(log_day, "%d/%m/%Y").strftime("%Y-%m-%d"),
                            'amount' : factor*float(re.findall('\d+\.\d+',splited[-2].replace('.','').replace(',','.'))[0])
                        }
                        balance.append(day)
                        
                    elif 'SDO' in line:
                
                        factor = 1
                        if '-' in splited[-2]:
                            factor = -1

                        day = {}
                        day['day'] = {
                            'date' : datetime.datetime.strptime(log_day, "%d/%m/%Y").strftime("%Y-%m-%d"),
                            'amount' : factor*float(re.findall('\d+\.\d+',splited[-2].replace('.','').replace(',','.'))[0])
                        }
                        balance.append(day)

                    else:

                        factor = 1

                        if '-' in splited[-2]:
                            factor=-1


                        adict = {}

                        adict['transaction'] = {
                            'date'   : datetime.datetime.strptime(log_day, "%d/%m/%Y").strftime("%Y-%m-%d"),
                            'source' : ' '.join(splited[1:-2]),
                            'type'   : ['CREDITO' if factor == 1 else 'DEBITO'][0],
                            'amount' : factor*float(re.findall('\d+\.\d+',splited[-2].replace('.','').replace(',','.'))[0])
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
    
    def output_itaupj3(self,final_output):
        
        # to json
        amounts = []
        balance = []
        date = ''
        for line in final_output:

            line = self.remover_acentos(line.lower())

            if bool(re.search('\d{2}/\d{2}/\d{2}',line)):

                date = re.search('\d{2}/\d{2}/\d+',line).group()

            else:
                splited = line.split(';')
                try:

                    if 'saldo do dia' in line:

                        day = {}
                        factor = 1
                        if '-' in splited[-2]:
                            factor = -1
                        day['day'] = {
                                'date' : datetime.datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d"),
                                'amount' : factor*float(re.findall('\d+\.\d+',splited[-2].replace('.','').replace(',','.'))[0])
                        }
                        balance.append(day)

                    else:
                        factor = 1
                        if '-' in splited[-2]:
                            factor = -1
                        adict = {}
                        adict['transaction'] = {
                            'date'   : datetime.datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d"),
                            'source' : splited[0],
                            'type'   : ['CREDITO' if factor == 1 else 'DEBITO'][0],
                            'amount' : factor*float(re.findall('\d+\.\d+',splited[-2].replace('.','').replace(',','.'))[0])
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
    
    def output_itaupj4(self,final_output):
        
        # to json
        amounts = []
        balance = []
        date = ''

        year = datetime.datetime.strptime(re.findall('(\d+\/\d+\/\d+)',final_output[0])[0], "%d/%m/%Y").year
        month = datetime.datetime.strptime(re.findall('(\d+\/\d+\/\d+)',final_output[0])[0], "%d/%m/%Y").month

        for line in final_output:

            line = self.remover_acentos(line.lower())

            splited = line.split(';')

            try:

                if 'saldo' in line:


                    if datetime.datetime.strptime(splited[0]+'/'+str(year), "%d/%m/%Y").month == 1 and month == 12:

                        year = year + 1

                    day = {}
                    factor = 1
                    if '-' in splited[-2]:
                        factor = -1
                    day['day'] = {
                            'date' : datetime.datetime.strptime(splited[0]+'/'+str(year), "%d/%m/%Y").strftime("%Y-%m-%d"),
                            'amount' : factor*float(re.findall('\d+\.\d+',splited[-2].replace('.','').replace(',','.'))[0])
                    }
                    balance.append(day)

                    month = datetime.datetime.strptime(splited[0]+'/'+str(year), "%d/%m/%Y").month

                else:

                    if datetime.datetime.strptime(splited[0]+'/'+str(year), "%d/%m/%Y").month == 1 and month == 12:

                        year = year + 1

                    factor = 1
                    if '-' in splited[-2]:
                        factor = -1
                    adict = {}
                    adict['transaction'] = {
                        'date'   : datetime.datetime.strptime(splited[0]+'/'+str(year), "%d/%m/%Y").strftime("%Y-%m-%d"),
                        'source' : ' '.join(splited[1:-2]),
                        'type'   : ['CREDITO' if factor == 1 else 'DEBITO'][0],
                        'amount' : factor*float(re.findall('\d+\.\d+',splited[-2].replace('.','').replace(',','.'))[0])
                    }
                    amounts.append(adict)

                    month = datetime.datetime.strptime(splited[0]+'/'+str(year), "%d/%m/%Y").month

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
        
    def get_information_itau(self):
        
        pagez = np.array(convert_from_path(self.filenameWithPath,first_page=1,last_page=1,dpi=300)[0])[500:1300,450:2400,:]
        final_output = self.do_opencv_partially(pagez)
        
        try:
            name = pytesseract.image_to_string(np.array(self.pages[0])[650:720,450:1300,:],lang='por',config=r'--oem 3 --psm 7')
        except:
            name = ''
        branchCode = ''
        accountNumber = ''
        for line in final_output:
            line = self.remover_acentos(line.lower())
            try:
                branchCode = re.findall('minha\s+agencia\s+([0-9\-]+)',line)[0]
                branchCode = branchCode.replace(' ','')
            except:
                pass
            try:
                accountNumber = re.findall('minha\s+conta\s+([0-9\-]+)',line)[0]
                accountNumber = accountNumber.replace(' ','')
            except:
                pass

        return name, branchCode, accountNumber
    
    def get_information_itaupj2(self):
        
        pagez1 = np.array(convert_from_path(self.filenameWithPath,first_page=1,last_page=1,dpi=300)[0])[500:680,50:700,:]
        pagez2 = np.array(convert_from_path(self.filenameWithPath,first_page=1,last_page=1,dpi=300)[0])[500:680,1050:1700]
        pagez = np.concatenate((pagez1,pagez2))
        final_output = self.do_opencv_partially(pagez)
        
        name = ''
        branchCode = ''
        accountNumber = ''

        try:
            name = self.remover_acentos(final_output[0].split(';')[0].lower())
        except:
            pass
        try:
            for line in final_output[3].split(';'):
                try:
                    branchCode = re.findall('^(\d+)$',line)[0]
                except:
                    pass
                try:
                    accountNumber = re.findall('^(\d+-\d+)$',line)[0]
                except:
                    pass
        except:
            pass

        return name, branchCode, accountNumber
    
    def get_information_itaupj3(self):
        
        final_output = ''
        
        try:
            pagez = np.array(convert_from_path(self.filenameWithPath,first_page=1,last_page=1,dpi=300)[0])[610:710,400:2000,:]

            final_output = self.do_opencv_partially(pagez)
            
        except:
            
            try:
                
                pagez = np.array(self.pages[0])[560:650,400:2000,:]
                
                final_output = self.do_opencv_partially(pagez)
                
            except:
                
                pass

        name = ''
        branchCode = ''
        accountNumber = ''

        try:
            name = self.remover_acentos(final_output[0].split(';')[0].lower())
        except:
            pass
        try:
            for line in final_output:
                try:
                    branchCode = re.findall('^(\d+)\/',line)[0]
                except:
                    try:
                        branchCode = re.findall('(\d+)\s+?-',line)[0]
                    except:
                        pass
                try:
                    accountNumber = re.findall('\/(\d+);?$',line)[0]
                except:
                    try:
                        accountNumber = re.findall('-\s+?(\S+);?$',line)[0]
                    except:
                        pass
        except:
            pass

        return name, branchCode, accountNumber
    
    def get_information_itaupj4(self):
        
        final_output = ''
        
        try:
            pagez = np.array(convert_from_path(self.filenameWithPath,first_page=1,last_page=1,dpi=300)[0])[220:320,10:2000,:]

            final_output = self.do_opencv_partially(pagez)
            
        except:
            
            pass

        name = ''
        branchCode = ''
        accountNumber = ''

        try:
            name = re.findall('nome:?\s(.+)',self.remover_acentos(final_output[0].split(';')[0].lower()))[0]
        except:
            pass
        try:
            for line in final_output:
                try:
                    branchCode = re.findall('(\d+)\/',line)[0]
                except:
                    pass
                try:
                    accountNumber = re.findall('\/(\d+-\d+);?$',line)[0]
                except:
                    pass
        except:
            pass

        return name, branchCode, accountNumber