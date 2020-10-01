from import_libs import *

class Mixin:

    def do_opencv_stuff(self,page_picture):
        
        #turn my page into gray
        gray = cv2.cvtColor(page_picture, cv2.COLOR_RGB2GRAY)
        #inverting black and white
        _ , binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        #intializing some structures
        rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 2)) #key structure
        sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)) # key structure
        # apply a tophat (whitehat) morphological operator to find light
        # regions against a dark background (i.e., the credit card numbers)
        tophat = cv2.morphologyEx(binary, cv2.MORPH_TOPHAT, rectKernel)
        # compute the Scharr gradient of the tophat image, then scale
        # the rest back into the range [0, 255]
        gradX = cv2.Sobel(tophat, ddepth=cv2.CV_32F, dx=1, dy=0,ksize=-1)
        gradX = np.absolute(gradX)
        (minVal, maxVal) = (np.min(gradX), np.max(gradX))
        try:
            gradX = (255 * ((gradX - minVal) / (maxVal - minVal)))
        except:
            gradX = (255 * ((int(gradX) - int(minVal)) / (int(maxVal) - int(minVal))))
        gradX = gradX.astype("uint8")
        # apply a closing operation using the rectangular kernel to help
        # cloes gaps in between credit card number digits, then apply
        # Otsu's thresholding method to binarize the image
        gradX = cv2.morphologyEx(gradX, cv2.MORPH_CLOSE, rectKernel)
        thresh = cv2.threshold(gradX, 0, 255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        # apply a second closing operation to the binary image, again
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, sqKernel)
        # find contours in the thresholded image, then initialize the
        # list of digit locations
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        locs = []

        #here I will choose wich contour I will use
        # loop over the contours
        for (i, c) in enumerate(cnts):
            # compute the bounding box of the contour, then use the
            # bounding box coordinates to derive the aspect ratio
            (x, y, w, h) = cv2.boundingRect(c)

            #working only with minimum size squares
            if w > 20 and h > 20 :
                # append the bounding box region of the digits group
                # to our locations list
                locs.append((x, y, w, h))

        # making a copy of the final result
        copylocs = locs.copy()
        # most contours are not in a rounded pixel, here I am trying to make every line countour stay together\
        # I need the countours to be aligned in orther to put everything in the exact place in my future csv, txt.
        locs = []
        for i in np.arange(0,len(copylocs)):
            x = int(np.round(copylocs[i][0]/10)*10)
            y = int(np.round(copylocs[i][1]/10)*10)
            w = int(np.round(copylocs[i][2]/10)*10)
            h = int(np.round(copylocs[i][3]/10)*10)
            locs.append((x, y, w, h))
            
        
        # sort the square locations 
        locs = sorted(locs, key=operator.itemgetter(1, 0))
        # diff to find the lines.
        diff= []
        
        size = 50
        if self.bank == 'ItadEmpresas' or self.bank == 'nubank' or len(locs[:]) < 50:
            size = len(locs[:])
            
        for i in np.arange(0,size-1):
            # number 6 is just a threshold I decided 
            if locs[i+1][1]-locs[i][1] > 6:
                diff.append((locs[i+1][1]-locs[i][1]))
        # average line space
        try:
            linespace = int(np.mean(diff))
            linestd = int(np.std(diff)/2)
        except:
            linespace = 10
            linestd = 5
        #Apply TESSERACT in the image - it works really well when set for straight line.
        final_output = []
        output = ''
        support_string = []
        y = locs[0][1]
        
        threshold = np.abs(linespace-linestd)
        if self.bank == 'inter' or self.bank == 'neon':
            threshold = linespace+linestd
        elif self.bank == 'stone':
            threshold = linespace+1.5*linestd
            
        for location in locs:
            try:
                output_text = pytesseract.image_to_string(page_picture[location[1]-10:location[1]+7+location[3],
                                                          location[0]-12:location[0]+15+location[2],:],lang='por',
                                                          config=r'--oem 3 --psm 7')
            except:
                output_text = pytesseract.image_to_string(page_picture[location[1]:location[1]+location[3],
                                                          location[0]:location[0]+location[2],:],lang='por',
                                                          config=r'--oem 3 --psm 7')
            #looking for almost the same line
            if np.abs(location[1] - y) < threshold:
                support_string.append((location[0],output_text))
            else:
                y = location[1]
                support_string = sorted(support_string,key=lambda x: x[0])
                for (x,string) in support_string:
                    output = output + string + ';'
                support_string = [(location[0],output_text)]
                output = output + '\n'
        #cleaning leftovers
        for (x,string) in support_string:
            output = output + string + ';'
        #final output
        final_output = output.split('\n')
        
        return final_output
    
    def do_opencv_partially(self,img_input):
        
        #turn my page into gray
        gray = cv2.cvtColor(img_input, cv2.COLOR_RGB2GRAY)
        #inverting black and white
        _ , binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        #intializing some structures
        rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 2)) #key structure
        sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)) # key structure
        # apply a tophat (whitehat) morphological operator to find light
        # regions against a dark background (i.e., the credit card numbers)
        tophat = cv2.morphologyEx(binary, cv2.MORPH_TOPHAT, rectKernel)
        # compute the Scharr gradient of the tophat image, then scale
        # the rest back into the range [0, 255]
        gradX = cv2.Sobel(tophat, ddepth=cv2.CV_32F, dx=1, dy=0,ksize=-1)
        gradX = np.absolute(gradX)
        (minVal, maxVal) = (np.min(gradX), np.max(gradX))
        gradX = (255 * ((gradX - minVal) / (maxVal - minVal)))
        gradX = gradX.astype("uint8")
        # apply a closing operation using the rectangular kernel to help
        # cloes gaps in between credit card number digits, then apply
        # Otsu's thresholding method to binarize the image
        gradX = cv2.morphologyEx(gradX, cv2.MORPH_CLOSE, rectKernel)
        thresh = cv2.threshold(gradX, 0, 255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        # apply a second closing operation to the binary image, again
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, sqKernel)
        # find contours in the thresholded image, then initialize the
        # list of digit locations
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        locs = []

        #here I will choose wich contour I will use
        # loop over the contours
        for (i, c) in enumerate(cnts):
            # compute the bounding box of the contour, then use the
            # bounding box coordinates to derive the aspect ratio
            (x, y, w, h) = cv2.boundingRect(c)

            #working only with minimum size squares
            if w > 20 and h > 10 :
                # append the bounding box region of the digits group
                # to our locations list
                locs.append((x, y, w, h))

        # making a copy of the final result
        copylocs = locs.copy()
        # most contours are not in a rounded pixel, here I am trying to make every line countour stay together\
        # I need the countours to be aligned in orther to put everything in the exact place in my future csv, txt.
        locs = []
        for i in np.arange(0,len(copylocs)):
            x = int(np.round(copylocs[i][0]/10)*10)
            y = int(np.round(copylocs[i][1]/10)*10)
            w = int(np.round(copylocs[i][2]/10)*10)
            h = int(np.round(copylocs[i][3]/10)*10)
            locs.append((x, y, w, h))
        # sort the square locations 
        locs = sorted(locs, key=operator.itemgetter(1, 0))
        # diff to find the lines.
        diff= []
        for i in np.arange(0,len(locs)-1):
            # number 6 is just a threshold I decided 
            if locs[i+1][1]-locs[i][1] > 6:
                diff.append((locs[i+1][1]-locs[i][1]))
        # average line space
        try:
            linespace = int(np.mean(diff))
            linestd = int(np.std(diff))
        except:
            linespace = 10
            linestd = 5
        #Apply TESSERACT in the image - it works really well when set for straight line.
        final_output = []
        output = ''
        support_string = []
        y = locs[0][1]
        
        threshold = np.abs(linespace-linestd)
        if self.bank == 'inter':
            threshold = linespace+linestd
        
        for location in locs:
            try:
                output_text = pytesseract.image_to_string(img_input[location[1]-10:location[1]+7+location[3],
                                                          location[0]-12:location[0]+15+location[2],:],lang='por',
                                                          config=r'--oem 3 --psm 7')
            except:
                output_text = pytesseract.image_to_string(img_input[location[1]:location[1]+location[3],
                                                          location[0]:location[0]+location[2],:],lang='por',
                                                          config=r'--oem 3 --psm 7')
            #looking for almost the same line
            if np.abs(location[1] - y) < threshold:
                support_string.append((location[0],output_text))
            else:
                y = location[1]
                support_string = sorted(support_string,key=lambda x: x[0])
                for (x,string) in support_string:
                    output = output + string + ';'
                support_string = [(location[0],output_text)]
                output = output + '\n'
        #cleaning leftovers
        for (x,string) in support_string:
            output = output + string + ';'
        #final output
        final_output = output.split('\n')
        
        return final_output
