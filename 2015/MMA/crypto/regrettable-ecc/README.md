# MMA : Regrettable ECC

#### Author: GSAir

**Description**:
> The challenge is to decrypt a flag encrypted using AES-CBC, and the key is generated from an Elliptic Curve.

Let's take a look at the encryption function:

    # public key: H = kG
    def encrypt(H, m):
        r = getRandomRange(1, p)
        M = r * G
        S = e * M
        T = e * r * H - M
        #print "encrypt: M = %s" % M
        cipher = AES.new(long_to_bytes(M.x, 32), mode = AES.MODE_CBC, IV = DEM_IV)
        dem_c = bytes_to_long(cipher.encrypt(pad(m)))
        return (S, T, dem_c)


And we know the following parameters:

    p = 115792089210356248762697446949407573530086143415290314195533631308867097853951
    A = -3
    B = 41058363725152142129326129780047268409114441015993725554835256314039467401291
    G = ECP(48439561293906451759052585252797914202762949526041747995844080717082404635286, 36134250956749795798585127919587881956611106672985015071877198253568414405109)
    e = 65537
    DEM_IV = "\xAA"*16

    #H = key.k * G
    H = ECP(109751108484562349164127530101305240692682402677631328958397290100273187096405, 90096893579313178361630896633528547111519814104799360692628427547223501810820)


They are using a *home-made* elliptic curve class which give every operation required on it. The Elliptic curve used is in it Weierstrass form: ```y^2 = x^3 + Ax + B```

We can see that the AES key is extracted from the x coordinate of the point M. And M is computed by ```M = r x G``` with ```r``` randomly chosen. SO one way to get M from this is to use their decryption routine:

    # secret key: k
    def decrypt(k, c):
        (S, T, dem_c) = c
        M = k * S - T
        #print "decrypt: M = %s" % M
        cipher = AES.new(long_to_bytes(M.x, 32), mode = AES.MODE_CBC, IV = DEM_IV)
        return unpad(cipher.decrypt(long_to_bytes(dem_c, AES.block_size)))


... but it required the private key k!!!
Then I realize ```S = e * M``` is the vulnerability. In a group of order ```ord```, ```ord * X = 0``` (using the additive notation and ```0``` for the group identity). Therefore if we find ```d``` such that ```e * d = 1 (mod ord)```, we have ```d * S = d * (e * S) = (d * e) * M = (1 + n * ord) * M = M + n * 0 = M```

We just have to find the order, which is a difficult problem in general. Using sage:

    sage: p = 115792089210356248762697446949407573530086143415290314195533631308867097853951
    sage: A = -3
    sage: B = 41058363725152142129326129780047268409114441015993725554835256314039467401291
    sage: E = EllipticCurve(GF(p), [A,B])
    sage:
    sage: print E.cardinality()
    115792089210356248762697446949407573529996955224135760342422259061068512044369

and finishing with a python script:

    with open('ciphertext', 'r') as fr:
        (S, T, dem_c) = eval(fr.read())

    M = int(gmpy.invert(e, 115792089210356248762697446949407573529996955224135760342422259061068512044369)) * S
    cipher = AES.new(long_to_bytes(M.x, 32), mode = AES.MODE_CBC, IV = DEM_IV)


    print unpad(cipher.decrypt(long_to_bytes(dem_c, AES.block_size)))


###Flag: MMA{4a2f832ab7fae69820a697156e0d3dd7423f81ed}
