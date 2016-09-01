# MMA : Signer and Verifier

#### Author : GSAir

**Description**:
> They give us two servers, one Verifier and one Signer. The Signer is a Oracle and send us the signature of any message we send. The verifier sends us one message and we have to sign it.

With the description I gave, everything seems straight forward, just open two socket and ask the Signer to sign the Verifier message:

    #/usr/bin/env python
    import socket

    sockVerifier = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockVerifier.connect(("cry1.chal.mmactf.link", 44816))

    toSign = sockVerifier.recv(2048)
    print toSign

    # to split the message
    partner = "Sign it!"

    toSign = toSign[toSign.index(partner) + len(partner) + 1:]

    val = int(toSign)

    sockSigner = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockSigner.connect(("cry1.chal.mmactf.link", 44815))

    sockSigner.sendall(str(val) + "\n")
    sign = eval(sockSigner.recv(512))

    print "\nSignature"
    print sign

    sockVerifier.sendall(str(sign) + "\n")

    flag = sockVerifier.recv(512)

    print "Flag"
    print flag


But unfortunately, the Signer refuse to send us back the signature:

    Traceback (most recent call last):
      File "tmp.py", line 21, in <module>
        sign = eval(sockSigner.recv(512))
      File "<string>", line 1
        By the way, I'm looking forward to the PIDs subsystem of cgroups.
             ^
    SyntaxError: invalid syntax

The two processes must some how communicate and the Signer failed when the request message was from the Verifier.
Therefore I try to understand better how the signature mechanism was working. It seems they were using RSA (based on the public key name). One of *basic* RSA signature issue is the fact that you can forge a signature based on two valid one. If *m1* signature is **s1** and *m2* signature is **s2**, then *m1 x m2* signature is **s1 x s2 % n**.

I tried that quickly by asking the Signer to sign 2 and 4, and I verify that the previous relation was holding, IT WASSSS!!!

So the idea is to make the Signer sign our message in two parts. My script work only if the message to sign is even, I didn't want to look for a small divisor so I relaunched the script (3 times) until I get the flag:

    #/usr/bin/env python
    import socket
    import gmpy

    sockVerifier = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockVerifier.connect(("cry1.chal.mmactf.link", 44816))

    toSign = sockVerifier.recv(2048)
    print toSign

    partner = "Sign it!"

    n = 167891001700388890587843249700549749388526432049480469518286617353920544258774519927209158925778143308323065254691520342763823691453238628056767074647261280532853686188135635704146982794597383205258532849509382400026732518927013916395873932058316105952437693180982367272310066869071042063581536335953290566509
    e = 65537

    toSign = toSign[toSign.index(partner) + len(partner) + 1:]

    val = int(toSign)

    if (val % 2 == 0):
        sockSigner = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockSigner.connect(("cry1.chal.mmactf.link", 44815))

        sockSigner.sendall("2\n")
        sign1 = sockSigner.recv(512)

        sockSigner = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockSigner.connect(("cry1.chal.mmactf.link", 44815))

        sockSigner.sendall(str(val / 2) + "\n")
        sign2 = sockSigner.recv(512)
    else:
        print 'Try again'

    sign = (int(sign1) * int(sign2)) % n

    print "\nSignature"
    print sign

    assert pow(sign, e, n) == val

    sockVerifier.sendall(str(sign) + "\n")

    flag = sockVerifier.recv(512)

    print "Flag"
    print flag

Voila!!

###Flag: MMA{homomorphic_challengers}
