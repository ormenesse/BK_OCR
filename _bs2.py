from import_libs import *

class Mixin13:
    
    def output_bs2(self,final_output):
        
        # to json
        amounts = []
        balance = []
        date = None

        for line in final_output:

            try:
                
                line = self.remover_acentos(line)
                splited = line.split(';')

                if 'Saldo Final' in line:
                    day = {}
                    factor = 1
                    if '-' in splited[-2]:
                        factor = -1
                    day['day'] = {
                            'date' : date,
                            'amount' : factor*float(re.findall('\d+\.\d+',line.replace(' ','').replace(',','.'))[0])
                    }
                    balance.append(day)

                #
                factor = 1
                if '-' in splited[-2]:
                    factor = -1
                adict = {}
                adict['transaction'] = {
                    'date'   : datetime.datetime.strptime(splited[0], "%d/%m/%Y").strftime("%Y-%m-%d"),
                    'source' : self.remover_acentos(' '.join(splited[:-2])),
                    'type'   : ['CREDITO' if factor == 1 else 'DEBITO'][0],
                    'amount' : factor*float(''.join(re.findall('(\d)',splited[-2])))/100
                }
                
                amounts.append(adict)

                date = datetime.datetime.strptime(splited[0], "%d/%m/%Y").strftime("%Y-%m-%d")

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
    
    def get_information_bs2(self):
        
        final_output = self.do_opencv_partially(np.array(convert_from_path(self.filenameWithPath,first_page=1,last_page=1,dpi=300)[0])[320:600,200:800,:])

        name = ''
        branchCode = ''
        accountNumber = ''

        final_output = self.remover_acentos(' '.join(final_output).lower())

        try:
            name = re.findall('^([^;]+)',final_output)[0]
        except:
            pass
        try:
            for line in final_output:
                try:
                    branchCode = re.findall('ag?:?\s+(\d+)',final_output)[0]
                except:
                    pass
                try:
                    accountNumber = re.findall('conta?:?\s+(\d+-\d+)',final_output)[0]
                except:
                    pass
        except:
            pass

        return name, branchCode, accountNumber