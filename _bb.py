from import_libs import *

class Mixin1:
    
    def output_bancobrasil(self,final_output):
        
        stop_for = set([j if '999saldo' in i.lower().replace(' ','') else 0 for j,i in enumerate(final_output)])
        int_stop_for = len(final_output)
        if max(stop_for) > 0 and max(stop_for) < int_stop_for:
            int_stop_for = max(stop_for) + 1 
            
        splited = []
        for line in final_output[:int_stop_for]:
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
            try:

                line = line.replace('€','C')
                line = self.remover_acentos(line)
                splt_line = line.split(';')
                adict = {}

                check_if_balance = re.findall('[0-9\.]{1,20}\,\d+[\sC|\sD|C|D]{1,2}',' '.join(splt_line))
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
                    'source' : re.sub('\d+\,\d{2}','',' '.join(splt_line[1:-1])),
                    'type'   : ['CREDITO' if 'D' not in check_if_balance[0] else 'DEBITO'][0],
                    'amount' : factor*float(re.findall('\d+\.\d+',check_if_balance[0])[0])
                }

                if 'saldo' not in adict['transaction']['source'].lower():
                    amounts.append(adict)
                else:
                    day = {}
                    day['day'] = {
                        'date' : adict['transaction']['date'],
                        'amount' : adict['transaction']['amount']
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
                self.logger.error(error + ' on the line ' + line)

        extrato = {}
        extrato['bank_statement'] = amounts
        extrato['balance'] = balance
        
        return extrato
    
    def output_bancobrasilpj2(self,final_output):
        
        # to json
        amounts = []
        balance = []
        for line in final_output:

            line = self.remover_acentos(line)
            line = line.replace('€','C')
            splited = line.split(';')

            try:
                if len(splited) == 4 and 'SALDO' in line:

                    day = {}
                    factor = 1
                    if 'D' in splited[-2]:
                        factor = -1
                    day['day'] = {
                            'date' : datetime.datetime.strptime(splited[0], "%d/%m/%Y").strftime("%Y-%m-%d"),
                            'amount' : factor*float(re.findall('\d+\.\d+',splited[-2].replace('.','').replace(',','.'))[0])
                    }
                    balance.append(day)

                elif len(re.findall('\d+\,\d{2}',line)) == 1:

                    factor = 1
                    if 'D' in splited[-2]:
                        factor = -1
                    adict = {}
                    adict['transaction'] = {
                        'date'   : datetime.datetime.strptime(splited[0], "%d/%m/%Y").strftime("%Y-%m-%d"),
                        'source' : remover_acentos(' '.join(splited[1:-2])),
                        'type'   : ['CREDITO' if factor == 1 else 'DEBITO'][0],
                        'amount' : factor*float(re.findall('\d+\.\d+',splited[-2].replace('.','').replace(',','.'))[0])
                    }
                    amounts.append(adict)

                elif len(re.findall('\d+\,\d{2}',line)) == 2:

                    day = {}
                    factor = 1
                    if 'D' in splited[-1]:
                        factor = -1
                    day['day'] = {
                            'date' : datetime.datetime.strptime(splited[0], "%d/%m/%Y").strftime("%Y-%m-%d"),
                            'amount' : factor*float(re.findall('\d+\.\d+',splited[-2].replace('.','').replace(',','.'))[0])
                    }
                    balance.append(day)
                    #
                    factor = 1
                    if 'D' in splited[-3]:
                        factor = -1
                    adict = {}
                    adict['transaction'] = {
                        'date'   : datetime.datetime.strptime(splited[0], "%d/%m/%Y").strftime("%Y-%m-%d"),
                        'source' : remover_acentos(' '.join(splited[1:-3])),
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
                self.logger.error(error + ' on the line ' + line)

        extrato = {}
        extrato['bank_statement'] = amounts
        extrato['balance'] = balance

        return extrato
    
    def get_information_bb(self):
        
        pagez = np.array(self.pages[0])[500:620,:1400,:]
        final_output = self.do_opencv_partially(pagez)
        
        name = ''
        branchCode = ''
        accountNumber = ''
        line = ''.join(final_output)
        line = self.remover_acentos(line.lower())
        try:
            branchCode = re.findall('agencia;([^;]+)',line)[0]
            branchCode = branchCode.replace(' ','')
        except:
            pass
        try:
            accountNumber = re.findall('conta corrente(.+-\d+)\s+([^;]+)',line)[0][0]
            accountNumber = accountNumber.replace(' ','')
            accountNumber = accountNumber.replace(';','')
        except:
            pass
        try:
            name = re.findall('conta corrente(.+-\d+)\s+([^;]+)',line)[0][1]
        except:
            pass

        return name, branchCode, accountNumber
    
    def get_information_bbpj2(self):
        
        pagez = np.array(self.pages[0])[:300,500:2000,:]
        final_output = self.do_opencv_partially(pagez)
        
        name = ''
        branchCode = ''
        accountNumber = ''
        for line in final_output:
            line = self.remover_acentos(line.lower())
            try:
                name = re.findall('cliente:\s+([^\|;]+)',line)[0]
            except:
                pass
            try:
                branchCode = re.findall('agencia:\s+(\d+-\d+)',line)[0]
                branchCode = branchCode.replace(' ','')
            except:
                pass
            try:
                accountNumber = re.findall('conta:\s+(\d+-\d+)',line)[0]
                accountNumber = accountNumber.replace(' ','')
            except:
                pass
            
        return name, branchCode, accountNumber
