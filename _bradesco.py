from import_libs import *

class Mixin2:
    
    def output_bradesco(self,final_output):
        
        # to json
        amounts = []

        for i,line in enumerate(final_output):
            try:
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
        
        return extrato
    
    def output_bradescopj2(self,final_output):
        
        stop_for = set([j if 'Ultimos Lançamentos;' in i else 0 for j,i in enumerate(final_output)])
        int_stop_for = len(final_output)
        if max(stop_for) > 0 and max(stop_for) < int_stop_for:
            int_stop_for = max(stop_for)
            
        # to json
        amounts = []
        balance = []
        date = ''
        for line in final_output[:int_stop_for]:
            try:
                line = self.remover_acentos(line)
                splited = line.split(';')

                if 'Ultimos Lançamentos;' in line:
                    break

                if bool(re.search('\d{2}/\d{2}/\d{2}',splited[0])):
                    date = re.search('\d{2}/\d{2}/\d+',splited[0]).group()

                if len(splited) > 3 and bool(re.search('\d+\.\d+',splited[-2].replace('.','').replace(',','.'))) and 'total' not in line.lower():

                    day = {}
                    factor = 1
                    if '-' in splited[-2]:
                        factor = -1
                    day['day'] = {
                            'date' : datetime.datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d"),
                            'amount' : factor*float(re.findall('\d+\.\d+',splited[-2].replace('.','').replace(',','.'))[0])
                    }
                    balance.append(day)

                    #
                    if bool(re.search('\d+\.\d+',splited[-3].replace('.','').replace(',','.'))):
                        factor = 1
                        if '-' in splited[-3]:
                            factor = -1
                        adict = {}
                        adict['transaction'] = {
                            'date'   : datetime.datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d"),
                            'source' : self.remover_acentos(' '.join(splited[1:-3])),
                            'type'   : ['CREDITO' if factor == 1 else 'DEBITO'][0],
                            'amount' : factor*float(re.findall('\d+\.\d+',splited[-3].replace('.','').replace(',','.'))[0])
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
    
    def get_information_bradesco(self):
        
        pagez = np.array(self.pages[0])[:900,:,:]
        final_output = self.do_opencv_partially(pagez)
        
        name = ''
        branchCode = ''
        accountNumber = ''
        for line in final_output:
            for splited in line.split(';'):

                splited = self.remover_acentos(splited.lower())
                try:
                    regex_out = re.findall('.+ag:\s+(\d+)\s+\|\s+cc:\s+([0-9\-]+)',splited)
                    branchCode = regex_out[0][0]
                    accountNumber = regex_out[0][1]
                except:
                    pass
                try:
                    name = re.findall('(.+)\s+\|\s+(cnpj|cnp\)): \d+\.\d+\.\d+\/\d+-\d+',splited)[0]
                except:
                    pass

        return name, branchCode, accountNumber
