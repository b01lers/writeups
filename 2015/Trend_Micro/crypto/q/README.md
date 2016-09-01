# Trend Micro : Q

#### Author: GSAir

**Description**:
> Your small program has been drew by kid, some values are missed, but you feel you can restore it!
> Please try to find the value of AES IV key.
>
> If you can get the key string like "KEY: key string", please submit "TMCTF{key string}" as your answer.

Ok, let's write this code:

    #!/usr/env python

    import base64
    import itertools
    from Crypto.Cipher import AES
    import sys
    import binascii

    # Predefine
    KEY = "5d6I9pfR7C1JQt.."

    # Replace with random number
    IV = "................"

    # Encryption
    def encrypt(message, passphrase, iv):
    	aes = AES.new(passphrase, AES.MODE_CBC, iv)
    	return aes.encrypt(message)

    # check argument
    #if len(sys.argv) < 2:
    #	print "Please input your data!"
    #	sys.exit

    # Output result
    #print "encrypte Data: " + binascii.hexlify(encrypt(sys.argv[1], KEY))

    # plaintext
    plaintext = "The message is protected by AES!"

    ciphertext = "fe...........................ec3307df037c689300bbf2812ff89bc0b49"

There is two details that we have to be careful with: in the key there is a character looking like a I or a 1, in the plaintext there is a \\! (is it '!' or '\n' because it is need to be 32 characters long for matching two AES block size.)

So the good answer is 'I' and '!' but I had to try all solutions...

We need to analyze the problem here.

 - They are using AES-CBC (block size 16 bytes, key size 16 bytes (or 24 or 32))
 - We almost have the key, only two characters are missing (can not be 24 characters based on the picture)
 - We know one plaintext of length two block
 - We know the second block of the corresponding ciphertext
 - .... They use CBC!!!!

So we remind CBC equations:

![equation_CBC](http://i.imgur.com/YB9WiIq.jpg)

We want to compute the IV so we need to recover the key and the first ciphertext block. If we look at the decryption equation for the second block, we know *almost* everything with some missing parts (key and first block ciphertext):

![interesting_equation](http://i.imgur.com/6DcmXWa.jpg)

A good encryption algorithm should output a strong pseudo-random ciphertext, so if we find a key which give us a block starting with "fe" and finishing with "ec3" then it is very likely that we found the good KEY. We can also see that the first ciphertext block ends with "9ec3" if we need to be more precise

Therefore the strategy is to pad the KEY with all possible 2 letters word and find a match for the first ciphertext. Once we have it we can extract the IV with the same equation.


    KEY = "5d6I9pfR7C1JQt"
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+="

    # Decryption
    def decrypt(message, passphrase):
    	aes = AES.new(passphrase, AES.MODE_ECB, "")
    	return aes.decrypt(message)

    lastblock = ciphertext[-32:].decode('hex')
    start = "fe"
    end = "9ec3"

    def xor(iv, block):
    	res = ""
    	for (x, y) in zip(iv, block):
    		res += chr(ord(x) ^ ord(y))

    	return res

    for res in itertools.product(alphabet, repeat=2):
    	passphrase = KEY + ''.join(res)

    	c = decrypt(lastblock, passphrase)

    	c0 = xor(c, plaintext[-16:]).encode('hex')
    	if c0.startswith(start) and c0.endswith(end):
    			print "Yes"
    			print passphrase
    			nKEY = passphrase

    			iv = decrypt(c0.decode('hex'), passphrase)

    			nIV = xor(plaintext[:16], iv)
    			break
    else:
    	print "Nooo"
    	sys.exit()

    # Test
    print ciphertext
    print encrypt(plaintext, nKEY, nIV).encode('hex')

    print "TMCTF{" + nIV.replace('Key:', '') + "}"

Now we just have to run it:

    Yes
    5d6I9pfR7C1JQt7$
    fe...........................ec3307df037c689300bbf2812ff89bc0b49
    fe1199011d45c87d10e9e842c1949ec3307df037c689300bbf2812ff89bc0b49
    TMCTF{rVFvN9KLeYr6}



###Flag: TMCTF{rVFvN9KLeYr6}
