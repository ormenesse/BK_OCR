from import_libs import *

class Mixin5:
    
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
    
    def output_caixa2(self,final_output):
        
        # to json
        amounts = []
        balance = []
        date = ''

        for line in final_output:

            line = self.remover_acentos(line.lower().replace('€','c'))

            splited = line.split(';')

            try:

                if len(re.findall('\d+\.\d+',line.replace('.','').replace(',','.'))) >= 2:

                    day = {}
                    factor = 1
                    if 'd' in splited[-2]:
                        factor = -1
                    day['day'] = {
                            'date' : datetime.datetime.strptime(re.findall('\d{2}\/\d{2}\/\d{2}',splited[0])[0], "%d/%m/%y").strftime("%Y-%m-%d"),
                            'amount' : factor*float(re.findall('\d+\.\d+',line.replace('.','').replace(',','.'))[1])
                    }
                    balance.append(day)

                factor = 1
                if '-' in line:
                    factor = -1
                adict = {}
                adict['transaction'] = {
                    'date'   : datetime.datetime.strptime(re.findall('\d{2}\/\d{2}\/\d{2}',splited[0])[0], "%d/%m/%y").strftime("%Y-%m-%d"),
                    'source' : splited[0][11:],
                    'type'   : ['CREDITO' if factor == 1 else 'DEBITO'][0],
                    'amount' : factor*float(re.findall('\d+\.\d+',line.replace('.','').replace(',','.'))[0])
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
    
    def get_information_caixa(self):
        
        pagez = np.array(convert_from_path(self.filenameWithPath,first_page=1,last_page=1,dpi=300)[0])[300:800,100:1500,:]
        final_output = self.do_opencv_partially(pagez)
        
        name = ''
        branchCode = ''
        accountNumber = ''
        for line in final_output:
            line = self.remover_acentos(line.lower())
            try:
                name = re.findall('^cliente:;?([^\|;]+)',line)[0]
            except:
                pass
            try:
                branchCode = re.findall('conta:;(\d+)',line)[0]
                branchCode = branchCode.replace(' ','')
            except:
                pass
            try:
                accountNumber = re.findall('conta:.+\s+(\d{4,}-\d+)',line)[0]
                accountNumber = accountNumber.replace(' ','')
            except:
                pass
            
        return name, branchCode, accountNumber

    def get_information_caixa2(self):
        
        pagez = np.array(convert_from_path(self.filenameWithPath,first_page=1,last_page=1,dpi=300)[0])[350:600,10:2000,:]

        final_output = self.do_opencv_partially(pagez)

        name = ''
        branchCode = ''
        accountNumber = ''

        try:
            name = re.findall('cliente:?\s(.+)',self.remover_acentos(final_output[0].split(';')[0].lower()))[0]
        except:
            pass
        try:
            for line in final_output:
                try:
                    branchCode = re.findall('agencia:?\s(\d+)',self.remover_acentos(line).lower())[0]
                except:
                    pass
                try:
                    accountNumber = re.findall('conta:?\s(\d+?\s+-?\s+\d+);?$',self.remover_acentos(line).lower())[0].replace(' ','')
                except:
                    pass
        except:
            pass

            
        return name, branchCode, accountNumber