from import_libs import *

class Mixin15:
    
    def output_nubank(self,final_output):
        
        months = ['janeiro','fevereiro','marco','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro']
        monthsAbbr = ['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez']
        
        # to json
        amounts = []
        balance = []
        date = None

        try:
            ano = re.findall('('+'|'.join(months)+')'+'\s+(\d{4})',' '.join(final_output))[0][1]
            mes = re.findall('('+'|'.join(months)+')'+'\s+(\d{4})',' '.join(final_output))[1][1]
        except:
            ano = int(datetime.datetime.now().strftime('%Y'))
            mes = int(datetime.datetime.now().strftime('%m'))

        dia = 1

        LineIndex = 0
        for i in range(len(final_output)):
            if 'movimentacoes' in  self.remover_acentos(final_output[i].lower()):
                LineIndex = i
                break

        for line in final_output[LineIndex:]:

            line = self.remover_acentos(line.lower())
            splited = line.split(';')

            if 'total de saidas' in line or 'total de entradas' in line or 'saldo do dia' in line:

                try:
                    dia = int(re.findall('(\d{2})'+'\s+'+'('+'|'.join(monthsAbbr)+')',line)[0][0])
                    mes = re.findall('(\d{2})'+'\s+'+'('+'|'.join(monthsAbbr)+')',line)[0][1]
                    mes = monthsAbbr.index(mes)+1
                except Exception as e:
                    exc_type, exc_obj, tb = sys.exc_info()
                    f = tb.tb_frame
                    lineno = tb.tb_lineno
                    filename = f.f_code.co_filename
                    linecache.checkcache(filename)
                    iline = linecache.getline(filename, lineno, f.f_globals)
                    error = ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, iline.strip(), exc_obj))
                    self.logger.error(error + ' on the line' + line)

                try:

                    if 'saldo do dia' in line:
                        day = {}
                        factor = 1
                        if '-' in splited[-2]:
                            factor = -1
                        day['day'] = {
                                'date' : datetime.datetime.strptime(str(dia).zfill(2)+'/'+str(mes).zfill(2)+'/'+str(ano), "%d/%m/%Y").strftime("%Y-%m-%d"),
                                'amount' : factor*float(re.findall('\d+\.\d+',splited[-2].replace(' ','').replace(',','.'))[0])
                        }
                        balance.append(day)

                    else:
                        factor = 1
                        if 'total de saidas' in line:
                            factor = -1
                        adict = {}
                        adict['transaction'] = {
                            'date'   : datetime.datetime.strptime(str(dia).zfill(2)+'/'+str(mes).zfill(2)+'/'+str(ano), "%d/%m/%Y").strftime("%Y-%m-%d"),
                            'source' : '',
                            'type'   : ['CREDITO' if factor == 1 else 'DEBITO'][0],
                            'amount' : factor*float( re.findall('-?(\d+\,\d{2})',line.replace(' ',''))[0].replace(',','.') )
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
    
    def get_information_nubank(self):
        
        final_output = self.do_opencv_partially(np.array(convert_from_path(self.filenameWithPath,first_page=1,last_page=1,dpi=300)[0])[180:350,1000:,:])

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
                    branchCode = re.findall('agencia?:?\s+(\d+)',final_output)[0]
                except:
                    pass
                try:
                    accountNumber = re.findall('conta?:?\s+(\d+-\d+)',final_output)[0]
                except:
                    pass
        except:
            pass

        return name, branchCode, accountNumber