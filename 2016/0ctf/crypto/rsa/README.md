# 0ctf : RSA?

#### Author: GSair

**Description**:
> It seems easy, right?
> Tip: openssl rsautl -encrypt -in FLAG -inkey public.pem -pubin -out flag.enc?

Well we start with the beginning, we print the modulus and check its bit strength:

    n = 23292710978670380403641273270002884747060006568046290011918413375473934024039715180540887338067
    bits length: 314
    e = 3

Well, it seems to be a piece of cake... But the description gave me a bad feeling. We use msieve to factor n:

    n = 26440615366395242196516853423447 * 27038194053540661979045656526063 * 32581479300404876772405716877547

Well, well... But our luck is that e = 3. We can factorize the polynomial X^3 - C mod p, etc... And using the Chinese Remainder Theorem we can find the flag.

Here the sage sript we used:

    from Crypto.PublicKey import RSA
    with open('public.pem') as f:
    	key = RSA.importKey(f.read())

    print "n = {}".format(key.n)
    print "bits length: {}".format(len(bin(key.n)) - 2)
    print "e = {}".format(key.e)

    with open('flag.enc') as f:
    	ciphertext = f.read()

    def toint(s):
    	return int(s.encode('hex'), 16)

    def tostr(s):
    	h = hex(s)[2:]
    	if len(h) % 2 == 0:
    		return h.decode('hex')
    	else:
    		return ('0' + h).decode('hex')

    C = toint(ciphertext)

    p = 26440615366395242196516853423447
    Xp = GF(p).polynomial_ring().gen()
    Cp = Integer(C)

    P = Xp**3 - Cp
    factP = factor(P)

    q = 27038194053540661979045656526063
    Xq = GF(q).polynomial_ring().gen()
    Cq = Integer(C)

    Q = Xq**3 - Cq
    factQ = factor(Q)

    r = 32581479300404876772405716877547
    Xr = GF(r).polynomial_ring().gen()
    Cr = Integer(C)

    R = Xr**3 - Cr
    factR = factor(R)

    def getval(poly, mod):
    	return mod - int(str(poly).split(" + ")[1])

    for vp, _ in factP:
        for vq, _ in factQ:
            if vq.degree() > 1:
                continue
    	    for vr, _ in factR:
    		    flag = tostr(crt([getval(vp, p), getval(vq, q), getval(vr, r)], [p, q, r]))
		        if "0ctf" in flag:
			        print flag[flag.index("0ctf"):]

And we get:

    0ctf{HahA!Thi5_1s_n0T_rSa~}
