# CSAW : FTP

#### Author: yfb76

This challenge was to reverse a x86_64 bit, stripped executable.  Lacking an IDA Pro license, we fired up Radare2.  We found the address of main from the call to libc_start_main at the beginning of the text section.  main() primarily set up a socket and handled incoming connections.  We moved on to the function that handles a new incoming connection, and from there to user authentication.  We discovered that you log in by sending:

    user <name>
    pass <password>

Further, the only allowed user is "blankwall", which was a static string.  We then reversed the password authentication section.  Once we had that, we wrote a python script to check it against the simple dictionary found on Linux, and got lucky.  The python is:

        import sys

        def f(s):
            p = 0x1505
            for c in s:
                y = (p << 5) & 0xFFFFFFFF
                y = (y + p) & 0xFFFFFFFF
                p = (y + ord(c)) & 0xFFFFFFFF

            return p

        with open('/usr/share/dict/cracklib-small') as fr:
            for line in fr:
                if(f(line) == 0xd386d209):
                    print line
                    sys.exit()

where f() is the reversed authentication function.  This very quickly spit out the password, cookie.  Great! We can now login.  Fortunately. there is a help command that displayed the option.  Using pasv to set up a outgoing connection, and then List we see that there is a flag.txt .  However, this is a RED HERRING as it contains the flag for the second FTP challenge.  

Searching for what to do next we ran

    rabin2 -z ftp

which lists the strings AND their locations.  We saw one that said congratulations for the reversing challenge.  We went there in the code and poked around some.  We discovered that to get there you have to issue a HIDDEN command: RDF.  We logged in and issued that and were rewarded!  Fun stuff.
