from import_libs import *
import copy

class Mixin11:
    
    def output_stone(self,final_output):
        
        fo = []
        for line in final_output:
            fo.append(line)
        fo.reverse()
        
        newArray = []
        buffer = ''
        for line in fo:
            
            if len(re.findall('\d{2}\/\d{2}\/\d{2}',line)) == 0:
                buffer = line
                
            else:
                if buffer != '':
                    newArray.append(line+buffer)
                    buffer = ''
                else:
                    newArray.append(line+buffer)
                    
        # to json
        amounts = []
        balance = []

        for line in newArray:

            line = self.remover_acentos(line.lower())

            splited = line.split(';')

            try:

                dictValues = {}
                count = 0
                for i,split in enumerate(splited):

                    if len(re.findall('(-?\d+\.?\d+,\d+|0,\d+|-?\d+\.?\d+\.?\d+,\d+)',split)) > 0:

                        dictValues[count] = {'value' :re.findall('(-?\d+\.?\d+,\d+|0,\d+|-?\d+\.?\d+\.?\d+,\d+)',split)[0], 'index' : i}
                        count = count + 1



                day = {}
                factor = 1
                if '-' in dictValues[1]['value']:
                    factor = -1
                day['day'] = {
                        'date' : datetime.datetime.strptime(splited[0], "%d/%m/%Y").strftime("%Y-%m-%d"),
                        'amount' : factor*float(re.findall('\d+\.\d+',dictValues[1]['value'].replace('.','').replace(',','.'))[0])
                }
                balance.append(day)

                factor = 1
                if '-' in dictValues[0]['value']:
                    factor = -1

                source = ''
                for i,split in enumerate(splited):
                    if i != dictValues[0]['index'] and i != dictValues[1]['index'] and i != 0:
                        source = source + ' ' + split

                adict = {}
                adict['transaction'] = {
                    'date'   : datetime.datetime.strptime(splited[0], "%d/%m/%Y").strftime("%Y-%m-%d"),
                    'source' : ' '.join(splited[1:-2]),
                    'type'   : ['CREDITO' if factor == 1 else 'DEBITO'][0],
                    'amount' : factor*float(re.findall('\d+\.\d+',dictValues[0]['value'].replace('.','').replace(',','.'))[0])
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
        
    def get_information_stone(self):

        final_output_name = self.do_opencv_partially(np.array(convert_from_path(self.filenameWithPath,first_page=1,last_page=1,dpi=300)[0])[350:550,50:1500,:])

        final_output = self.do_opencv_partially(np.array(convert_from_path(self.filenameWithPath,first_page=1,last_page=1,dpi=300)[0])[460:700,1700:,:])

        name = ''
        branchCode = ''
        accountNumber = ''

        final_output_name = self.remover_acentos(' '.join(final_output_name).replace(';','').lower())

        final_output = self.remover_acentos(' '.join(final_output).lower())

        try:
            name = re.findall('titular\s(.+)',final_output_name.split(';')[0])[0]
        except:
            pass
        try:
            for line in final_output:
                try:
                    branchCode = re.findall('agencia?\s+(\d+)',final_output)[0]
                except:
                    pass
                try:
                    accountNumber = re.findall('conta\s+de\s+pagamento\s+(\d+-\d+);?$',final_output)[0]
                except:
                    pass
        except:
            pass
        
        return name, branchCode, accountNumber
