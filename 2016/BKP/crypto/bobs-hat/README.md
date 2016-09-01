# BKP : Bob's Hat

#### Author: GSAir

**Description**:
> bob's hat : crypto : Alice and Bob are close together, likely because they have a lot of things in common.
This is why Alice asked him a small **q**uestion, about something cooler than a wiener.

It seems that the password of the zip is encrypted with the given public key. And based on the name of the challenge we guess that we will have to do 4 steps before getting the flag.

Also the description gives multiple informations that we need to keep in mind

   1. "lot of things in common"
   2. "small **q**"
   3. "wiener"

### Step 1

    from Crypto.PublicKey import RSA
    import gmpy
    with open("almost_almost_almost_almost_there.pub", "r") as f:
        key = RSA.importKey(f.read())

    print len(bin(key.n)) - 2
    print key.e

gives us:

    1024
    65537

Trying to factorize n with Sage/msieve didn't work in 30sec so we gave up (not hint #2).
The #3 hints is not useful either... OK let's try well known issue with RSA: close prime factors are vulnerable to Fermat factorization.

    def fermat_factor(n):
        a = gmpy.sqrt(n) + 1
        b = a*a - n
        bsq = gmpy.sqrt(b)

        while bsq * bsq != b:
            a += 1
            b = a * a - n
            bsq = gmpy.sqrt(b)

        return  a + bsq

    p = fermat_factor(key.n)
    q = key.n // p

    d = long(gmpy.invert(key.e, (p - 1) * (q - 1)))

    privKey = RSA.construct((key.n, key.e, d))

    with open("almost_almost_almost_almost_there.encrypted", "r") as f:
        print privKey.decrypt(f.read())

And we have the first password: XtCgoEKksjKFWlqOSxqsEhK/+tsr1k5c

### Step 2

    with open("almost_almost_almost_there.pub", "r") as f:
        key2 = RSA.importKey(f.read())

    print len(bin(key2.n)) - 2
    print key2.e

gives us again:

    1024
    65537

This time the hint #1 is useful: the two modulus are sharing a prime factor:

    p = gmpy.gcd(key1.n, key.n)
    q = key1.n // p

    d = long(gmpy.invert(key1.e, (p - 1) * (q - 1)))

    privKey = RSA.construct((key1.n, key1.e, d))
    with open("almost_almost_almost_there.encrypted", "r") as f:
        print privKey.decrypt(f.read())

And we have the second password: rlSpJ6HbP+cZXaOuSPOe4pgfevGnXtLt

### Step 3

    with open("almost_almost_there.pub", "r") as f:
        key3 = RSA.importKey(f.read())

    print len(bin(key3.n)) - 2
    print key3.e

this time gives us::

    1040
    65537

The modulus is a little bit bigger and we can't use hint #3, therefore it should be hint #2. And yes, the modulo has a very small prime factor.

    p = 54311
    q = key3.n // p
    d = long(gmpy.invert(key3.e, (p - 1) * (q - 1)))

    privKey = RSA.construct((key3.n, key3.e, d))

    with open("almost_almost_there.encrypted", "r") as f:
        print privKey.decrypt(f.read())

And we have the third password: hQdK+dKleMJqth/dofWyFaiWp3PW7jil

### Step 4

This time even before checking the value of e, we expect to have a big value. Wiener proposed an attack on RSA when using big encryption exposent.

    with open("almost_there.pub", "r") as f:
        key = RSA.importKey(f.read())

    print len(bin(key.n)) - 2
    print key.e

and indeed:

    1024
    49446678600051379228760906286031155509742239832659705731559249988210578539211813543612425990507831160407165259046991194935262200565953842567148786053040450198919753834397378188932524599840027093290217612285214105791999673535556558448523448336314401414644879827127064929878383237432895170442176211946286617205

We can therefore launch a wiener attack using the following code [rsa-wiener-attack](https://github.com/pablocelayes/rsa-wiener-attack.git):

    import ContinuedFractions, Arithmetic, RSAvulnerableKeyGenerator
    def hack_RSA(e,n):
        '''
        Finds d knowing (e,n)
        applying the Wiener continued fraction attack
        '''
        frac = ContinuedFractions.rational_to_contfrac(e, n)
        convergents = ContinuedFractions.convergents_from_contfrac(frac)

        for (k,d) in convergents:

            #check if d is actually the key
            if k!=0 and (e*d-1)%k == 0:
                phi = (e*d-1)//k
                s = n - phi + 1
                # check if the equation x^2 - s*x + n = 0
                # has integer roots
                discr = s*s - 4*n
                if(discr>=0):
                    t = Arithmetic.is_perfect_square(discr)
                    if t!=-1 and (s+t)%2==0:
                        print("Hacked!")
                        return d
        return None

        d = hack_RSA(key.e, key.n)
        privKey = RSA.construct((key.n, key.e, d))

        with open("almost_there.encrypted", "r") as f:
            print privKey.decrypt(f.read())

Then we get the last password: /3aAP5dF2zmrPh9K6A4AqMLsIiYDk2C2 and a file FLAG appears

    cat FLAG
    BKPCTF{Its_not_you,_its_rsa_(that_is_broken)}
