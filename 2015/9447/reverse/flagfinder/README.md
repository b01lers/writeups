# 9447 : FlagFinder

#### Author: GSAir

**Description**:
> I've forgotten my flag. I remember it has the format "9447{<some string>}", but what could it be?
>
> Unfortunately the program no longer just prints the flag.

We first run the basic commands:

    file flagFinderRedux
    flagFinderRedux: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked (uses shared libs), for GNU/Linux 2.6.24, BuildID[sha1]=8c0c9c0d5c39ff0cc1954fa8682288b6169b8fff, stripped

    rabin2 -z flagFinderRedux
    [strings]
    addr=0x00400834 off=0x00000834 ordinal=000 sz=21 section=.rodata string=Usage: %s <password>
    addr=0x0040084a off=0x0000084a ordinal=001 sz=5 section=.rodata string=9447
    addr=0x0040084f off=0x0000084f ordinal=002 sz=15 section=.rodata string=The flag is %s
    addr=0x0040085f off=0x0000085f ordinal=003 sz=10 section=.rodata string=Try again
    addr=0x00601086 off=0x00001086 ordinal=000 sz=4 section=.data string=n<q
    addr=0x006010a0 off=0x000010a0 ordinal=001 sz=3 section=.data string=2J
    addr=0x006010a6 off=0x000010a6 ordinal=002 sz=3 section=.data string=1T
    addr=0x006010c0 off=0x000010c0 ordinal=003 sz=3 section=.data string=s
    addr=0x006010c3 off=0x000010c3 ordinal=004 sz=4 section=.data string=['_
    addr=0x006010d8 off=0x000010d8 ordinal=005 sz=5 section=.data string=M*4.
    addr=0x006010dd off=0x000010dd ordinal=006 sz=4 section=.data string=zl7

Ok it has to be a little bit more complex, let's run it:

    $ ./flagFinderRedux
    Usage: ./flagFinderRedux <password>
    $ ./flagFinderRedux flag
    Try again

So there is a password, we guess that if we give the good password then the flag will be displayed because of the string `addr=0x0040084f`. Let's see what `ltrace` can tell us something on the value of the password

    ltrace ./flagFinderRedux flag
    __libc_start_main(0x40063e, 2, 0x7fffb9270508, 0x4007b0 <unfinished ...>
    strcpy(0x7fffb9270380, "2J\333\245\333\r1T\324A\361\211\227\343O\331\362\355\v\377\311\343K\341j\032\033\332\005\254\347\202"...) = 0x7fffb9270380
    memcmp(0x7fffb9270380, 0x40084a, 4, 0xcd874c9c) = 0xfffffff9
    memcmp(0x7fffb9270380, 0x40084a, 4, 34) = 0xffffffe9
    memcmp(0x7fffb9270380, 0x40084a, 4, 166) = 0xffffffe9
    memcmp(0x7fffb9270380, 0x40084a, 4, 0) = 0xffffffe9
    memcmp(0x7fffb9270380, 0x40084a, 4, 202) = 0xffffffe9
    ...
    ...
    FOREVERRRRR

OK so there must be kind of anti debugging stuff going on. We may notice a string copied at the beginning, but it doesn't make much sense... We need to fire radare now...

    r2 flagFinderRedux
    [0x00400520]> aa
    [0x00400520]> pdf@main
    <<lot of weird stuff>>
    ....
           0x004006fb    be4a084000   mov esi, str.9447
           0x00400700    4889c7       mov rdi, rax
           0x00400703    e8f8fdffff   call sym.imp.memcmp
             sym.imp.memcmp()
           0x00400708    85c0         test eax, eax
      ,==< 0x0040070a    7551         jnz 0x40075d
      |    ; DATA XREF from 0x0040108c (unk)
      |    0x0040070c    8b057a092000 mov eax, [rip+0x20097a] ; 0x0040108c
      |    0x00400712    89c2         mov edx, eax
      |    0x00400714    488b45b0     mov rax, [rbp-0x50]
      |    0x00400718    4883c008     add rax, 0x8
      |    0x0040071c    488b08       mov rcx, [rax]
      |    0x0040071f    488b45d8     mov rax, [rbp-0x28]
      |    0x00400723    4889ce       mov rsi, rcx
      |    0x00400726    4889c7       mov rdi, rax
      |    0x00400729    e8d2fdffff   call sym.imp.memcmp
      |       sym.imp.memcmp()
      |    0x0040072e    85c0         test eax, eax
     ,===< 0x00400730    751f         jnz 0x400751
     ||    0x00400732    488b45b0     mov rax, [rbp-0x50]
     ||    0x00400736    4883c008     add rax, 0x8
     ||    0x0040073a    488b00       mov rax, [rax]
     ||    0x0040073d    4889c6       mov rsi, rax
     ||    0x00400740    bf4f084000   mov edi, str.Theflagiss
     ||    0x00400745    b800000000   mov eax, 0x0
     ||    0x0040074a    e891fdffff   call sym.imp.printf
     ||       sym.imp.printf()
    ,====< 0x0040074f    eb4a         jmp fcn.0040079b
     |`---> 0x00400751    bf5f084000   mov edi, str.Tryagain
    | |    0x00400756    e875fdffff   call sym.imp.puts
    ....

We can see at `0x0040074a` the print statement when the password is correct and `0x00400756` when it is incorrect.

The `memcmp at `0x00400729` seems interesting, let's use `gdb` to see what they are comparing:

    $ gdb flagFinderRedux
    (gdb) break *0x00400729
    Breakpoint 1 at 0x400729
    (gdb) r test
    Starting program: CTF/9447CTF15/flagfinder/flagFinderRedux test

    Breakpoint 1, 0x0000000000400729 in ?? ()
    (gdb) x/s $rsi
    0x7fffffffe592:	"test"
    (gdb) x/s $rdi
    0x7fffffffe140:	"9447{C0ngr47ulaT1ons_p4l_buddy_y0Uv3_solved_the_re4l__H4LT1N6_prObL3M}"
    (gdb)

Sweet a flag!!

###Flag: 9447{C0ngr47ulaT1ons_p4l_buddy_y0Uv3_solved_the_re4l__H4LT1N6_prObL3M}
