#!/usr/bin/env python
import sys
import os
import os.path
import time
import numpy
import cv2
import argparse
import decode
import code39
import ean

if __name__ == "__main__" :
    DECODE_EAN_THRESHOLD_START = 100
    DECODE_EAN_THRESHOLD_END = 200
    DECODE_EAN_THRESHOLD_STEP = 5
    ap = argparse.ArgumentParser()
    ap.add_argument("-i","--image", required = True, help = "Path to image file")
    args = vars(ap.parse_args())
    
    img_file = args["image"]
    
    image = cv2.imread(img_file, cv2.IMREAD_UNCHANGED)
    height =  image.shape[0]
    width  =  image.shape[1]
    print "height =",height, " width =", width, len(image.shape)
    if len(image.shape) >= 3 :
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else :
        gray = image

    thn = DECODE_EAN_THRESHOLD_START
    while thn <= DECODE_EAN_THRESHOLD_END :
        ret,th_img = cv2.threshold(gray,thn,255,cv2.THRESH_BINARY)
        thn = thn + DECODE_EAN_THRESHOLD_STEP
    
        rows = []
        col= ""
        for h in range(height):
            col= ""
            for w in range(width):
                if th_img[h,w] > 0 :
                    col = col + "0"
                else :
                    col = col + "1"
            if col.count('0') == width :
                continue
            if col.count('1') == width :
                continue
            start = col.find("1")
            end = col.rfind("1")
            new_col = col[start : end + 1]
            # print new_col
            rows.append(new_col)
            col = ""
        nrow = len(rows)
        # tmp_row = rows[(nrow + 1)/2]
        find = False
        for tmp_row in rows :
            # print tmp_row
            # ean.DEBUG = True
            res = ean.ean_decode(tmp_row)
            if None != res :
                if len(res) > 0 :
                    find = True
                    print "Decoded:", res
                    break
            else :
                result = decode.barcode_decode(tmp_row)
                if None == result :
                    continue
                for widths in result :
                    str_decode = code39.c39_decode(widths)
                    if None != str_decode :
                        print "Code39 Decoded:", str_decode
                        find = True
                        break
                if find :
                    break
        if find :
            break
