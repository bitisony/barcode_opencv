#!/usr/bin/env python
import sys
import os
import os.path
import time
import numpy as np
import getopt

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
DEBUG = False
MIN_INVERT_CHANGE = 9
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
        "100101101101" \
        ]

C39_WIDTH_LST = [ \
        "111221211", \
        "211211112", \
        "112211112", \
        "212211111", \
        "111221112", \
        "211221111", \
        "112221111", \
        "111211212", \
        "211211211", \
        "112211211", \
        "112211211", \
        "112112112", \
        "212112111", \
        "111122112", \
        "211122111", \
        "112122111", \
        "111112212", \
        "211112211", \
        "112112211", \
        "111122211", \
        "211111122", \
        "112111122", \
        "212111121", \
        "111121122", \
        "211121121", \
        "112121121", \
        "111111222", \
        "211111221", \
        "112111221", \
        "111121221", \
        "221111112", \
        "122111112", \
        "222111111", \
        "121121112", \
        "221121111", \
        "122121111", \
        "121111212", \
        "221111211", \
        "122111211", \
        "121212111", \
        "121211121", \
        "121112121", \
        "111212121", \
        "121121211"\
        ]

def c39_format_width(onecode_widths, unit_width):
    if len(onecode_widths) != MIN_INVERT_CHANGE :
        if DEBUG :
            print "Error: widths list length failed!"
            print onecode_widths
        return None
    avg_width = unit_width
    if (unit_width == 0) :
        flt_avg_width = (sum(onecode_widths) * 1.0 / CODE39_WIDTH) + 0.25
        avg_width = int(flt_avg_width)
    elif unit_width > 0 :
        avg_width = unit_width
    else :
        return None
    non_aligned_lst = []
    widths_sum = 0
    for idx in range(MIN_INVERT_CHANGE) :
        if onecode_widths[idx] < avg_width :
            onecode_widths[idx] = avg_width
        if onecode_widths[idx] / avg_width > CODE39_BIN_WIDTH_MAX :
            onecode_widths[idx] = CODE39_BIN_WIDTH_MAX * avg_width
        if onecode_widths[idx] % avg_width != 0 :
            if (onecode_widths[idx] / avg_width + 1) > CODE39_BIN_WIDTH_MAX :
                onecode_widths[idx] = CODE39_BIN_WIDTH_MAX * avg_width
        if onecode_widths[idx] % avg_width != 0 :
            non_aligned_lst.append(idx)
        else :
            widths_sum += onecode_widths[idx]
    num_non_aligned = len(non_aligned_lst)
    if num_non_aligned == 0 :
        return onecode_widths
    if num_non_aligned == 1:
        idx = non_aligned_lst[0]
        onecode_widths[idx] = avg_width * CODE39_WIDTH - widths_sum
        return onecode_widths

    rest_check_sum = 0
    for var in range(num_non_aligned) :
        idx = non_aligned_lst[var]
        flt_multipled = 1.0 * onecode_widths[idx] % avg_width
        dealed_width = int(100 * flt_multipled + 26) / 100
        onecode_widths[idx] = dealed_width
        rest_check_sum += dealed_width
    if rest_check_sum + widths_sum != avg_width * CODE39_WIDTH:
        if DEBUG :
            print onecode_widths
            print "check_sum failed!"
        return None
    return onecode_widths

def c39_start_check(widths_list):
    start_widths = widths_list[0:9]
    start_widths = c39_format_width(start_widths, 0)
    if None == start_widths :
        return False
    avg_width = start_widths[0]
    width_tbl = [ width/avg_width for width in start_widths ]
    str_width_tbl = [str(width) for width in width_tbl ]
    str_widths = "".join(str_width_tbl)
    if DEBUG :
        print str_widths
    if str_widths == C39_WIDTH_LST[CODE39_SART_CHAR] :
        return True,avg_width
    return False,0

def c39_decode(widths_list) :
    num_widths = len(widths_list)
    if num_widths < 29 :
        return None
    if 9 != num_widths % 10 :
        return None
    chk_start,avg_width = c39_start_check(widths_list)
    if DEBUG :
        print "start symbol checked :", chk_start
    # checked the stop
    chk_stop,avg_width2 = c39_start_check(widths_list[-9 : ])
    if DEBUG :
        print "start symbol checked :", chk_stop
    if (avg_width == 0) or (avg_width != avg_width2) :
        return widths_list
    widths_step = MIN_INVERT_CHANGE + 1
    num_pure_code = (num_widths - 19) / widths_step
    str_decode_tbl = []
    for cnt in range(num_pure_code) :
        start = 10 + cnt * widths_step
        end = start + widths_step
        cur_code_widths = widths_list[start : end]
        if DEBUG :
            print cur_code_widths
        formated_widths = c39_format_width(cur_code_widths[0 : 9], avg_width)
        if None == formated_widths :
            return None
        width_tbl = [ width / avg_width for width in formated_widths ]
        str_width_tbl = [str(width) for width in width_tbl ]
        str_widths = "".join(str_width_tbl)
        str_decode_tbl.append(str_widths)
        if DEBUG :
            print str_widths
    num_c39_code = len(C39_WIDTH_LST)
    decode_res = ""
    for str_decode in str_decode_tbl :
        for idx in range(num_c39_code) :
            if str_decode == C39_WIDTH_LST[idx] :
                decode_res += CODE39_CHARACTERS[idx]
    return decode_res

if __name__ == "__main__" :
    import decode
    # print sys.argv
    if len(sys.argv) < 2 :
        sys.exit(-1)
    opts,args = getopt.getopt(sys.argv[1:], "hd", ["help"])
    # print opts,args
    for opt,arg in opts :
        # print "opt:",opt
        if opt in ('-h', "--help") :
            print "Help pring"
        elif opt == "-d" :
            DEBUG = True
            decode.DEBUG = True
            print "DEBUG =", DEBUG
        else :
            pass

    if args == [] :
        print "Error: No argument"
        sys.exit(-1)
    if DEBUG :
        print args[0]
    result = decode.barcode_decode(args[0])
    if None == result :
        sys.exit(-1)
    for widths in result :
        str_decode = c39_decode(widths)
        if None != str_decode :
            print "Decoded:", str_decode

