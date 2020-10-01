from import_libs import *

class Mixin14:
    
    def neon_process_page(self,pagez):
        
        # Specify size on horizontal axis
        cols = pagez.shape[1]
        horizontal_size = cols // 30
        # Create structure element for extracting horizontal lines through morphology operations
        horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1))
        # Apply morphology operationsb
        horizontal = cv2.erode(pagez, horizontalStructure)
        horizontal = cv2.dilate(pagez, horizontalStructure)
        
        # Specify size on vertical axis
        cols = pagez.shape[0]
        vertical_size = cols // 30
        # Create structure element for extracting horizontal lines through morphology operations
        verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1,vertical_size))
        # Apply morphology operations
        vertical = cv2.erode(pagez, verticalStructure)
        vertical = cv2.dilate(pagez, verticalStructure)
        
        for i in range(pagez.shape[0]):
            for j in range(pagez.shape[1]):
                if vertical[i,j,0] < 255 and vertical[i,j,1] < 255 and vertical[i,j,2] < 255:
                    pagez[i,j,0] = 255
                    pagez[i,j,1] = 255
                    pagez[i,j,2] = 255
                else:
                    pass

                if horizontal[i,j,0] < 255 and horizontal[i,j,1] < 255 and horizontal[i,j,2] < 255:
                    pagez[i,j,0] = 255
                    pagez[i,j,1] = 255
                    pagez[i,j,2] = 255
                else:
                    pass

                if pagez[i,j,0] == 0 and pagez[i,j,1] == 166 and pagez[i,j,2] == 221:
                    pagez[i,j,0] = 0
                    pagez[i,j,1] = 0
                    pagez[i,j,2] = 0
                else:
                    pass

                if pagez[i,j,0] == 3 and pagez[i,j,1] == 162 and pagez[i,j,2] == 164:
                    pagez[i,j,0] = 0
                    pagez[i,j,1] = 0
                    pagez[i,j,2] = 0
                else:
                    pass
                
        return pagez
    
    def output_neon(self,final_output):
        
        # to json
        amounts = []
        balance = []

        for line in final_output:

            line = self.remover_acentos(line.lower())

            splited = line.split(';')

            try:

                # valor

                factor = -1
                if '-' in re.findall('(-?r\$|-?rs)',line)[0]:
                    factor = -1
                else:
                    factor = 1

                try:
                    date = re.findall('(\d{2}\/\d{2}\/\d{4})',line)[0]
                except:
                    pass

                adict = {}
                adict['transaction'] = {
                    'date'   : datetime.datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d"),
                    'source' : splited[0],
                    'type'   : ['CREDITO' if factor == 1 else 'DEBITO'][0],
                    'amount' : factor*float(re.findall('(\d+\.\d{2})',line.replace('.','').replace(',','.'))[0])
                }
                amounts.append(adict)

                # saldo

                day = {}

                factor = -1
                if '-' in re.findall('(-?r\$|-?rs)',line)[1]:
                    factor = -1
                else:
                    factor = 1

                day['day'] = {
                        'date' : datetime.datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d"),
                        'amount' : factor*float(re.findall('(\d+\.\d{2})',line.replace('.','').replace(',','.'))[1])
                }

                if len(balance) > 0 and balance[-1]['day']['date'] == day['day']['date']:
                    balance[-1]['day']['amount'] = day['day']['amount']
                else:
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
    
    def get_information_neon(self):

        final_output = self.do_opencv_partially(np.array(convert_from_path(self.filenameWithPath,first_page=1,last_page=1,dpi=300)[0])[200:500,100:1200,:])

        name = ''
        branchCode = ''
        accountNumber = ''

        final_output = self.remover_acentos(' '.join(final_output).lower())

        try:
            name = re.findall('nome:?;\s+([^;]+)',final_output)[0]
        except:
            pass
        try:
            for line in final_output:
                try:
                    branchCode = re.findall('agencia:?;?\S+?\s+(\d+)',final_output)[0]
                except:
                    pass
                try:
                    accountNumber = re.findall('(\d+-\d+)?;$',final_output)[0]
                except:
                    pass
        except:
            pass

        return name, branchCode, accountNumber