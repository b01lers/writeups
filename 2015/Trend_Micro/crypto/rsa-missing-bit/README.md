# Trend Micro : RSA Missing Bit

#### Author: GSAir

**Description**:
> In this challenge we are given a PublicKey.pem file as well as a base64 encoding of a ciphertext (Hopefully the flag).

Let's take a look at the PublicKey:

    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    import gmpy

    with open("PublicKey.pem", "rb") as key_file:
   	 pub_key = serialization.load_pem_public_key(
   		 key_file.read(),
   		 backend=default_backend()
   	 )

    print pub_key.public_numbers().n

And we get the value 82401872610398250859431855480217685317486932934710222647212042489320711027708.

This doesn't seems to be a very secure RSA key, the modulus is even so one of the prime factor would be 2... hum. But 4 is also factor. So the clue makes sense now, the missing bit has to be the LSB.

However do we flip the last bit or we add and additional bit? Adding an extra bit give a number which is easily factorize by sage in 4 different prime.

So we just continue why the number 82401872610398250859431855480217685317486932934710222647212042489320711027709.

The modulus is only a 256bits integer, the factorization is quite fast (using sage 6min). We now continue the script:

    # Fixed n
    n = 82401872610398250859431855480217685317486932934710222647212042489320711027709
    e = pub_key.public_numbers().e

    # factor
    p = 279125332373073513017147096164124452877
    q = 295214597363242917440342570226980714417

    assert(p * q == n)

    d = gmpy.invert(e, (p - 1) * (q - 1))

    with open("flag.bin", "rb") as f:
   	 flag = f.read()

    flag = flag.encode('hex')

    c = int(flag, 16)
    hc = hex(pow(c, d, n))

    print hc
    print ("0" + hc[2:]).decode('hex')

Decoding the value became the hardest part but we did it:

?T?v??y!TMCTF{$@!zbo4+qt9=5}


###Flag: TMCTF{$@!zbo4+qt9=5}
