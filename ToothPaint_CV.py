from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import *
import numpy as np
import cv2
from skimage.util import *
from skimage.segmentation import*
import math
import random

class Paint_CV:
    def __init__(self):
        pass

    def SLIC_check(self, image, G_Filter, SLIC_nseg):
        img = img_as_float(image)
        segments_slic = slic(img, n_segments=SLIC_nseg, compactness=10, sigma=G_Filter)
        seg_slic = np.unique(segments_slic)
        if SLIC_nseg >= len(seg_slic):
            SLIC_nseg = SLIC_nseg - (SLIC_nseg - len(seg_slic))
        else:
            SLIC_nseg = None
        return SLIC_nseg

    def CONT_check(self, image, G_Filter, lowThres, highThres):
        img = cv2.GaussianBlur(self.ConvertColor(1, image.copy()), (G_Filter, G_Filter), 0)
        contours = []
        while contours == []:
            _, threshold = cv2.threshold(img, lowThres, highThres, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            if contours == []:
                if lowThres > 1:
                    lowThres -= 1
                if highThres < 255:
                    highThres += 1
        return contours

    def Segmentation(self, image, flag, G_Filter=None, bgCOLOR=None, ThresCOL=None, MaskCOL=None, KM_clst=None, MaskColor=None, SLIC_nseg=None, SLIC_mask=None, bound=None, Exam=None, Contours=None, Cont_wanted=None):
        if flag==34:        #COLOR
            img = cv2.GaussianBlur(image.copy(), (G_Filter, G_Filter), 0)
            maskLIST = []
            masking = np.zeros(image.shape[:2], np.uint8)
            for col in ThresCOL:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                mask = cv2.inRange(img, col[0], col[1])
                if MaskCOL == -1:   #invert mask
                    mask = 255 - mask
                kernel = np.ones((3, 3), np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)
                maskLIST.append(mask)
                masking = cv2.bitwise_or(masking, mask)
            image = image.copy()

            if MaskCOL==1:
                for mask in maskLIST:
                    image[mask>0] = (random.randint(10,250), random.randint(10,250), random.randint(10,250))
            if not bgCOLOR:
                image[masking == 0] = (0,0,0)
            else:
                image[masking == 0] = bgCOLOR
        elif flag==35:
            # img = cv2.GaussianBlur(self.ConvertColor(1, image.copy()), (G_Filter, G_Filter), 0)
            # contours = []
            # while contours==[]:
            #     _, threshold = cv2.threshold(img, lowThres, highThres, cv2.THRESH_BINARY)
            #     contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            #     if contours==[]:
            #         if lowThres>1:
            #             lowThres -= 1
            #         if highThres<255:
            #             highThres += 1
            # areaLIST = []
            # for contour in contours:
            #     areaLIST.append(cv2.contourArea(contour))
            # sortAreaLIST = areaLIST.copy()
            # sortAreaLIST.sort(reverse=True)
            # h,w,_ = image.shape
            # if sortAreaLIST[0]==((h-1)*(w-1)):
            #     x = sortAreaLIST[1]
            # else:
            #     x = sortAreaLIST[0]
            # x = areaLIST.index(x)
            # res = contours[x]
            maskLIST = []
            masking = np.zeros(image.shape[:2], np.uint8)
            if Exam:
                mask = cv2.drawContours(np.zeros(image.shape[:2], np.uint8), [Contours[Exam]], -1, (255, 255, 255), -1)
                if MaskCOL == -1:  # invert mask
                    mask = 255 - mask
                kernel = np.ones((3, 3), np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)
                maskLIST.append(mask)
                masking = cv2.bitwise_or(masking, mask)
            else:
                for (i,cont) in enumerate(Contours):
                    if Cont_wanted[i]:
                        mask = cv2.drawContours(np.zeros(image.shape[:2], np.uint8), [cont], -1, (255, 255, 255), -1)
                        if MaskCOL == -1:  # invert mask
                            mask = 255 - mask
                        kernel = np.ones((3, 3), np.uint8)
                        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                        mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)
                        maskLIST.append(mask)
                        masking = cv2.bitwise_or(masking, mask)
            image = image.copy()
            if not all(not x for x in MaskColor) and not Exam:
                for (i,col) in enumerate(MaskColor):
                    if col:
                        image[maskLIST[i] > 0] = col
            if not bgCOLOR:
                image[masking == 0] = (0, 0, 0)
            else:
                image[masking == 0] = bgCOLOR
            if bound:
                image = cv2.drawContours(image, Contours, -1, (255,255,0), 2)
        elif flag==36:
            px_val = np.float32(image.copy()).reshape((-1, 3))
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1)
            _, label, center = cv2.kmeans(px_val, KM_clst, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            if all(not x for x in MaskColor):
                center = np.uint8(center)
                masked_image = center[label.flatten()]
            else:
                masked_image = image.copy().reshape((-1, 3))
                for i in range(len(MaskColor)):
                    col = MaskColor[i]
                    if col:
                        masked_image[label.flatten() == i] = MaskColor[i]
            image = masked_image.reshape(image.shape)
        elif flag==37:
            img = img_as_float(image)   #convert bgr2rgb, turn to float
            segments_slic = slic(img, n_segments=SLIC_nseg, compactness=10, sigma=G_Filter)
            seg_slic = np.unique(segments_slic)
            masking = np.zeros(img.shape[:2], np.uint8)
            if Exam or Exam==0:
                for (i, segVal) in enumerate(seg_slic):
                    if Exam==i:

                        mask = np.zeros(image.shape[:2], np.uint8)
                        mask[segments_slic == segVal] = 255
                        MaskImg = cv2.bitwise_and(img, img, mask=mask)
                        break
            elif all(not x for x in SLIC_mask):
                if bgCOLOR:
                    Temp = np.zeros(img.shape, np.uint8)
                    Temp[masking == 0] = bgCOLOR
                    MaskImg = img_as_float64(Temp)
                else:
                    MaskImg = masking
            elif all(x for x in SLIC_mask) and all(not x for x in MaskColor):
                MaskImg = img
            else:
                maskLIST = []
                for (i, segVal) in enumerate(np.unique(segments_slic)):
                    if SLIC_mask[i]:
                        mask = np.zeros(image.shape[:2], np.uint8)
                        mask[segments_slic == segVal] = 255
                        maskLIST.append((mask, i))
                        masking = cv2.bitwise_or(masking, mask)
                        # MaskImg = cv2.bitwise_and(img, img, mask=mask)
                if all(not x for x in MaskColor):
                    MaskImg = cv2.bitwise_and(img, img, mask=masking)
                else:
                    MaskImg = np.zeros(img.shape, np.uint8)
                    for mask in maskLIST:
                        if MaskColor[mask[1]]:
                            MaskImg[mask[0]>0] = MaskColor[mask[1]]
                if bgCOLOR:
                    MaskImg = img_as_ubyte(MaskImg)
                    MaskImg[masking == 0] = bgCOLOR
                MaskImg = img_as_float64(MaskImg)
            if bound:
                SLICimage = mark_boundaries(MaskImg, segments_slic)
            else:
                SLICimage = MaskImg
            image = img_as_ubyte(SLICimage)
        return image

    def EdgeDetection(self, image, flag, G_Ksize, Thres_low=None, Thres_high=None, S_Ksize=None, Ksize=None):
        grey_image = self.ConvertColor(1, image)
        image = cv2.GaussianBlur(grey_image, (G_Ksize, G_Ksize), 0)
        if flag==23:    #Wide   Canny
            image = cv2.Canny(image, 10, 200)
        elif flag==24:  #Tight  Canny
            image = cv2.Canny(image, 225, 250)
        elif flag==25:  #Auto   Canny
            sigma = 0.33
            v = np.median(image)
            # apply automatic Canny edge detection using the computed median
            lower = int(max(0, (1.0 - sigma) * v))
            upper = int(min(255, (1.0 + sigma) * v))
            image = cv2.Canny(image, lower, upper)
        elif flag==26:  #Customize Canny
            image = cv2.Canny(image, Thres_low, Thres_high)
        elif flag==27:  #Laplacian
            image = cv2.Laplacian(image, ksize=S_Ksize, ddepth=cv2.CV_16S)
            image = cv2.convertScaleAbs(image)
        elif flag==28:  # Sobel X
            Sobel_X = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=Ksize)
            image = cv2.convertScaleAbs(Sobel_X)
        elif flag==29:  # Sobel Y
            Sobel_Y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=Ksize)
            image = cv2.convertScaleAbs(Sobel_Y)
        elif flag==30:  # Sobel X & Y
            Sobel_X = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=Ksize)
            Sobel_Y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=Ksize)
            image = cv2.bitwise_or(cv2.convertScaleAbs(Sobel_X), cv2.convertScaleAbs(Sobel_Y))
        elif flag==31:
            kernelx = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])
            image = cv2.filter2D(image, -1, kernelx)
        elif flag==32:
            kernely = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
            image = cv2.filter2D(image, -1, kernely)
        elif flag==33:
            kernelx = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])
            kernely = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
            image = cv2.bitwise_or(cv2.filter2D(image, -1, kernelx), cv2.filter2D(image, -1, kernely))
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        return image

    def Threshold(self, image, flag, thres=None, maxThres=None, BlockSize=None, constant=None):
        if 16<=flag<=20:
            if flag==16:
                thres_type = cv2.THRESH_BINARY
            elif flag==17:
                thres_type = cv2.THRESH_BINARY_INV
            elif flag==18:
                thres_type = cv2.THRESH_TRUNC
            elif flag==19:
                thres_type = cv2.THRESH_TOZERO
            elif flag==20:
                thres_type = cv2.THRESH_TOZERO_INV
            _, image = cv2.threshold(image, thres, maxThres, thres_type)
        elif flag==21:
            image = self.ConvertColor(1, image)
            image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, BlockSize, constant)
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        elif flag==22:
            image = self.ConvertColor(1, image)
            image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, BlockSize, constant)
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        return image

    def Filter(self, image, flag, Ksize=None, depth=None, colspace=None, contrast=None, sharpen=None, bitLevel=None, customFilter=None):
        if flag==3:     #Gaussian Blur
            image = cv2.GaussianBlur(image, (Ksize, Ksize), 0)
        elif flag==4:   #Median Blur
            image = cv2.medianBlur(image, Ksize)
        elif flag==5:   #Average Blur
            image = cv2.blur(image, (Ksize, Ksize))
        elif flag==6:   #Box Filter
            image = cv2.boxFilter(image, 0, (Ksize, Ksize))
        elif flag==7:   #Bilateral Filter
            image = cv2.bilateralFilter(image, depth, colspace, colspace)
        elif flag==8:
            image = cv2.addWeighted(image, contrast, np.zeros(image.shape, image.dtype), 0,0)
        elif flag==9:
            kernel = np.ones((Ksize, Ksize), np.float32) * (-1)
            kernel[math.floor(Ksize / 2), math.floor(Ksize / 2)] = sharpen
            image = cv2.filter2D(image, -1, kernel)
        elif flag==10:  #Emboss
            filter = np.array([[0,1,0],[0,0,0],[0,-1,0]])
            image = cv2.filter2D(image, -1, filter)
            image += 128
        elif flag==11:  #Sepia
            filter = np.array([[0.272, 0.534, 0.131], [0.349, 0.686, 0.168], [0.393, 0.769, 0.189]])
            image = cv2.transform(image, filter)
        elif flag==12:  #Mexican
            filter = np.array([[0,0,-1,0,0],[0,-1,-2,-1,0],[-1,-2,16,-2,-1],[0,-1,-2,-1,0],[0,0,-1,0,0]])
            image = cv2.filter2D(image, -1, filter)
        elif flag==13:
            gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            r, c = gray_img.shape
            x = np.zeros((r, c, 8), dtype=np.uint8)
            x[:, :, bitLevel] = 2 ** bitLevel
            r = np.zeros((r, c, 8), dtype=np.uint8)
            r[:, :, bitLevel] = cv2.bitwise_and(gray_img, x[:, :, bitLevel])
            mask = r[:, :, bitLevel] > 0
            r[mask] = 255
            img = r[:, :, bitLevel]
            image = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif flag==14:
            filter = np.array(customFilter)
            image = cv2.filter2D(image, -1, filter)
        return image

    def Histogram(self, image, type, flag):
        if flag==1: #Equalize
            img_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
            image = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
        elif flag==2:
            img_lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            img_lab[:,:,0] = clahe.apply(img_lab[:,:,0])
            image = cv2.cvtColor(img_lab, cv2.COLOR_LAB2BGR)
        image = self.ConvertColor(type, image)
        return image

    def CropImage(self, image, coords):
        return image[min(coords[1], coords[3]):max(coords[1], coords[3])+1, min(coords[0], coords[2]):max(coords[0], coords[2])+1]

    def SaveImage(self, filename, image):
        return cv2.imwrite(filename, image)

    def LoadImage(self, filepath):
        return cv2.imread(filepath)

    def ResizeImage(self, image, dim):
        return cv2.resize(image, (dim[0], dim[1]))

    def ConvertColor(self, type, image):
        if type==0:
            return image
        elif type==1:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        elif type==2:
            return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        elif type==3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)[:,:,0]
        elif type==4:
            return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)[:,:,1]
        elif type==5:
            return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)[:,:,2]
        elif type==6:
            return cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
        elif type==7:
            return cv2.cvtColor(image, cv2.COLOR_BGR2HLS)[:,:,1]
        elif type == 8:
            return cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        elif type == 9:
            return cv2.cvtColor(image, cv2.COLOR_BGR2LUV)
        elif type == 10:
            return cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
        elif type == 11:
            return cv2.cvtColor(image, cv2.COLOR_BGR2XYZ)

    def OverlayImage(self, image, background, coords):
        top, bottom, left, right = coords[1], coords[1] + image.shape[0], coords[0], coords[0] + image.shape[1]
        if left>background.shape[1] or right<0 or top>background.shape[0] or bottom<0:
            return background
        if left<0:
            image = self.CropImage(image, (abs(left), 0, image.shape[1], image.shape[0]))
            left = 0
        if right>background.shape[1]:
            image = self.CropImage(image, (0, 0, image.shape[1]-(right-background.shape[1])-1, image.shape[0]))
            right = background.shape[1]
        if top<0:
            image = self.CropImage(image, (0, abs(top), image.shape[1], image.shape[0]))
            top = 0
        if bottom>background.shape[0]:
            image = self.CropImage(image, (0, 0, image.shape[1], image.shape[0]-(bottom-background.shape[0])-1))
            bottom = background.shape[0]
        background[top:bottom, left:right] = image
        return background

    def RotateImage(self, image, coords, index):
        if index < 4:
            ang = 0
            lst = []
            center = (coords[0] + image.shape[1] / 2, coords[1] + image.shape[0] / 2)
            if index == 1:
                ang = -90, 3
            elif index == 2:
                ang = 90, 1
            elif index == 3:
                ang = 180, 2
            M = cv2.getRotationMatrix2D(center, ang[0], 1)
            coordes = np.array([[coords[0], coords[1], 1], [coords[0] + image.shape[1], coords[1], 1], [coords[0] + image.shape[1], coords[1] + image.shape[0], 1], [coords[0], coords[1] + image.shape[0], 1]])
            for coord in coordes:
                lst.append(np.array(np.round(M.dot(coord), 0)).astype(int).tolist())
            coords = (min(lst)[0], min(lst)[1], max(lst)[0],max(lst)[1])
            image = np.rot90(image, ang[1]).copy()
        else:
            if index == 4:
                image = cv2.flip(image, 0)  # flip vertical
            elif index == 5:
                image = cv2.flip(image, 1)  # flip horizontal
        return image, coords

    def drawPrimitive(self, image, coords, type, color=(255,255,255), thick=None):      # dotted square, line, filled-square, square,
        if type == 1:
            color = (random.randint(5,250),random.randint(5,250),random.randint(5,250))
            width = 5
            thick = 1
            LR, UD, dst = self.calcRegion(coords)
            if sum(dst) == 0:
                return
            gap = dst[0] / width
            for i in range(math.ceil(gap / 2)):
                cv2.line(image, (coords[0] + width * 2 * LR * i, coords[1]), (coords[0] + width * 2 * LR * i + width * LR, coords[1]), color, thick, cv2.LINE_AA)
                cv2.line(image, (coords[2] + width * 2 * LR * i * -1, coords[3]), (coords[2] + width * 2 * LR * i * -1 + width * LR * -1, coords[3]), color, thick, cv2.LINE_AA)
            gap = dst[1] / width
            for i in range(math.ceil(gap / 2)):
                cv2.line(image, (coords[0], coords[1] + width * 2 * UD * i), (coords[0], coords[1] + width * 2 * UD * i + width * UD), color, thick, cv2.LINE_AA)
                cv2.line(image, (coords[2], coords[3] + width * 2 * UD * i * -1), (coords[2], coords[3] + width * 2 * UD * i * -1 + width * UD * -1), color, thick, cv2.LINE_AA)
        elif type==2:
            color = (150, 150, 150)
            width = 2
            LR, UD, dst = self.calcRegion(coords)
            gap = dst[0] / width
            for i in range(math.ceil(gap / 2)):
                cv2.line(image, (coords[0] + width * 2 * LR * i, coords[1]), (coords[0] + width * 2 * LR * i + width * LR, coords[1]), color, 1, cv2.LINE_AA)
            gap = dst[1] / width
            for i in range(math.ceil(gap / 2)):
                cv2.line(image, (coords[0], coords[1] + width * 2 * UD * i), (coords[0], coords[1] + width * 2 * UD * i + width * UD), color, 1, cv2.LINE_AA)
        elif type == 3:
            cv2.line(image, (coords[0], coords[1]), (coords[2], coords[3]), color, thick, cv2.LINE_AA)
        elif type == 5:
            cv2.rectangle(image, (coords[0], coords[1]), (coords[2], coords[3]), color, thick, cv2.LINE_AA)
        elif type == 4:
            center, radius = self.recalc_Center_Radius(coords)
            cv2.circle(image, center, max(radius), color, thick, cv2.LINE_AA)
        elif type == 6:
            cv2.polylines(image, [self.Triangle(coords)], True, color, thick, cv2.LINE_AA)
        elif type == 8:
            cv2.fillPoly(image, [self.Triangle(coords)], color)
        elif type == 7:
            cv2.polylines(image, [self.Diamond(coords)], True, color, thick, cv2.LINE_AA)
        elif type == 9:
            cv2.fillPoly(image, [self.Diamond(coords)], color)


    def drawText(self, image, text, coords, fontstyle, scale, color, thick):
        font = None
        if fontstyle == 0:
            font = cv2.FONT_HERSHEY_COMPLEX
        elif fontstyle == 1:
            font = cv2.FONT_HERSHEY_COMPLEX_SMALL
        elif fontstyle == 2:
            font = cv2.FONT_HERSHEY_DUPLEX
        elif fontstyle == 3:
            font = cv2.FONT_HERSHEY_PLAIN
        elif fontstyle == 4:
            font = cv2.FONT_HERSHEY_SCRIPT_COMPLEX
        elif fontstyle == 5:
            font = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
        elif fontstyle == 6:
            font = cv2.FONT_HERSHEY_TRIPLEX
        elif fontstyle == 7:
            font = cv2.FONT_ITALIC
        cv2.putText(image, text, coords, font, scale, color, thick)

    def recalc_Center_Radius(self, coords):
        LR, UD, dst = self.calcRegion(coords)
        radius = [dst[0]//2, dst[1]//2]
        center = (int(coords[0]+radius[0]*LR), int(coords[1]+radius[1]*UD))
        return center, radius

    def Triangle(self, coords):
        center, radius = self.recalc_Center_Radius(coords)
        c = [center[0], center[1]-radius[1]]
        b = [center[0] +radius[0], center[1]+radius[1]]
        a = [center[0] -radius[0], center[1]+radius[1]]
        return np.array([a,b,c], np.int32)

    def Diamond(self, coords):
        center, radius = self.recalc_Center_Radius(coords)
        return np.array([[center[0]-radius[0], center[1]], [center[0], center[1]-radius[1]], [center[0]+radius[0], center[1]], [center[0], center[1]+radius[1]]], np.int32)


    def ReLocateCoords(self, coords):
        LR, UD, dst = self.calcRegion(coords)
        if LR==-1:
            coords[0] -= dst[0]
            coords[2] += dst[0]
        if UD == -1:
            coords[1] -= dst[1]
            coords[3] += dst[1]
        return coords


    def calcRegion(self, coords):
        LR = UD = 0
        dst = [0, 0]
        x1 = coords[0]
        y1 = coords[1]
        x2 = coords[2]
        y2 = coords[3]
        if x2 < x1:
            LR = -1
            dst[0] = x1 - x2
        elif x2 > x1:
            LR = 1
            dst[0] = x2 - x1
        if y2 < y1:
            UD = -1
            dst[1] = y1 - y2
        elif y2 > y1:
            UD = 1
            dst[1] = y2 - y1
        return LR, UD, dst

    def Color_picker(self, color, wid=(10,20), hsv=None):
        image = np.zeros((500, 500, 3), np.uint8)
        image[:] = color
        if hsv:
            image = cv2.cvtColor(image.copy(), cv2.COLOR_HSV2BGR)
        if wid[0]>0:
            self.drawPrimitive(image, (int(500*.01), int(500*.01), int(500*.99), int(500*.99)), 5, (0,0,0), wid[0])
        if wid[1]>0:
            self.drawPrimitive(image, (int(500*.1), int(500*.1), int(500*.9), int(500*.9)), 5, (255,255,255), wid[1])
        return image

class HistogramPlot(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.setLayout(QVBoxLayout())
        self.canvas = PlotCanvas()
        self.layout().addWidget(self.canvas)

    def Plot(self, image):
        self.canvas.plot(image)

class PlotCanvas(FigureCanvas):
    def __init__(self):
        fig = Figure(figsize=(4, 4), dpi=72)
        FigureCanvas.__init__(self, fig)
        self.axes = fig.add_subplot(111)
        self.axes.axis('off')
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plot(self, image):
        self.axes.clear()
        self.axes.hist(image.ravel(), 256, [0, 256], color='black')
        if len(image.shape)==3:
            color = ('b', 'g', 'r')
            for i, col in enumerate(color):
                histr = cv2.calcHist([image], [i], None, [256], [0, 256])
                self.axes.plot(histr, color=col)
        self.axes.set_ylim(ymin=0)
        self.axes.set_xlim(xmin=0, xmax=256)
        self.axes.set_position([0, 0, 1, 1])
        self.draw()