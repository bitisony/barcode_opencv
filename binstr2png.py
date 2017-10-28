#!/usr/bin/env python
import sys
import os
import os.path
import time
import numpy as np
import cv2
import getopt

DEBUG = False
DEF_IMG_HEIGHT = 121

opts,args = getopt.getopt(sys.argv[1:], "hdwi:o:", ["help", "output", "input"])
# print opts,args
str_bin_arr = []
input_file = ""
def_output = time.strftime("%Y%m%d%H%M%S", time.localtime())
output_file = "img" + def_output + ".png"
print "output:", output_file
is_width_arr = False

for opt,arg in opts :
    # print opt,arg
    if opt in ('-h', "--help") :
        print "Help print"
    elif opt == "-d" :
        DEBUG = True
        # print "DEBUG =", DEBUG
    elif opt == "-w" :
        is_width_arr = True
    elif opt in ("-i","--input"):
        input_file = arg
        if os.path.exists(input_file) :
            in_f = open(input_file, "r")
            lines = in_f.readlines()
            in_f.close()
            str_bin_arr = [line.strip() for line in lines ]
        else :
            print "Error: input file path don\'t exist!"
            sys.exit(-1)
    elif opt in ("-o", "--output"):
        output_file = arg
    else :
        pass

if DEBUG :
    print args

if args == [] and "" == input_file :
    print "Error: No argument"
    sys.exit(-1)
if "" == input_file :
    line = ""
    if is_width_arr :
        space_bar_tbl = ["0","1"]
        str_width = args[0]
        for i in range(len(str_width)) :
            # print "i=", i, str_width[i]
            width = int(str_width[i])
            if 0 != width :
                line += "".center(width, space_bar_tbl[i%2])
    else :
        line = args[0]
    pad_space = "".center(4,"0")
    line = pad_space + line + pad_space
    height = DEF_IMG_HEIGHT
    for row in range(height) :
        str_bin_arr.append(line)
if is_width_arr and "" != input_file :
    print "Error: don't support width string from file"
    sys.exit(-1)

rows = []
if [] != str_bin_arr :
    height = len(str_bin_arr)
    for h in range(height) :
        line = str_bin_arr[h]
        if DEBUG :
            print line
        cols = []
        for idx in range(len(line)) :
            if "1" == line[idx] :
                cols.append(0)
            else :
                cols.append(255)
        if DEBUG :
            print cols
        rows.append(cols)

gray_img = np.array(rows, dtype=np.uint8)
print gray_img
cv2.imwrite(output_file, gray_img)
# cv2.imshow(output_file,gray_img)
# key = cv2.waitKeyEx(-1) & 0xff
# cv2.destroyAllWindows()
