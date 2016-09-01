# 0ctf : Equations

#### Author: GSAir

**Description**:
> Here is a RSA private key with its upper part masked. Can your recover the private key and decrypt the file?

First we need to rewrite the string, using an OCR online and some manually correction:

    import base64
    key = "Os9mhOQRdqW2cwVrnNI72DLcAXpXUJ1HGwJBANWiJcDUGxZpnERxVw7s0913WXNt" +
            "V4GqdxCzG0pG5EHThtoTRbyX0aqRP4U/hQ9tRoSoDmBn+3HPITsnbCy67VkCQBM4" +
            "xZPTtUKM6Xi+16VTUnFVs9E4rqwIQCDAxn9UuVMBXlX2Cl0xOGUF4C5hItrX2woF" +
            "7LVS5EizR63CyRcPovMCQQDVyNbcWD7N88MhZjujKuSrHJot7WcCaRmTGEIJ6TkU" +
            "8NWt9BVjR4jVkZ2EqNd0KZWdQPukeynPcLlDEkIXyaQx"

The key is a base64 of an ASN1 encoding. We know that the private RSA keys are as follow:

      Version ::= INTEGER { two-prime(0), multi(1) }
      (CONSTRAINED BY
      {-- version must be multi if otherPrimeInfos present --})

      RSAPrivateKey ::= SEQUENCE {
          version           Version,
          modulus           INTEGER,  -- n
          publicExponent    INTEGER,  -- e
          privateExponent   INTEGER,  -- d
          prime1            INTEGER,  -- p
          prime2            INTEGER,  -- q
          exponent1         INTEGER,  -- d mod (p-1)
          exponent2         INTEGER,  -- d mod (q-1)
          coefficient       INTEGER,  -- (inverse of q) mod p
          otherPrimeInfos   OtherPrimeInfos OPTIONAL
      }

In ASN1, integers start with the byte 0x02, as the key is cut in the middle let's remove the beginning to be able to read it.

    key = base64.b64decode(key)
    with open('key.pem', 'wb') as f:
        f.write(base64.b64encode(key[:key.index('\x02')].encode('hex')))

Using opeenssl we can read the key:

    > cat key.pem | tr -d '\n' | base64 -d | openssl asn1parse -inform DER
    0:d=0  hl=2 l=  65 prim: INTEGER           :D5A225C0D41B16699C4471570EECD3DD7759736D5781AA7710B31B4A46E441D386DA1345BC97D1AA913F853F850F6D4684A80E6067FB71CF213B276C2CBAED59
    67:d=0  hl=2 l=  64 prim: INTEGER           :1338C593D3B5428CE978BED7A553527155B3D138AEAC084020C0C67F54B953015E55F60A5D31386505E02E6122DAD7DB0A05ECB552E448B347ADC2C9170FA2F3
    133:d=0  hl=2 l=  65 prim: INTEGER           :D5C8D6DC583ECDF3C321663BA32AE4AB1C9A2DED6702691993184209E93914F0D5ADF415634788D5919D84A8D77429959D40FBA47B29CF70B943124217C9A431

So we have the last 3 integers, namely
    dp = e^(-1) mod (p - 1)
    dq = e^(-1) mod (q - 1)
    qinv = q^(-1) mod p

These relations can be rewritten:

    e * dp - 1 = k * (p - 1)
    e * dq - 1 = k' * (q - 1)

Therefore p - 1 divides e * dp - 1 (Same story with q). We don't know e but we can guess it is 3 or 0x10001. 3 didn't give use big enough prime number so I stick with 0x10001.

I used the following sage script to solve the challenge, there are comments :) Enjoy!

    import itertools
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_v1_5

    dp = long("D5A225C0D41B16699C4471570EECD3DD7759736D5781AA7710B31B4A46E441D386DA1345BC97D1AA913F853F850F6D4684A80E6067FB71CF213B276C2CBAED59", 16)
    dq = long("1338C593D3B5428CE978BED7A553527155B3D138AEAC084020C0C67F54B953015E55F60A5D31386505E02E6122DAD7DB0A05ECB552E448B347ADC2C9170FA2F3", 16)
    qinv = long("D5C8D6DC583ECDF3C321663BA32AE4AB1C9A2DED6702691993184209E93914F0D5ADF415634788D5919D84A8D77429959D40FBA47B29CF70B943124217C9A431",16)
    e = 0x10001

    print '############ first factor ############'
    # k * (q - 1) == e * dq - 1
    val1 = e * dq - 1

    # let's find possible values for k
    factval1 = factor(val1)

    # write factor with multiplicity
    allfactval1 = []
    for a, b in factval1:
    	allfactval1 += [a] * b

    # we know q - 1 is even, let's remove a 2 from the factors
    allfactval1.pop(0)

    # let's try all possible values for k
    q = 1
    for r in xrange(1, len(allfactval1)):
    	for fact in itertools.combinations(allfactval1, r):
    		k = reduce(lambda x, y: x * y, fact, 1)
    		tq = val1/k + 1
    		if tq > q and tq in Primes():
    			q = tq

    # make some verifications
    assert (dq * e) % (q - 1) == 1
    print "q = {}".format(q)
    print "bit strength: {}".format(len(bin(q)) - 2)
    print

    print '############ second factor ############'
    val2 = e * dp - 1

    # We tried to factorize val2 however it took way to long... We may not need the full factorization:
    allfactval2 = []
    P = Primes()
    val2c = val2
    p = 2
    while val2c > 2**500:
    	while val2c % p == 0:
    		allfactval2.append(p)
    		val2c /= p
    	p = P.next(p)

    # add the remainder to the list of factors
    allfactval2.append(val2)

    # we only have a partial factorization, however the bigger number is less than 500 bits, it must be a factor of p - 1
    allfactval2.pop(0)

    p = 1
    for r in xrange(1, len(allfactval2)):
    	for fact in itertools.combinations(allfactval2, r):
    		k = reduce(lambda x, y: x * y, fact, 1)
    		p = val2/k + 1
    		if tp > p and p in Primes():
    			p = tp

    # some checks
    assert (e * dp) % (p - 1) == 1
    assert (q * qinv) % p == 1
    print "p = {}".format(p)
    print "bit strength: {}".format(len(bin(p)) - 2)
    print

    # generate RSA key and get the flag
    with open('flag.enc') as f:
    	flag = f.read()

    d = inverse_mod(e, (p - 1) * (q - 1))

    key = RSA.construct((long(p * q), long(e), long(d)))
    cipher = PKCS1_v1_5.new(key)

    print '############ Flag ############'
    print cipher.decrypt(flag, "")

The result:

    0ctf{Keep_ca1m_and_s01ve_the_RSA_Eeeequati0n!!!}
