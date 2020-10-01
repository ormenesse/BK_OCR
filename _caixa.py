from import_libs import *

class Mixin5:
    
    def output_caixa(self,final_output):
        
        # to json
        amounts = []
        balance = []
        for i,line in enumerate(final_output):
            try:
                line.replace('€','C')
                splt_line = line.split(';')

                adict = {}

                factor = 1
                if 'D' in splt_line[-3]:
                    factor = -1

                adict['transaction'] = {
                    'date'   : datetime.datetime.strptime(splt_line[0], "%d/%m/%Y").strftime("%Y-%m-%d"),
                    'source' : self.remover_acentos(line[ 10 : len(line)-len(''.join(splt_line[-3:])) ].replace(';',' ')),
                    'type'   : ['CREDITO' if factor == 1 else 'DEBITO'][0],
                    'amount' : factor*float(re.findall('\d+\.\d+',splt_line[-3].replace('.','').replace(',','.'))[0])
                }
                amounts.append(adict)

                if 'D' in splt_line[-2]:
                    factor = -1

                day = {}
                day['day'] = {
                        'date'   : datetime.datetime.strptime(splt_line[0], "%d/%m/%Y").strftime("%Y-%m-%d"),
                        'amount' : factor*np.round(float(''.join(re.findall('[\-\d+]',splt_line[-2])))/100,2)
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
                self.logger.error(error + ' on the line' + line)

        extrato = {}
        extrato['bank_statement'] = amounts
        extrato['balance'] = balance
        
        return extrato
    
    def get_information_caixa(self):
        
        pagez = np.array(convert_from_path(self.filenameWithPath,first_page=1,last_page=1,dpi=300)[0])[300:800,100:1500,:]
        final_output = self.do_opencv_partially(pagez)
        
        name = ''
        branchCode = ''
        accountNumber = ''
        for line in final_output:
            line = self.remover_acentos(line.lower())
            try:
                name = re.findall('^cliente:;?([^\|;]+)',line)[0]
            except:
                pass
            try:
                branchCode = re.findall('conta:;(\d+)',line)[0]
                branchCode = branchCode.replace(' ','')
            except:
                pass
            try:
                accountNumber = re.findall('conta:.+\s+(\d{4,}-\d+)',line)[0]
                accountNumber = accountNumber.replace(' ','')
            except:
                pass
            
        return name, branchCode, accountNumber
