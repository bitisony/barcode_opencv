import os
import os.path
import time
import numpy as np
import cv2 as cv

# CHECK ASCII   WIDTH           BARCODE         CHECK   ASCII   WIDTH           BARCODE
# VALUE	CHAR    ENCODING        ENCODING	VALUE	CHAR	ENCODING	ENCODING
# 0	0	NNNWWNWNN	101001101101	22	M	WNWNNNNWN	110110101001
# 1	1	WNNWNNNNW	110100101011	23	N	NNNNWNNWW	101011010011
# 2	2	NNWWNNNNW	101100101011	24	O	WNNNWNNWN	110101101001
# 3	3	WNWWNNNNN	110110010101	25	P	NNWNWNNWN	101101101001
# 4	4	NNNWWNNNW	101001101011	26	Q	NNNNNNWWW	101010110011
# 5	5	WNNWWNNNN	110100110101	27	R	WNNNNNWWN	110101011001
# 6	6	NNWWWNNNN	101100110101	28	S	NNWNNNWWN	101101011001
# 7	7	NNNWNNWNW	101001011011	29	T	NNNNWNWWN	101011011001
# 8	8	WNNWNNWNN	110100101101	30	U	WWNNNNNNW	110010101011
# 9	9	NNWWNNWNN	101100101101	31	V	NWWNNNNNW	100110101011
# 10	A	NNWWNNWNN	110101001011	32	W	WWWNNNNNN	110011010101
# 11	B	NNWNNWNNW	101101001011	33	X	NWNNWNNNW	100101101011
# 12	C	WNWNNWNNN	110110100101	34	Y	WWNNWNNNN	110010110101
# 13	D	NNNNWWNNW	101011001011	35	Z	NWWNWNNNN	100110110101
# 14	E	WNNNWWNNN	110101100101	36	-	NWNNNNWNW	100101011011
# 15	F	NNWNWWNNN	101101100101	37	.	WWNNNNWNN	110010101101
# 16	G	NNNNNWWNW	101010011011	38	SPACE	NWWNNNWNN	100110101101
# 17	H	WNNNNWWNN	110101001101	39	$	NWNWNWNNN	100100100101
# 18	I	NNWNNWWNN	101101001101	40	/	NWNWNNNWN	100100101001
# 19	J	NNNNWWWNN	101011001101	41	+	NWNNNWNWN	100101001001
# 20	K	WNNNNNNWW	110101010011	42	%	NNNWNWNWN	101001001001
# 21	L	NNWNNNNWW	101101010011	n/a	*	NWNNWNWNN	100101101101

CODE39_SART_CHAR = 43
CODE39_STOP_CHAR = 43
CODE39_BIN_WIDTH_MAX = 2
CODE39_WIDTH = 12
CODE39_CHARACTERS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-. $/+%*" 
CODE39_ENCODINGS = [ \
        "101001101101", \
        "110100101011", \
        "101100101011", \
        "110110010101", \
        "101001101011", \
        "110100110101", \
        "101100110101", \
        "101001011011", \
        "110100101101", \
        "101100101101", \
        "110101001011", \
        "101101001011", \
        "110110100101", \
        "101011001011", \
        "110101100101", \
        "101101100101", \
        "101010011011", \
        "110101001101", \
        "101101001101", \
        "101011001101", \
        "110101010011", \
        "101101010011", \
        "110110101001", \
        "101011010011", \
        "110101101001", \
        "101101101001", \
        "101010110011", \
        "110101011001", \
        "101101011001", \
        "101011011001", \
        "110010101011", \
        "100110101011", \
        "110011010101", \
        "100101101011", \
        "110010110101", \
        "100110110101", \
        "100101011011", \
        "110010101101", \
        "100110101101", \
        "100100100101", \
        "100100101001", \
        "100101001001", \
        "101001001001", \
        "100101101101", \
        ]

def code39_decode(decode_str) :
    # decode = "P23507824"
    print "input :", decode_str
    decode = ""
    idx = 0
    bin_width = 0
    str_len = len(decode_str)
    code_s = ""
    code_cnt = 0
    code_dir = 1
    symbols = []
    symbol_idx = 0
    symbols_cnt = 0
    while idx < str_len :
        # skip "0 , code39 always encode starting with bar"
        if "" == code_s :
            if "0" ==  decode_str[idx] :
                idx = idx + 1
                continue

        bin_width = 1
        # print "bin_width :", bin_width
        code_s = code_s + decode_str[idx]
        # print "code_s[", code_cnt, "] =", code_s
        code_cnt = code_cnt + 1
        if "1" == decode_str[idx] :
            while ((idx + 1) < str_len) and ("1" == decode_str[idx + 1]):
                idx = idx + 1
                bin_width = bin_width + 1
                # print "bin_width :", bin_width
                if bin_width <= CODE39_BIN_WIDTH_MAX :
                    code_s = code_s + decode_str[idx]
                    # print "code_s[", code_cnt, "] =", code_s
                    code_cnt = code_cnt + 1
                else :
                    print "bin_width :", bin_width

        else :
            while  ((idx + 1) < str_len) and ("0" == decode_str[idx + 1]) :
                idx = idx + 1
                bin_width = bin_width + 1
                # print "bin_width :", bin_width
                if bin_width <= CODE39_BIN_WIDTH_MAX :
                    code_s = code_s + decode_str[idx]
                    # print "code_s[", code_cnt, "] =", code_s
                    code_cnt = code_cnt + 1
                else :
                    print "Warning: bin_width =", bin_width

        # forward/reveres
        if len(code_s) == CODE39_WIDTH : 
            print "code_s :", code_s
            if 0 == symbols_cnt :
                # check if is reverse or not
                reverse = code_s[::-1]
                if  code_s == CODE39_ENCODINGS[CODE39_SART_CHAR] :
                    code_dir = 1
                elif reverse == CODE39_ENCODINGS[CODE39_STOP_CHAR] :
                    code_dir = 0
                else :
                    code_dir = -1
            # code39 format error, return empty string
            if code_dir < 0 :
                return ""
            symbols_cnt = symbols_cnt + 1

            tmp_str = code_s
            if 0 == code_dir :
                tmp_str = code_s[::-1]
            symbol_idx = 0
            for s in CODE39_ENCODINGS :
                if s == tmp_str :
                    symbols.append(symbol_idx)
                symbol_idx = symbol_idx + 1
            code_s = ""
            code_cnt = 0
        idx = idx + 1
    # end while idx < str_len :
    decode = "" 
    if CODE39_SART_CHAR != symbols[0] :
        return ""
    if CODE39_STOP_CHAR != symbols[-1] :
        return ""
    for sym in symbols :
        decode = decode + CODE39_CHARACTERS[sym]
    print "code_dir=  ", code_dir
    if 0 == code_dir :
        decode = decode[::-1]
    return decode

