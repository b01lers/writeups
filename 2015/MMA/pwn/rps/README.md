# MMA : RPS

#### Author: yfb76

First we run the binary to get a sense of what it does.  It's a rock paper scissors command line game.  You enter a user name, and then you have to win 50 times in a row.  If you do, they send you the flag.  You have a (1/3)^50 chance of doing this if your opponent is truly random.  Clearly, we need to alter the randomness so that we *know* what the opponent will show.

Dynamic Analysis
-------------------------

We start our dynamic analysis with our good friend _ltrace_ .  What do we see:

![ltrace screen shot for rps](http://i.imgur.com/FMlo7rF.jpg "ltrace screenshot")

So it is reading 4 bytes from /dev/urandom .  What does it do with them? Lets continue our ltrace session:

![ltrace screen shot 2](http://i.imgur.com/bnKKAi0.jpg "ltrace screenshot 2")

It prompts for a user name, which it reads in with gets().  Our mental antennae start to tingle,
because gets() reads until the end of a line - so there is *no* character limit.  This makes it a prime canidate for buffer overflows.  There is some more dialog (note: "janken" is japanese slang for rock paper sissors according to my friend Serge), and then a call to srand().  As you are likely aware: if you use the same value for srand() then you get the same results from a series of calls to rand() for each execution of the program.  Since user input occurs before srand() we hope that there is a buffer overflow we can exploit to dictate the seed given to srand().  

Static Analysis
--------------------

With this theory in mind, lets dip into the assembly code to see whats going on on the stack.  Note:
I dissasbembled with:

>objdump -d rps > rps.S

Fortunately, the binary wasn't stripped which makes this easy.  We find main.  The first item of
interest is the call to fread:

![assembly screenshot 1](http://i.imgur.com/LYxxu6i.jpg "assembly screenshot 1")

As my note in the code says, this results in the random bytes being stored in -0x20(%ebp).  Continuing on, we come to the call to gets() - our potential vulnerability:

![assembly screenshot 2](http://i.imgur.com/IfZW7bL.jpg "assembly screenshot 2")

We see that it store the user name to -0x50(%ebp).  The final question is what gets passed
to srand() as the seed:

![assembly screenshot 3](http://i.imgur.com/TvB09K3.jpg "assembly screenshot 3")

It is -0x20(%ebp).  There is a difference of 0x30 = 48 between where the user name entry starts and the seed passed to srand().  So, with a 52 character user name, the last 4 become the value given to srand(), overriding the values read in from /dev/urandom.  

In Which we Get Lazy and Guess
---------------------------------------------

At this point, we should have continued our static analysis to see how they choose Rock, Paper,
or Scissor based on rand().  However, this is a low point "warmup" challenge, so we guessed that
they took the random % 3, and assigned 0, 1, 2 to rock, paper, scissor in some order.

To test this, we wrote a small C program to dump out the first 40 rand values, mod 3, for our
chose seed: 0x61616161, ie "aaaa".  With this, we played the game locally, and mapped rock, paper, scissor to the values successfully and consistently.

The Exploit
=======

We wrote a python script to connect to their server, and then send all 50 answers at once (otherwise our game would timeout).  Running it yielded the flag.  

    #/usr/bin/env python
    import socket

    def f(i):
            if (i == 0):
                    return "P"
            elif (i == 1):
                    return "S"
            else:
                    return "R"

    sockSigner = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockSigner.connect(("milkyway.chal.mmactf.link", 1641))

    sol = [1,2,0,2,2,1,2,2,1,1,2,0,2,1,1,1,1,2,2,1,2,0,1,2,0,1,1,1,0,2,2,1,0,0,2,2,1,2,2,0,1,2,0,0,0,2,0,0,1,0]

    print sockSigner.recv(2048)
    sockSigner.sendall("a" * 52 + "\n")

    st = ""
    for x in sol:
            st += str(f(x))

    print sockSigner.recv(10048)
    sockSigner.send(st + "\n")

    print sockSigner.recv(10048)

Huzzah, 50 points in the bucket!  A very enjoyable challenge.  Shout out to GSAir for writing the python.  Only fair since I'd written his code for Smart Cipher #3.
