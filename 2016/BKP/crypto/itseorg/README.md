# BKP : Itseorg

#### Author: GSAir

**Description**:
> ltseorg - crypto: make some (charlie)hash collisions! ltseorg.bostonkey.party 5555


This challenge was designed based on a hash function: [groestl](http://www.groestl.info/) which was among the five finalists of the competition organize by NIST to define SHA3.

Unfortunatly the challenge was broken, the padding function simply added \x00 in the end of the input


    def pad_msg(msg):
	    while not (len(msg) % 16 == 0): msg+="\x00"
	    return msg


Therefore ("aa", "aa00") is a collision but I did not note the flag...

Hopefully the correct chalenge will be available next year :)
