from import_libs import *

class Mixin7:
    
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

                    adict['transaction'] = {
                        'date'   : datetime.datetime.strptime(splt_line[0], "%d/%m/%Y").strftime("%Y-%m-%d"),
                        'source' : self.remover_acentos(splt_line[1]),
                        'type'   : ['CREDITO' if '-' not in splt_line[3] else 'DEBITO'][0],
                        'amount' : np.round(float(''.join(re.findall('[\-\d+]',splt_line[3])))/100,2)
                    }
                    amounts.append(adict)
            except:
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
    
    def output_santander3(self,final_output):
        
        # to json
        amounts = []
        balance = []
        date = ''

        for line in final_output:

            line = self.remover_acentos(line.lower().replace('€','c'))

            splited = line.split(';')

            try:

                index = -2

                if len(splited) == 6:

                    index = -3

                    day = {}
                    factor = 1
                    if '-' in splited[-2]:
                        factor = -1
                    day['day'] = {
                            'date' : datetime.datetime.strptime(re.findall('\d{2}\/\d{2}\/\d{2}',splited[0])[0], "%d/%m/%y").strftime("%Y-%m-%d"),
                            'amount' : factor*float(re.findall('\d+',splited[-2].replace('.','').replace(',',''))[0])/100
                    }
                    balance.append(day)

                factor = 1

                if '-' in splited[index]:
                    factor = -1
                adict = {}
                adict['transaction'] = {
                    'date'   : datetime.datetime.strptime(re.findall('\d{2}\/\d{2}\/\d{2}',splited[0])[0], "%d/%m/%y").strftime("%Y-%m-%d"),
                    'source' : splited[1],
                    'type'   : ['CREDITO' if factor == 1 else 'DEBITO'][0],
                    'amount' : factor*float(re.findall('\d+',splited[index].replace('.','').replace(',',''))[0])/100
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
    
    def get_information_santander(self):
        
        pagez = np.array(convert_from_path(self.filenameWithPath,first_page=1,last_page=1,dpi=300)[0])[300:500,:,:]
        final_output = self.do_opencv_partially(pagez)
        
        name = ''
        branchCode = ''
        accountNumber = ''
        final_output = self.remover_acentos(''.join(final_output)).lower()
        try:
            name = final_output.split(';')[0]
        except:
            pass
        try:
            branchCode = re.findall('agencia:\s+(\d+)',final_output)[0]
            branchCode = branchCode.replace(' ','')
        except:
            pass
        try:
            accountNumber = re.findall('conta:\s+(\d+)',final_output)[0]
            accountNumber = accountNumber.replace(' ','')
        except:
            pass

        return name, branchCode, accountNumber

    def get_information_santander2(self):
        
        pagez = np.array(convert_from_path(self.filenameWithPath,first_page=1,last_page=1,dpi=300)[0])[400:600,:,:]
        final_output = self.do_opencv_partially(pagez)
        
        name = ''
        branchCode = ''
        accountNumber = ''
        final_output = self.remover_acentos(''.join(final_output)).lower()
        try:
            name = final_output.split(';')[0]
        except:
            pass
        try:
            branchCode = re.findall('agencia:\s+(\d+)',final_output)[0]
            branchCode = branchCode.replace(' ','')
        except:
            pass
        try:
            accountNumber = re.findall('conta\s+corrente:\s+([^;\s]+)',final_output)[0]
            accountNumber = accountNumber.replace(' ','')
        except:
            pass

        return name, branchCode, accountNumber
    
    def get_information_santander3(self):
        
        pagez = np.array(convert_from_path(self.filenameWithPath,first_page=1,last_page=1,dpi=300)[0])[400:600,:,:]
        
        final_output = self.do_opencv_partially(pagez)

        name = ''
        branchCode = ''
        accountNumber = ''
        final_output = self.remover_acentos(''.join(final_output)).lower()
        try:
            name = final_output.split(';')[0]
        except:
            pass
        try:
            branchCode = re.findall('agencia:\s+(\d+)',final_output)[0]
            branchCode = branchCode.replace(' ','')
        except:
            pass
        try:
            accountNumber = re.findall('conta:\s+([^;\s]+)',final_output)[0]
            accountNumber = accountNumber.replace(' ','')
        except:
            pass

        return name, branchCode, accountNumber
