# MMA : Alicegame

#### Author: GSAir

**Description**:
> This challenge gave us access to an Encryption Oracle, the Oracle requested a ```m``` and a ```r``` and sent us back a couple ```(s1, s2)```. After some interaction, the Oracle sent the encryption of the flag: ```My Secret Message: (S1, S2)```.
>
> Initially there were no source code, but they released the server code as a hint.

I didn't have the chance to try this challenge before they released the hint, therefore I am not sure that I would have figure out quickly that it was an El Gamal encryption scheme.

    public key: (g, h, p)
    private key: (x, p)
    p is a prime number
    h = g^x mod p

    Encryption:
    r = rand(1, p)
    s1 = g^r mop p
    s2 = (m * h^r) mod p
    Decryption:
    m = s2 * (s1^x)^(-1) mod p


First we have to find the public key at least, like we can choose ```m, r``` with the Oracle, ```1,1``` give us ```s1,s2 = g, h```.
For ```p```, we see in the code that it is a 201bits long prime. Therefore I chose ```m, r = 1 << 201, 0``` then ```p = 1 << 201 - s2```.

And now happy of myself, I jumped on Sage and try to solve the discrete logarithm in order to find x... We are still waiting for the answer...

Then on the IRC channel after the CTF I read about using Pohlig-Hellman algorithm to solve the discrete log. This algo works very well when the prime number is smooth! So it was their mistake, El Gammal requires that ```p - 1``` has a big prime factor, ideally ```p = 2 * q + 1``` where ```q``` is prime. Here they choose ```p``` randomly each time we contact the Oracle.

Therefore the solution I get a little bit late was to connect until we obtain a ```p``` smooth enough, I put the limit at 200 tries or biggest factor around 16 digits. You may want to restart if the biggest factor is too big, the memory used by the algorithm can be quite high.

Here the complete code using Sage:

    import socket
    import sys
    import os
    from Crypto.Random import random
    from Crypto.Util.number import *
    from sage.all import *


    def maxfacor(N):
    	f = factor(N)
    	return f[-1][0]

    ma = 1 << 200

    for i in xrange(200):
    	print i
    	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    	sock.connect(("cry1.chal.mmactf.link", 39985))

    	sock.recv(512)
    	# m
    	sock.recv(512)
    	sock.sendall("1\n");

    	# r
    	sock.recv(512)
    	sock.sendall("1\n");

    	(g, h) = eval(sock.recv(1024))

    	m = long(1 << 201)

    	# m
    	sock.recv(512)
    	sock.sendall(str(m) + "\n");

    	# r
    	sock.recv(512)
    	sock.sendall("0\n");

    	(_, m2) = eval(sock.recv(1024))

    	p = m - m2

    	# m
    	sock.recv(512)
    	sock.sendall("123456789\n");

    	# r
    	sock.recv(512)
    	sock.sendall("2\n");

    	(r, s1) = eval(sock.recv(512))
    	assert pow(g, 2, p) == r
    	assert (s1 * inverse_mod(h ** 2, p)) % p == 123456789

    	mm = maxfacor(p - 1)
    	if (mm < ma):
    		ma = mm

    		gg = g
    		hh = h
    		pp = p

    		sock.recv(512)
    		sock.sendall("g\n");
    		msg = sock.recv(512)
    		(rr, ss) = eval(msg[msg.index(':') + 1:])

    		if (ma < 10 ** 15):
    			break
        sock.close()


    print (gg, hh, pp)
    print factor(pp - 1)
    print (rr, ss)

    G = Mod(gg, pp)
    H = Mod(hh, pp)
    S = Mod(ss, pp)
    R = Mod(rr, pp)

    X = discrete_log(H, G)
    print "X =", X

    print "Flag:"
    print long_to_bytes(long(S / R**X))

I get a very nice number, the discrete log has been computed in few seconds:

    (1080203957590237745049901920385991402970505501880223903139384L, 563458214284375217945104521525965621224108823187624594055245L, 1633125361436592775454853523384722935381387816712069503813959L)
    2 * 3 * 31 * 37 * 131 * 358373 * 2337217 * 2767343 * 6374341 * 30524531 * 665813651 * 6032526820063
    (548963366317246148127966051702960320595286976476120175543273L,81754052271027868453470529110750662527594169494019779266181L)
    X = 596652681294729697295278089954066695569205559569341341391146
    MMA{wrOng_wr0ng_ElGamal}



###Flag: MMMA{wrOng_wr0ng_ElGamal}
