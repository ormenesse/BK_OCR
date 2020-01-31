from functions_imports import *

class Mixin9:
    
    def output_sicredi(self,final_output):
        
        # to json
        amounts = []
        balance = []
        date = ''
        for i,line in enumerate(final_output):
            try:
                line = self.remover_acentos(line)
                splited = line.split(';')

                if len(splited) == 2:

                    splitz = final_output[i+1].split(';')
                    cache = []

                    for n,j in enumerate(splitz):

                        if n == 1:

                            cache.append(j)
                            cache.append(splited[0])
                        else:

                            cache.append(j)

                    final_output[i+1] = ';'.join(cache)

                elif len(splited) >= 5 and bool(re.search('\d+\.\d+',splited[-2].replace('.','').replace(',','.'))):

                    day = {}
                    factor = 1
                    if '-' in splited[-2]:
                        factor = -1
                    day['day'] = {
                            'date' : datetime.datetime.strptime(splited[0], "%d/%m/%Y").strftime("%Y-%m-%d"),
                            'amount' : factor*float(re.findall('\d+\.\d+',splited[-2].replace('.','').replace(',','.'))[0])
                    }
                    balance.append(day)

                    #

                    factor = 1
                    if '-' in splited[-3]:
                        factor = -1
                    adict = {}
                    adict['transaction'] = {
                        'date'   : datetime.datetime.strptime(splited[0], "%d/%m/%Y").strftime("%Y-%m-%d"),
                        'source' : self.remover_acentos(' '.join(splited[1:-3])),
                        'type'   : ['CREDITO' if factor == 1 else 'DEBITO'][0],
                        'amount' : factor*float(re.findall('\d+\.\d+',splited[-3].replace('.','').replace(',','.'))[0])
                    }
                    amounts.append(adict)

                #else:
                #    print(line, len(splited))

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
        
    def get_information_sicredi(self):
        
        pagez = np.array(self.pages[0])[450:700,:,:]
        final_output = self.do_opencv_partially(pagez)
        name = ''
        branchCode = ''
        accountNumber = ''
        for line in final_output:
            line = self.remover_acentos(line.lower())
            try:
                name = re.findall('associado:\s(.+);',line)[0]
            except:
                pass
            try:
                branchCode = re.findall('cooperativa:\s(\d+)',line)[0]
            except:
                pass
            try:
                accountNumber = re.findall('conta\scorrente:\s(\S+)',line)[0]
            except:
                pass
        
        return name, branchCode, accountNumber