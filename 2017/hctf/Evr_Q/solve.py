#!/usr/bin/env python2


# 1. xor every char with 0x76
# 2. xor chars [7, 14) w/ 0xad and other stuff 
# 3. xor chars [14, 21) w/ 0xbe and other stuff
# 4. xor chars [21, 28) w/ 0xef and other stuff

from pwn import *

def lshift(y, x):
    return x << y
def rshift(y, x):
    return x >> y
def _and(y, x):
    return y & x;
def _or(y, x):
    return y | x;
def _xor(y, x):
    return y ^ x;

def math7to14(char):
    return _or(
        rshift(1,
            _and(0xAA,
                _xor(0xad,
                    _xor(0x76, char)
                )
            )
        ),
        _and(0xAA,
            lshift(1,
                _xor(0xad,
                    _xor(0x76, char)
                )
            )
        )
    )

def math14to21(char):
    return _or(
        rshift(2,
            _and(0xcc,
                _xor(0xbe,
                    _xor(0x76, char)
                )
            )
        ),
        _and(0xcc,
            lshift(2,
                _xor(0xbe,
                    _xor(0x76, char)
                )
            )
        )
    )

def math21to28(char):
    return _or(
        rshift(4,
            _and(0xf0,
                _xor(0xef,
                    _xor(0x76, char)
                )
            )
        ),
        _and(0xf0,
            lshift(4,
                _xor(0xef, 
                    _xor(0x76, char)
                )
            )
        )
    )

#encoded flag address: 0x41b0dc
encoded_flag = list("\x1e\x15\x02\x10\rHHo\xdd\xddHdc\xd7.,\xfejm*\xf2o\x9aM\x8bK\xca\xcfN@F\x10GF\x0b")
flag = []
for c in encoded_flag:
    flag += [(chr(ord(c) ^ 0x76)) ]

for i in range(len(encoded_flag)):
    if 7 <= i < 14:
        for j in range(128):
            if math7to14(j) == ord(encoded_flag[i]):
                print("i: " + str(i) + " j: " + str(j) + " char: " +chr(j))
                flag[i] = chr(j)
    if 14 <= i < 21:
        for j in range(128):
            if math14to21(j) == ord(encoded_flag[i]):
                print("i: " + str(i) + " j: " + str(j) + " char: " +chr(j))
                flag[i] = chr(j)
    if 21 <= i < 28:
        for j in range(128):
            if math21to28(j) == ord(encoded_flag[i]):
                print("i: " + str(i) + " j: " + str(j) + " char: " +chr(j))
                flag[i] = chr(j)

print(''.join(c for c in flag))
# hctf{>>D55_CH0CK3R_B0o0M!-5e860f10}
