#!/usr/bin/env python
# str_bin = "1111000011100000000000011111111000011110000111111111111111000011110000111100001111111111111110000000000001111111100001111000000000000111111100001111000000000000111111100000111000011110000111100001111111100011111111000000001111111111110000111000000001111111100000000111111110000111000001111111111100000000111100000000111111111110000111111110000111111110000000011100001111"

EAN_MIN_WIDTH_NUM = 33 # 6 * 4 + 9
CODE39_MIN_WDITH_NUM = 9 * 3 # start + char + stop
CODE93_MIN_WDITH_NUM = 6 * 3 + 1 # start + char + stop + Termination
CODE128_MIN_WDITH_NUM  = 6 * 3 + 2

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
    return encode_width_arr

