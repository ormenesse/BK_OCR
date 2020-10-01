from import_libs import *

class Mixin12:
    
    def output_c6(self,final_output):
        
        # to json
        amounts = []
        balance = []

        for line in final_output:

            line = self.remover_acentos(line.lower())

            splited = line.split(';')

            try:

                if 'saldo disponivel' in line:


                    day = {}
                    factor = 1
                    if '-' in splited[-2]:
                        factor = -1
                    day['day'] = {
                            'date' : datetime.datetime.strptime(re.findall('\d{2}\/\d{2}\/\d{2}',splited[0])[0], "%d/%m/%y").strftime("%Y-%m-%d"),
                            'amount' : factor*float(re.findall('\d+\.\d+',line.replace('.','').replace(',','.'))[0])
                    }
                    balance.append(day)

                else:

                    factor = 1
                    if ';d;' in line:
                        factor = -1
                    adict = {}
                    adict['transaction'] = {
                        'date'   : datetime.datetime.strptime(re.findall('\d{2}\/\d{2}\/\d{2}',splited[0])[0], "%d/%m/%y").strftime("%Y-%m-%d"),
                        'source' : splited[0][10:]+' ' +splited[1],
                        'type'   : ['CREDITO' if factor == 1 else 'DEBITO'][0],
                        'amount' : factor*float(re.findall('\d+\.\d+',line.replace('.','').replace(',','.'))[0])
                    }
                    amounts.append(adict)

            except Exception as e:
                print(line, e)
                #PrintException()

        extrato = {}
        extrato['bank_statement'] = amounts
        extrato['balance'] = balance

        return extrato
        
    def get_information_c6(self):

        final_output = self.do_opencv_partially(np.array(convert_from_path(self.filenameWithPath,first_page=1,last_page=1,dpi=300)[0])[450:600,10:,:])

        name = ''
        branchCode = ''
        accountNumber = ''

        final_output = self.remover_acentos(' '.join(final_output).lower())

        try:
            name = re.findall(';\s+([\w\s]+);',final_output)[0]
        except:
            pass
        try:
            for line in final_output:
                try:
                    branchCode = re.findall('agencia:?\s+(\d+)',final_output)[0]
                except:
                    pass
                try:
                    accountNumber = re.findall('conta:?\s+(\d+-\d+)',final_output)[0]
                except:
                    pass
        except:
            pass
        
        return name, branchCode, accountNumber
