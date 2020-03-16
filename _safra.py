from import_libs import *

class Mixin10:
    
    
    def output_safra(self,final_output):
        
        stop_for = set([j if 'LANÇAMENTOS FUTUROS'.lower() in i.lower() else 0 for j,i in enumerate(final_output)])
        int_stop_for = len(final_output)
        if max(stop_for) > 0 and max(stop_for) < int_stop_for:
            int_stop_for = max(stop_for)
            
        # Ano atual
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        
        # to json
        amounts = []
        balance = []
        for line in final_output[:int_stop_for]:
            line = self.remover_acentos(line)
            splited = line.split(';')

            try:

                daysz = splited[0].split('/')

                if month < int(daysz[1]):
                    year = year - 1

                month = int(daysz[1])

                log_day = daysz[0] + '/' + str(month) + '/' + str(year)

                #for balance
                #'21/01/2020;SALDO DO DIA;2.636,75;',
                if 'SALDO'.lower() in line.lower():

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
                print(log_day,line, e)
                #pass

        extrato = {}
        extrato['bank_statement'] = amounts
        extrato['balance'] = balance
        
        return extrato
    
    def get_information_safra(self):
        
        pagez = np.array(self.pages[0])[350:550,1400:2500,:]
        final_output = self.do_opencv_partially(pagez)
        name = ''
        try:
            name = re.findall('^(.+);$',final_output[0])[0]
        except:
            pass
        branchCode = ''
        accountNumber = ''
        for line in final_output[1:]:
            line = self.remover_acentos(line.lower())
            try:
                branchCode = re.findall('ag:\s(\d+)',line)[0]
            except:
                pass
            try:
                accountNumber = re.findall('conta:\s([^;]+)',line)[0]
            except:
                pass
        
        return name, branchCode, accountNumber
