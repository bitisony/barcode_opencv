#!/usr/bin/env python
# str_bin = "1111000011100000000000011111111000011110000111111111111111000011110000111100001111111111111110000000000001111111100001111000000000000111111100001111000000000000111111100000111000011110000111100001111111100011111111000000001111111111110000111000000001111111100000000111111110000111000001111111111100000000111100000000111111111110000111111110000111111110000000011100001111"
import sys
import os
import os.path
import time
import numpy
import cv2
import getopt

DEBUG =  False

MIN_WIDTH_NUM = 17
BAR_VS_SPACE_WIDTH_THRESHOLD = 5

def barcode_decode (str_bin) :
    if None == str_bin :
        return None
    start_idx = 0
    end_idx = 0
    width_idx = 0 
    bin_arr = ["0", "1"]
    encode_width_arr = []
    str_encode = str_bin.strip("0")
    encode_len = len(str_encode)
    while end_idx < encode_len :
        end_idx = str_encode.find(bin_arr[width_idx % 2], start_idx)
        if end_idx < 0 :
            end_idx = encode_len
            width = end_idx - start_idx
            encode_width_arr.append(width)
            break
        width = end_idx - start_idx
        encode_width_arr.append(width)
        width_idx += 1
        start_idx = end_idx
    num_en_width = len(encode_width_arr)
    if DEBUG :
        print encode_width_arr,"len =", num_en_width
    start_idx = 0
    end_idx = num_en_width
    ratio_cnt = 0
    match_arr = []
    while start_idx < (num_en_width - MIN_WIDTH_NUM -1) :
        idx = start_idx
        if DEBUG :
            print "idx =", idx
        while idx < num_en_width -1 :
            ratio = encode_width_arr[idx + 1] / encode_width_arr[idx] 
            if ratio < 1 :
                ratio = encode_width_arr[idx] / encode_width_arr[idx + 1] 
            if ratio >= BAR_VS_SPACE_WIDTH_THRESHOLD :
                if ratio_cnt >= MIN_WIDTH_NUM :
                    end_idx = idx + 1
                    match_arr.append([start_idx,end_idx])
                ratio_cnt = 0
                print "pre start_idx =", start_idx
                start_idx = idx + 2
                if encode_width_arr[idx] > encode_width_arr[idx + 1] :
                    start_idx = idx + 1
                if 0 != start_idx % 2 :
                    start_idx += 1
                print "next start_idx =", start_idx
                break
            else :
                ratio_cnt += 1
                idx += 1
        if DEBUG :
            print "After inc, idx =", idx
        if idx >= (num_en_width - 2) :
            print "Last match_arr.append" 
            match_arr.append([start_idx,num_en_width])
            break

    candidate_arr = []
    for match in match_arr :
        start_idx,end_idx= match
        match_res = encode_width_arr[start_idx : end_idx]
        candidate_arr.append(match_res)
        if DEBUG :
            print match
            print match_res
    return candidate_arr

if __name__ == "__main__" :
    # print sys.argv
    if len(sys.argv) < 2 :
        sys.exit(-1)
    opts,args = getopt.getopt(sys.argv[1:], "hd", ["help"])
    print opts,args
    for opt,arg in opts :
        print "opt:",opt
        if opt in ('-h', "--help") :
            print "Help pring"
        elif opt == "-d" :
            DEBUG = True
            print "DEBUG =", DEBUG
        else :
            pass

    if args == [] :
        print "Error: No argument"
        sys.exit(-1)
    if DEBUG :
        print args[0]
    result = barcode_decode(args[0])
    if None != result :
        for match in result :
            print match

