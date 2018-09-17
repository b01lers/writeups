#!/usr/bin/env python2
import pyavltree
from pwn import *


p = remote('misc.chal.csaw.io', 9001)
p.recvline()
nums = p.recvline().split(',')
nums = [int(num) for num in nums]

print(nums)

tree = pyavltree.AVLTree()
for elem in nums:
    tree.insert(elem)

n = tree.rootNode
l = [n]

n = tree.preorder(n)

print(n)

out = (','.join([str(elem) for elem in n]))
print(out)
p.sendline(out)

p.interactive()

