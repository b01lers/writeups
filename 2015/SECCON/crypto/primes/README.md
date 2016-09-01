# SECCON : Primes

#### Author: GSAir

**Description**:
> $ cp pq.cgi /var/www/pq.cgi.txt
> http://pailler.quals.seccon.jp/pq.cgi.txt
> http://pailler.quals.seccon.jp/cgi-bin/pq.cgi

After reading the source code we saw the different mathematic operation made for this cipher but we have no idea that it is in fact a real cipher (Paillier cipher).

    a = int(v["p"])
	b = int(v["q"])
	n = (a * b)
	l = (a - 1) * (b - 1)
	r = l
	d = 1
	while 1:
		d = ((n // r + 1) * d) % n
		r = (d * l) % n
		if r == 1:
			break
	while 1:
		x = pow(random.randint(1000000000, 9999999999), n, (n * n))
		o = (pow(n + 1, 1, n * n) * x) % (n * n)
		y = (((pow(o, l, n * n) - 1) // n) * d) % n
		if y == 1:
			break
	c = (pow(n + 1, int(v["num"]), n * n) * x) % (n * n)
	h = (c * o) % (n * n)
	q = "%019d + %019d = %019d" % (c, o, h)
	print q

We rather focus on the return value and find a vector attack:

    c * (o^(-1) mod (n * n)) = (n + 1)^(flag - 1) mod (n * n)

  Like seems to be pretty small, solving the discrete log shouldn't be and issue. But first we need to find n. We get multiple tuple from the web page and try to find the appropriate n:

    import gmpy
    from math import sqrt

    ll = [5482460662146238449, 5573714494494633851, 3040427570606643821, 1537061713970281939, 4709214333931034802, 1333243899908145474, 5385712764812592093, 5347111526885147926, 2226758680194388067, 787833992670284409, 5703615284814877468, 1135625743047701058, 3642606709020177221, 1443162315940259178, 3489385376926980902, 5509049828176720926, 1999889265221318422, 2135304646995180591]

    n = max(map(lambda x: int(sqrt(x)), ll))

    while True:
        for x in xrange(0, len(l), 3):
            if (l[x] * l[x + 1]) % (n * n) !=  l[x + 2]:
                break;
        else:
            print ">>", n
            break

        n += 1

We found `n = 2510510339 = 42727 * 58757` but like we don't know the cipher, the factorization doesn't seems helpful...

    n = 2510510339

    a = 42727
    b = 58757

    l = (a - 1) * (b - 1)
    r = l
    d = 1
    while 1:
        d = ((n // r + 1) * d) % n
        r = (d * l) % n
        if r == 1:
            break

    c = ll[0]
    o = ll[1]

    print pow(o, l, n * n), l, pow(o, l, n * n) % n
    print (((pow(o, l, n * n) - 1) // n) * d) % n
    invo = gmpy.invert(o, n * n)

    print n + 1, (c * invo) % (n * n), n * n

    >> 2510510340, 3792102295877927130, 6302662162225894921

So let's see if sage can give us the flag

    sage: G = Integers(6302662162225894921)
    sage: V = G(3792102295877927130)
    sage: E = G(2510510340)
    sage: V.log(E) + 1
    1510490612

Which gives us: 1510490612 and placing this number on the server gives the flag: SECCON{SECCoooo_oooOooo_ooooooooN}
