#!/usr/bin/env python
import sys
import os
import os.path
import time
import numpy
import cv2
import argparse
import decode
import getopt

DEBUG = False
LEFT_GUARD = "101"
RIGHT_GUARD = "101"
RIGHT_GUARD_UPCE = "010101"
CENTER_GUARD = "01010"
CODE_LEN = 7
EAN13_SYMBOL_NUM = 12
UPC_E_SYMBOL_NUM = 6
EAN8_SYMBOL_NUM = 8
CELL_REPEAT_MAX = 4
MIN_INVERT_CHANGE = 4

EAN_CODE_LENGTH_TBL = [EAN13_SYMBOL_NUM, EAN8_SYMBOL_NUM, UPC_E_SYMBOL_NUM]
EAN_ENCODES_INVERT_TBL = [
        EAN13_SYMBOL_NUM * MIN_INVERT_CHANGE + 11, 
        EAN8_SYMBOL_NUM * MIN_INVERT_CHANGE + 11, 
        UPC_E_SYMBOL_NUM * MIN_INVERT_CHANGE + 9]

## DIGIT	LEFT-HAND ENCODING	RIGHT-HAND ENCODING
## ODD PARITY (A)	EVEN PARITY (B)	ALL CHARACTERS
## 0	0001101	0100111	1110010
## 1	0011001	0110011	1100110
## 2	0010011	0011011	1101100
## 3	0111101	0100001	1000010
## 4	0100011	0011101	1011100
## 5	0110001	0111001	1001110
## 6	0101111	0000101	1010000
## 7	0111011	0010001	1000100
## 8	0110111	0001001	1001000
## 9	0001011	0010111	1110100

# CHECK     NUMBER SYSTEM 0 NUMBER SYSTEM 1
# CHARACTER ENCODING	    ENCODING
# 0	    EEEOOO	    OOOEEE
# 1	    EEOEOO	    OOEOEE
# 2	    EEOOEO	    OOEEOE
# 3	    EEOOOE	    OOEEEO
# 4	    EOEEOO	    OEOOEE
# 5	    EOOEEO	    OEEOOE
# 6	    EOOOEE	    OEEEOO
# 7	    EOEOEO	    OEOEOE
# 8	    EOEOOE	    OEOEEO
# 9	    EOOEOE	    OEEOEO

UPC_E_PARITY_TBL = [
        ["EEEOOO",	    "OOOEEE"],
        ["EEOEOO",	    "OOEOEE"],
        ["EEOOEO",	    "OOEEOE"],
        ["EEOOOE",	    "OOEEEO"],
        ["EOEEOO",	    "OEOOEE"],
        ["EOOEEO",	    "OEEOOE"],
        ["EOOOEE",	    "OEEEOO"],
        ["EOEOEO",	    "OEOEOE"],
        ["EOEOOE",	    "OEOEEO"],
        ["EOOEOE",	    "OEEOEO"],
        ]

EAN13_DECODE_TBL = [ \
["0001101", "0100111", "1110010"], \
["0011001", "0110011", "1100110"], \
["0010011", "0011011", "1101100"], \
["0111101", "0100001", "1000010"], \
["0100011", "0011101", "1011100"], \
["0110001", "0111001", "1001110"], \
["0101111", "0000101", "1010000"], \
["0111011", "0010001", "1000100"], \
["0110111", "0001001", "1001000"], \
["0001011", "0010111", "1110100"], \
]

def ean_decode(str_bin) :
# step 1. find left guard
    if DEBUG :
        print "input:", str_bin
    str_encode = str_bin.strip("0")
    encode_len = len(str_encode)
    min_len = 6 * CODE_LEN + 9
    if encode_len < min_len :
        if DEBUG :
            print "Error: Invalid encoding length!"
        return None
    encode_width_arr = []
    end_idx = 0
    start_idx = 0
    width_idx = 0 
    bin_arr = ["1", "0"]
    while end_idx < encode_len :
        end_idx = str_encode.find(bin_arr[(width_idx + 1)% 2], start_idx)
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
    ean_normal_len = 12 * MIN_INVERT_CHANGE + 11
    upc_short_len = (UPC_E_SYMBOL_NUM  * MIN_INVERT_CHANGE) + 9
    if DEBUG :
        print "origin:", encode_width_arr, "num_width_arr:", num_en_width
    found = False
    for valid_len in EAN_ENCODES_INVERT_TBL :
        if num_en_width == valid_len :
            found = True
            if DEBUG :
                print "valid_len =", num_en_width
            break
    if found == False :
        if DEBUG :
            print "encode_length:", num_en_width
        return None
    # left guard check
    left_guard_sum = 0
    for idx in range(3) :
        left_guard_sum += encode_width_arr[idx]
    avg_width = left_guard_sum / 3
    if DEBUG :
        print "avg_width:",avg_width
    tmp_left_guard = ""
    for idx in range(3) :
        width = encode_width_arr[idx] / avg_width
        tmp_left_guard += "".center(width, bin_arr[idx%2])
    if DEBUG :
        print tmp_left_guard
    if tmp_left_guard != LEFT_GUARD :
        if DEBUG :
            print "Error: Invalid left guard!"
        return None

    tmp_right_guard = ""
    for idx in range(3) :
        width = encode_width_arr[num_en_width - idx -1] / avg_width
        tmp_right_guard += "".center(width, bin_arr[idx%2])
    if DEBUG :
        print tmp_right_guard
    if tmp_right_guard != RIGHT_GUARD :
        if DEBUG :
            print "Error: Invalid right guard!"
        return None

    # copy to pure encoding width to dst_en_arr
    left_start = 3
    ena_half_len = (EAN13_SYMBOL_NUM / 2) * MIN_INVERT_CHANGE
    if EAN_ENCODES_INVERT_TBL[1] == num_en_width :
        ena_half_len = (EAN8_SYMBOL_NUM / 2) * MIN_INVERT_CHANGE
    if DEBUG :
        print "ena_half_len", ena_half_len
    left_end = left_start + ena_half_len
    dst_en_arr = encode_width_arr[left_start : left_end]
    if num_en_width > EAN_ENCODES_INVERT_TBL[2] :
        right_base = 8 + ena_half_len
        if DEBUG :
            print "right_base =", right_base
        for idx in range(ena_half_len) :
            dst_en_arr.append(encode_width_arr[right_base + idx])
    pure_encode_len = len(dst_en_arr)
    if DEBUG :
        print dst_en_arr, pure_encode_len
    # adjust wdith to align avg_width
    for idx in range(pure_encode_len) :
        if dst_en_arr[idx] < avg_width :
            dst_en_arr[idx] = avg_width
    for idx in range(pure_encode_len) :
        if (dst_en_arr[idx] % avg_width) != 0 :
            offset = idx % MIN_INVERT_CHANGE
            base = (idx / MIN_INVERT_CHANGE) * MIN_INVERT_CHANGE
            sym_sum = 0
            for ii in range(MIN_INVERT_CHANGE) :
                if offset != ii :
                    sym_sum += dst_en_arr[base + ii]
            code_len = sym_sum / avg_width
            part_len = CODE_LEN - code_len
            rest_len = dst_en_arr[idx] / avg_width
            if DEBUG :
                print "code_len:",code_len, "part_len:",part_len, "rest_len:", rest_len
            # check if add or insert width
            if (rest_len + code_len) == CODE_LEN :
                dst_en_arr[idx] = avg_width * rest_len
            else :
                dst_en_arr[idx] = avg_width * (rest_len + 1)
                rest_len = dst_en_arr[idx] / avg_width
                if DEBUG :
                    print "code_len:",code_len, "rest_len:", rest_len
                if (rest_len + code_len) != CODE_LEN :
                    if DEBUG :
                        print "Error: encode length!"
                    return None

    if DEBUG :
        print "pure encoding:", dst_en_arr, pure_encode_len
    str_encode = ""
    str_encode_arr = []
    for idx in range(pure_encode_len) :
        if idx < (UPC_E_SYMBOL_NUM * MIN_INVERT_CHANGE) :
            str_encode += "".center(dst_en_arr[idx]/avg_width, bin_arr[(idx + 1)%2])
        else :
            str_encode += "".center(dst_en_arr[idx]/avg_width, bin_arr[(idx)%2])
        if 0 == ((idx+1) % MIN_INVERT_CHANGE) :
            str_encode_arr.append(str_encode)
            if DEBUG :
                print str_encode
            str_encode = ""
    str_ean13_decode = ""
    dig_arr_ean13_decode = []
    for str_encode in str_encode_arr :
        digit_line = 0
        found = False
        for encode_digits in EAN13_DECODE_TBL :
            for number in encode_digits :
                if  str_encode == number :
                    str_ean13_decode += str(digit_line)
                    dig_arr_ean13_decode.append(digit_line)
                    found = True
                    break
            if found :
                break
            digit_line = digit_line + 1
        if found :
            pass
        else :
            return None
    found = False
    cur_decode_len = len(dig_arr_ean13_decode) 
    for valid_len in EAN_CODE_LENGTH_TBL :
        if cur_decode_len == valid_len :
            found = True
            if DEBUG :
                print "valid_len =", num_en_width
            break
    if found == False :
        if DEBUG :
            print "Error: Invalid encode length!"
        return None
    print "digit arr:", str_ean13_decode, ", length:",len(str_ean13_decode)
    check_sum = 0
    for i in range(len(dig_arr_ean13_decode) - 1) :
        if 0 == (i%2) :
            check_sum += dig_arr_ean13_decode[i] * 3
        else :
            check_sum += dig_arr_ean13_decode[i] * 1
    if len(dig_arr_ean13_decode) == EAN13_SYMBOL_NUM :
        check_digit = dig_arr_ean13_decode[-1]
        tmp_check_digit = 10 - (check_sum % 10)
        if tmp_check_digit == check_digit :
            # this is UPC-A symbols
            str_ean13_decode = "0" + str_ean13_decode
            pass
        else :
            check_sum += 7
            tmp_check_digit = 10 - (check_sum % 10)
            if tmp_check_digit != check_digit :
                return None
            # this is EAN13 standard symbols
            str_ean13_decode = "7" + str_ean13_decode
    elif len(dig_arr_ean13_decode) == EAN8_SYMBOL_NUM :
        check_digit = dig_arr_ean13_decode[-1]
        tmp_check_digit = 10 - (check_sum % 10)
        if tmp_check_digit != check_digit :
            return None
    elif len(dig_arr_ean13_decode) == UPC_E_SYMBOL_NUM :
        parity_style = ""
        for str_encode in str_encode_arr :
            if 0 == str_encode.count("1") % 2 :
                parity_style += "E"
            else :
                parity_style += "O"
        if DEBUG :
            print "Pariy Style:", parity_style
        found = False
        for num_system  in range(2) :
            for digit in range(10) :
                if parity_style == UPC_E_PARITY_TBL[digit][num_system] :
                    str_ean13_decode = str(num_system) + str_ean13_decode
                    str_ean13_decode += str(digit)
                    found = True
                    break
            if found :
                break
        if found :
            pass
        else :
            return None

    return  str_ean13_decode

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
    result = ean_decode(args[0])
    if None != result :
        print result

