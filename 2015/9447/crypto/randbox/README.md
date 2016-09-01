# 9447 : randBox

#### Author: GSAir

**Description**:
> Find your random black box here:
>
> randBox-iw8w3ae3.9447.plumbing port 9447
>
> Note that the order of challenges has changed as of about 2015-11-28 23:00 UTC
>
> This solution was used before the order changed.


Connecting to this server we realize that there is 10 level before getting the flag. Here a fast description of the different levels with the code used in the end.

Each level started with a ciphertext, we needed to find the plaintext. The server was an oracle, if the plaintext sent wasn't the correct one we were getting back its encrypted ciphertext. We could submit 21 plaintext total, which means that we had only 11 errors possible for the complet game.

For all level, the alphabet used are the hexadecimal digits and the ciphers used are alphabetical.

#### Level 1

This was a Caesar cipher. IDEA: send '0' to get the value of the shift

#### Level 2

This cipher was rotating the plaintext. IDEA: send '1000.....0' (length of the ciphertext) and figure out where the 1 was afterward.

#### Level 3, 4, 5

This was a permutation cipher. IDEA: send the alphabet to get the permutation.

#### Level 6

This cipher was a kind of Vigenere. IDEA: send '0...0' (length of the ciphertext) and get the shift for each poition

Now are the difficult ones

#### Level 7

I still don't know what was this cipher but it was encrypting the letter at position i based on letter at position i - 1. Sometime it was the difference, sometime the sum, sometime I don't know. So I did a rainbow table for every possibilities. Also XY and YX would give the same result.

The difficult part was to guess the first character which was kind of random too. Well we have 1/16 chances right? So we run it until we are lucky.

#### Level 8

This one is a kind of chain cipher like CBC. We only need to know the IV. IDEA: send 0 to get the IV.

#### Level 9

Same magic than level 7

#### Level 10

This cipher was a permutation cipher and then applied the following transformation:
abcdef -> badcfe.
IDEA: send the alphabet to get the permutation.

So the only difficult part was level 7 and level 9. We had 1/64 chance to pass both, but the computer is pretty fast.

We finally get the flag: 9447{crYpt0_m4y_n0T_Be_S0_haRD}


Here the code:

    import socket
    import time


    def easy_round(sock):
        ciph =  sock.recv(1024)
        alphabet = ciph.split('\n')[0].split("'")[-2]

        # Round 1 - ceasar cipher
        ciph =  sock.recv(1024)
        ciphertext = ciph.split('\n')[0].split("'")[-2]
        sock.sendall("0\n")
        perm = sock.recv(1024)
        key = alphabet.index(perm[0])
        sock.recv(1024)
        sol = ""
        for x in ciphertext:
            sol += alphabet[(alphabet.index(x) - key) % len(alphabet)]
        sock.sendall(sol + "\n")
        sock.recv(1024)

        # Round 2 - shift
        ciph =  sock.recv(1024)
        ciphertext = ciph.split('\n')[1].split("'")[-2]
        sock.sendall("1" + "0" * (len(ciphertext) - 1) + "\n")
        perm = sock.recv(1024)
        key = perm.index("1")
        sock.recv(1024)
        sol = ""
        for i in xrange(len(ciphertext)):
            sol += ciphertext[(i + key) % len(ciphertext)]
        sock.sendall(sol + "\n")
        sock.recv(1024)

        # Round 3 - permutation
        ciph =  sock.recv(1024)
        ciphertext = ciph.split('\n')[1].split("'")[-2]
        sock.sendall(alphabet + "\n")
        perm = sock.recv(1024)
        sock.recv(1024)
        sol = ""
        for x in ciphertext:
            sol += alphabet[perm.index(x)]
        sock.sendall(sol + "\n")
        sock.recv(1024)

        # Round 4 - permutation
        ciph =  sock.recv(1024)
        ciphertext = ciph.split('\n')[1].split("'")[-2]
        sock.sendall(alphabet + "\n")
        perm = sock.recv(1024)
        sock.recv(1024)
        sol = ""
        for x in ciphertext:
            sol += alphabet[perm.index(x)]
        sock.sendall(sol + "\n")
        sock.recv(1024)


        # Round 5 - permutation
        ciph =  sock.recv(1024)
        ciphertext = ciph.split('\n')[1].split("'")[-2]
        sock.sendall(alphabet + "\n")
        perm = sock.recv(1024)
        sock.recv(1024)
        sol = ""
        for x in ciphertext:
            sol += alphabet[perm.index(x)]
        sock.sendall(sol + "\n")
        sock.recv(1024)

        # Round 6 - vigenere
        ciph =  sock.recv(1024)
        ciphertext = ciph.split('\n')[1].split("'")[-2]
        sock.sendall("0" * len(ciphertext) + "\n")
        perm = sock.recv(1024)[:-1]
        sock.recv(1024)
        sol = ""
        j = 0
        for x in ciphertext:
            sol += alphabet[alphabet.index(x) - alphabet.index(perm[j])]
            j = (j + 1) % len(perm)
        sock.sendall(sol + "\n")
        sock.recv(1024)

    # Round 7 - unknown randomness
    dic = {'a': {'a': '0', 'c': '6', 'b': '1', 'e': '4', 'd': '7', 'f': '5'}, 'c': {'c': '0', 'e': '2', 'd': '1', 'f': '3'}, 'b': {'c': '7', 'b': '0', 'e': '5', 'd': '6', 'f': '4'}, 'e': {'e': '0', 'f': '1'}, 'd': {'e': '3', 'd': '0', 'f': '2'}, '1': {'a': 'b', 'c': 'd', 'b': 'a', 'e': 'f', 'd': 'c', 'f': 'e', '1': '0', '3': '2', '2': '3', '5': '4', '4': '5', '7': '6', '6': '7', '9': '8', '8': '9'}, '0': {'a': 'a', 'c': 'c', 'b': 'b', 'e': 'e', 'd': 'd', 'f': 'f', '1': '1', '0': '0', '3': '3', '2': '2', '5': '5', '4': '4', '7': '7', '6': '6', '9': '9', '8': '8'}, '3': {'a': '9', 'c': 'f', 'b': '8', 'e': 'd', 'd': 'e', 'f': 'c', '3': '0', '5': '6', '4': '7', '7': '4', '6': '5', '9': 'a', '8': 'b'}, '2': {'a': '8', 'c': 'e', 'b': '9', 'e': 'c', 'd': 'f', 'f': 'd', '3': '1', '2': '0', '5': '7', '4': '6', '7': '5', '6': '4', '9': 'b', '8': 'a'}, '5': {'a': 'f', 'c': '9', 'b': 'e', 'e': 'b', 'd': '8', 'f': 'a', '5': '0', '7': '2', '6': '3', '9': 'c', '8': 'd'}, '4': {'a': 'e', 'c': '8', 'b': 'f', 'e': 'a', 'd': '9', 'f': 'b', '5': '1', '4': '0', '7': '3', '6': '2', '9': 'd', '8': 'c'}, '7': {'a': 'd', 'c': 'b', 'b': 'c', 'e': '9', 'd': 'a', 'f': '8', '7': '0', '9': 'e', '8': 'f'}, '6': {'a': 'c', 'c': 'a', 'b': 'd', 'e': '8', 'd': 'b', 'f': '9', '7': '1', '6': '0', '9': 'f', '8': 'e'}, '9': {'a': '3', 'c': '5', 'b': '2', 'e': '7', 'd': '4', 'f': '6', '9': '0'}, '8': {'a': '2', 'c': '4', 'b': '3', 'e': '6', 'd': '5', 'f': '7', '9': '1', '8': '0'}}
    dic2 = {}
    for k1, v1 in dic.iteritems():
        if not k1 in dic2:
            dic2[k1] = {}
        for k2, v2 in v1.iteritems():
            if not k2 in dic2:
                dic2[k2] = {}
            dic2[k2][k1] = v2
            dic2[k1][k2] = v2

    dic = dic2
    alphabet = "0123456789abcdef"

    while True:
        sock = socket.socket()
        sock.connect(("randBox-iw8w3ae3.9447.plumbing",9447))
        start = time.time()

        easy_round(sock)
        ciph =  sock.recv(1024)
        ciphertext = ciph.split('\n')[2].split("'")[-2]
        sock.sendall("0\n")
        perm = sock.recv(1024)[:-1]
        sol = perm[0]
        sock.recv(128)

        j = 1
        sol = alphabet[(alphabet.index(ciphertext[0]) - alphabet.index(sol[-1])) % len(alphabet)]
        for x in ciphertext[1:]:
            for k, v in dic[sol[-1]].iteritems():
                if v == x:
                    sol += k
                    break
            else:
                print "shit"
        sock.sendall(sol + "\n")
        sock.recv(1024)

        ciph = sock.recv(128)
        if not "You" in ciph:
            sock.close()
            continue
        print "7 done"

        # Round 8 - CBC like cipher
        ciphertext = ciph.split('\n')[1].split("'")[-2]
        sock.sendall("0\n")
        perm = sock.recv(1024)[:-1]
        sock.recv(128)
        key = alphabet.index(perm[0])

        sol = ""
        for x in ciphertext:
            sol += alphabet[(alphabet.index(x) - key) % len(alphabet)]
            key = alphabet.index(x)
        sock.sendall(sol + "\n")
        sock.recv(1024)

        # Round 9 - Same magic than level 7
        ciph = sock.recv(1024)
        ciphertext = ciph.split('\n')[1].split("'")[-2]

        sock.sendall("0\n")
        perm = sock.recv(1024)[:-1]
        sol = perm[0]
        sock.recv(128)

        j = 1
        sol = alphabet[(alphabet.index(ciphertext[0]) - alphabet.index(sol[-1])) % len(alphabet)]
        for x in ciphertext[1:]:
            for k, v in dic[sol[-1]].iteritems():
                if v == x:
                    sol += k
                    break
            else:
                print "shit"

        sock.sendall(sol + "\n")
        sock.recv(1024)

        ciph = sock.recv(128)
        if not "You" in ciph:
            sock.close()
            continue

        # level 10 - some weird permutation
        print ciph
        ciphertext = ciph.split('\n')[1].split("'")[-2]
        print "ciphertext", ciphertext

        sock.sendall(alphabet + "\n")
        perm = sock.recv(1024)[:-1]
        print sock.recv(128)
        print "perm", perm

        p = [2 * (i/2) + (i + 1) % 2 for i in range(len(alphabet))]
        sol = ""
        for x in ciphertext:
            sol += alphabet[p[perm.index(x)]]
        ssol = ""
        for i in xrange(0, len(sol), 2):
            ssol += sol[i+1] + sol[i]

        print ssol
        sock.sendall(ssol + "\n")
        print sock.recv(128)
        print sock.recv(128)
        print sock.recv(128)
