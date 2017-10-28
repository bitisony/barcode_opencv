#!/usr/bin/env python
import sys
import os
import os.path
import cv2
import numpy as np
import getopt
DEBUG = False
output_file = ""
img_file  = ""
th_int = 127
long_option = ["help", "debug", "input", "output", "threshold"]
opts,args = getopt.getopt(sys.argv[1:], "hdi:o:t:", long_option)
for opt,arg in opts :
    if opt in ("-i", "--input") :
        img_file = arg
        if False == os.path.exists(img_file)  :
            print "Error: Image file \"%s\" don't exist!" % img_file
            sys.exit(-1)
    elif opt in ("-o", "--output") :
        output_file = arg
    elif opt in ("-d", "--debug") :
        DEBUG = True
    elif opt in ("-t", "--threshold") :
        th_int = int(arg)
if "" == img_file :
    sys.exit(-2)

img = cv2.imread(img_file, cv2.IMREAD_UNCHANGED)
gray = img
if len(img.shape) == 3 :
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ret,th_img = cv2.threshold(gray, th_int, 255,cv2.THRESH_BINARY)

if  "" ==  output_file :
    base_name = os.path.basename(img_file)
    pure_name = os.path.splitext(base_name)[0]
    output_file = pure_name + ".txt"
print "Convert binary file format to %s" % output_file
# cv2.imwrite(output_file, th_img)
height,width = th_img.shape
allLines = []
for h in range(height) :
    line = ""
    for w in range(width) :
        if th_img[h,w] > 0 :
            line += "0"
        else :
            line += "1"
    line += "\n"
    allLines.append(line)

f = open(output_file, "w")
f.writelines(allLines)
f.close()

if DEBUG :
    cv2.imshow("origin", img)
    cv2.imshow("gray", gray)
    th_fname = "threshold(%s)" % th_int
    cv2.imshow(th_fname, th_img)
    
    key = cv2.waitKey(-1) & 0xff
    cv2.destroyAllWindows()

