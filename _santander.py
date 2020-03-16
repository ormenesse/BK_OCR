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

                    adict[datetime.datetime.strptime(splt_line[0], "%d/%m/%Y").strftime("%Y-%m-%d")] = {
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
    
    def get_information_santander(self):
        
        pagez = np.array(self.pages[0])[300:500,:,:]
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
        
        pagez = np.array(self.pages[0])[400:600,:,:]
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
