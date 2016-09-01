# BKP : HMAC_CRC

#### Author: GSAir

**Description**:
> hmac_crc - crypto: We're trying a new mac here at BKP---HMAC-CRC. The hmac (with our key) of "zupe zecret" is '0xa57d43a032feb286'.  What's the hmac of "BKPCTF"?
>
> NOTE: this write-up is based on the previous write-up of hellman from the team More Smoked Leet Chicken and can be found
> [here](http://mslc.ctf.su/wp/mma-ctf-2015-motto-mijikai-address-cryptoweb-100300/)

# Material
-----------
We have one python source file.

    #!/usr/bin/env python
    def to_bits(length, N):
      return [int(i) for i in bin(N)[2:].zfill(length)]

    def from_bits(N):
      return int("".join(str(i) for i in N), 2)

    CRC_POLY = to_bits(65, (2**64) + 0xeff67c77d13835f7)
    CONST = to_bits(64, 0xabaddeadbeef1dea)

    def crc(mes):
      mesg = mes[::] + CONST
      shift = 0
      while shift < len(mesg) - 64:
        if mesg[shift]:
          for i in range(65):
            mesg[shift + i] ^= CRC_POLY[i]
        shift += 1
      return mesg[-64:]

    INNER = to_bits(8, 0x36) * 8
    OUTER = to_bits(8, 0x5c) * 8

    def xor(x, y):
      return [g ^ h for (g, h) in zip(x, y)]

    def hmac(h, key, mesg):
      return h(xor(key, OUTER) + h(xor(key, INNER) + mesg))

    PLAIN_1 = "zupe zecret"
    PLAIN_2 = "BKPCTF"

    def str_to_bits(s):
      return [b for i in s for b in to_bits(8, ord(i))]

    def bits_to_hex(b):
      return hex(from_bits(b)).rstrip("L")

    if __name__ == "__main__":
      with open("key.txt") as f:
        KEY = to_bits(64, int(f.read().strip("\n"), 16))
      print PLAIN_1, "=>", bits_to_hex(hmac(crc, KEY, str_to_bits(PLAIN_1)))
      print "BKPCTF{" + bits_to_hex(hmac(crc, KEY, str_to_bits(PLAIN_2))) + "}"

# Solution
------------

CRC are based on polynomial arithmetic, it is a polynomial modulo reduction in GF(2) with additional masking before and after. In our case the CRC is 64bit and has only an addition afterward.

The CRC used could be written CRC(M) = (M(X) \* X**64 + C(X)) mod P(X) where C(X) is the polynomial 0xabaddeadbeef1dea and P(X) is the polynomial 0x1eff67c77d13835f7

We are going to construct the sage program used:

    from sage.all import *

    def ntopoly(npoly):
        return sum(c*X**e for e, c in enumerate(Integer(npoly).bits()))

    def polyton(poly):
        return sum(int(poly[i])*(1 << i) for i in xrange(poly.degree() + 1))

    X = GF(2).polynomial_ring().gen()
    N = 64

    P = ntopoly((2**64) + 0xeff67c77d13835f7)
    I = ntopoly(int(("36"*8), 16))
    O = ntopoly(int(("5C"*8), 16))
    C = ntopoly(0xabaddeadbeef1dea)


With that we can defined the CRC and the HMAC-CRC functions:

    def crc(v):
        pv = ntopoly(int(v.encode('hex'), 16))
        return hex(polyton((pv * X**64) % P))

    def hmaccrc(k, v):
        pv = ntopoly(int(v.encode('hex'), 16))
        pk = ntopoly(int(k, 16))
        inner = ((pk + I) * X**(64+len(v)*8) + pv * X**64 + C) % P
        return hex(polyton(((pk + O) * X**(64 + 64) + inner * X**64 + C) % P))

Writing the HMAC in polynomial form yields:

    HMAC(K, M) = K(X) * X**128 * (X ** len(M) + 1) + O(X) * X**128 + I(X) * X**(128 + len(M)) + M(X) * X**128 + C(X) * (X**64 + 1) mod P(X)

Therefore we could reverse the equation and get K:

    K(X) = (HMAC(K, M) - O(X) * X**128 + I(X) * X**(128 + len(M)) + M(X) * X**128 + C(X) * (X**64 + 1)) / (X**128 * (X ** len(M) + 1)) mod P(X)

Luckily X\*\*128 \* (X \*\* len(M) + 1) is invertible modulo P(X) given the size of the message, therefore we can retrieve the key:


    msg = "zupe zecret"
    l = len(msg) * 8
    M = ntopoly(int(msg.encode("hex"), 16))

    HMAC = ntopoly(0xa57d43a032feb286)

    NUM = (HMAC - (O * X**128 + I * X**64 * X**(64+l) + m * X**64 * X**64 + C * (X**64 + 1))) % P(X)
    DEN = X**128 * (X**l + 1)

    assert (1 == gcd(P, DEN)  
    K = NUM * inverse_mod(DEN, P)

And we compute the solution

    print hmaccrc(hex(polyton(K))[2:], "BKPCTF")
    > BKPCTF{d2db2b8b9002841f}
