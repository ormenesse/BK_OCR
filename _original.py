from functions_imports import *

class Mixin6:
    
    def output_original(self,final_output):
        
        #deciding boundries
        stop_for = set([j if len(re.findall('^\d{2}\/\d{2}\/\d{2}',i)) > 0 else 0 for j,i in enumerate(final_output)])
        int_stop_for = len(final_output)
        if max(stop_for) > 0 and max(stop_for) < int_stop_for:
            int_stop_for = max(stop_for)
            
        splited = []
        for line in final_output[:int_stop_for+2]:
            splited.append(len(line.split(';')))
            
        # organizing document
        final_array = []
        for i,n in enumerate(splited):
            if n == 2:
                try:
                    string = final_array.pop()
                    string = string.split(';')
                    string[1] = string[1] + ' ' + final_output[i].split(';')[0]
                    final_array.append(';'.join(string))
                except:
                    pass
            elif n == 3 and 'R$' not in final_output[i]:
                try:
                    string = final_array.pop()
                    string = string.split(';')
                    string[1] = string[1] + ' ' + final_output[i].split(';')[0]
                    final_array.append(';'.join(string))
                except:
                    pass
            else:
                final_array.append(final_output[i])
                
        # to json
        amounts = []
        balance = []
        for line in final_array:
            try:
                line = self.remover_acentos(line)
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
                        'source' : splt_line[1],
                        'type'   : splt_line[2],
                        'amount' : factor*float(re.findall('\d+\.\d+',splt_line[3].replace(',','.'))[0])
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
    
    def get_information_original(self):
        
        pagez = np.array(self.pages[0])[500:950,200:1150,:]
        final_output = self.do_opencv_partially(pagez)
        
        name = ''
        try:
            name = re.findall('^([^\|;]+)',final_output[0].lower())[0]
        except:
            pass
        branchCode = ''
        accountNumber = ''
        for line in final_output:
            line = self.remover_acentos(line.lower())
            try:
                branchCode = re.findall('agencia:\s+([^\|;]+)',line)[0]
                branchCode = branchCode.replace(' ','')
            except:
                pass
            try:
                accountNumber = re.findall('conta:\s([^\|;]+)',line)[0]
                accountNumber = accountNumber.replace(' ','')
            except:
                pass
        
        return name, branchCode, accountNumber