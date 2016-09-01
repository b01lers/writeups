# CSAW : Hacking Time

#### Author: ammar2

**Description**:
> This challenge was interesting, in that it involved reverse engineering an NES game. An architecture that most people aren't likely to be familiar with: 6502. Thankfully, the architecutre is stupidly simple, one accumulator and two registers, once you get past the hurdle of getting proper tools to debug the program, it isn't too difficult.

First things first, we need to run the game, so I quickly looked up the most popular NES emulator and [FCEUX](http://www.fceux.com/web/home.html) was the top hit. Once you load up and run the .nes file provided, it goes through a lot of text and button pressing after which you are required to enter a 24 digit password to proceed. After you enter the password, you need to press a button to proceed which kinda hints that the raw letters must be stored somewhere in memory.

Luckily FCEUX has great in built debugging tools, including a HEX editor that allows you to inspect the entirety of the NES's memory. By entering an easily identifiable passphrase, we can quickly determine where its being stored in memory.
![](https://i.imgur.com/C76tYGC.png)

After locating the password in memory, I right clicked the first byte and added a read breakpoint for that memory address so I could determine where in the assembly the password was being validated. This quickly pointed me to the following subroutine. I've commented it from my notes for readability.

       LDY #$00                     ;
       LDA #$00                     ; Reset the values in the accumulator and y register to 0
       STA $003B = #$00             ; Store the value of the accumulator, a.k.a 0 to the memory address 0x003B
    |->LDA $0005,Y @ $0005 = #$48   ; Load (0x0005 + Y) into the accumulator, essentially gets the first ascii letter(H) from the password array.
    |  TAX                          ; Transfer the accumulator to the x register
    |  ROL                          ; Rotate the accumulator one bit left
    |  TXA
    |  ROL
    |  TAX
    |  ROL
    |  TXA
    |  ROL
    |  TAX
    |  ROL
    |  TXA                          ; ...
    |  ROL                          ; All these operations essentially end up rotating the accumulator 3 bits left
    |  PHA                          ; Add the accumulator on top of the stack
    |  LDA $003B = #$00             ; Load the value at (0x003B) into the accumulator (0 initially)
    |  TAX
    |  ROR
    |  TXA
    |  ROR
    |  TAX
    |  ROR
    |  TXA                          ; ...
    |  ROR                          ; All these operations essentially end up rotating the accumulator 2 bits right
    |  STA $003B = #$00             ; Store the bit shifted value back to (0x003B)
    |  PLA                          ; Pop our old accumulator from the stack onto the accumulator
    |  CLC                          ; Clear the carry bit
    |  ADC $003B = #$00             ; Add the accumulator to the value we stored at 0x003B
    |  EOR $955E,Y @ $955E = #$70   ; XOR the accumulator with (0x955E + Y) where Y is the index of the loop
    |  STA $003B = #$00             ; Store the result back to (0x003B)
    |  TAX
    |  ROL
    |  TXA
    |  ROL
    |  TAX
    |  ROL
    |  TXA
    |  ROL
    |  TAX
    |  ROL
    |  TXA
    |  ROL
    |  TAX
    |  ROL
    |  TXA                          ; ...
    |  ROL                          ; All these operations essentially end up rotating the accumulator 4 bits right
    |  EOR $9576,Y @ $9576 = #$20   ; XOR the accumulator with (0x09576 + Y) where Y is the index of the loop
    |  STA $001E,Y @ $001E = #$03   ; Store the result of the XOR to (0x001E + Y), essentially acting as an array for this final result per letter
    |  INY                          ; Increment Y, the loop index
    |  CPY #$18                     ; Compare Y to 0x18
    -<-BNE $82F7                    ; Jump back to start of loop if they are not not equal

       LDY #$00                     ; Set Y, the loop index to 0
    |->LDA $001E,Y @ $001E = #$03   ; Load up the value at (0x001E + Y) to the accumulator
    |  BNE $8346                    ; If the loaded value isn't equal to zero, jumps and creates a failure condition
    |  INY                          ; Increment Y
    |  CPY #$18                     ; Compare Y to 0x18
    |-<BNE $8339                    ; Jump back to start of loop if they are not equal

       LDA #$01
       RTS ------------------------; Return this subroutine


My first response to this was to simply the comment/NO OP out the jumps, while this certainly got us pass the password screen, the game then said that the password was basically the flag which meant that there wasn't an easy way out, I actually had to work through the logic to figure out what a valid password would be.

After annotating the code, stepping through it and figuring out it was doing, I came up with the underlying logic and wrote it out in psuedo code.


    byte[] someMagicArray = {...};
    byte[] anotherMagicArray = {...};

    byte[] resultArray = new byte[24];
    byte something = 0;
    for (int i = 0; i < 24; i++) {
        x = input_ascii_letter[i];
        x = left_rotate(x, 3);
        something = right_rotate(something, 2)
        x += something;
        x ^= someMagicArray[i];
        something = x;
        x = right_rotate(x, 4);
        x ^= anotherMagicArray[i];
        resultArray[i] = x;
    }

    for (int i = 0; i < 24; i++) {
        if (resultArray[i]  != 0) {
            ERROR();
        }
    }
    SUCCESS();



After dumping out the contents of someMagicArray and anotherMagicArray at 0x09576 and 0x955E, it was trivial to write a program that brute forced the letters to put in to get 24 zeroes in our result array.

The code to do this is shown below:

    import sys

    def left_rotate(st, s):
            return ((st << s) | (st >> 8 - s)) & 0xFF

    def right_rotate(st, s):
            return left_rotate(st, 8 - s)

    tab2 = [0x20, 0xAC, 0x7A, 0x25, 0xD7, 0x9C, 0xC2, 0x1D, 0x58, 0xD0, 0x13, 0x25, 0x96, 0x6A, 0xDC, 0x7E, 0x2E, 0xB4, 0xB4, 0x10, 0xCB, 0x1D, 0xC2, 0x66]
    tab1 =  [0x70, 0x30, 0x53, 0xA1, 0xD3, 0x70, 0x3F, 0x64, 0xB3, 0x16, 0xE4, 0x04, 0x5F, 0x3A, 0xEE, 0x42, 0xB1, 0xA1, 0x37, 0x15, 0x6E, 0x88, 0x2A, 0xAB]
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890 "

    def brute_force(s):
            som = 0
            for i, y in enumerate(s):
                    x = ord(y)
                    x = left_rotate(x, 3)
                    som = right_rotate(som, 2)
                    x = (x + som) & 0xFF
                    x = x ^ tab1[i]
                    som = x
                    x = right_rotate(x, 4)
                    x = x ^ tab2[i]

            som = right_rotate(som, 2)
            i = len(s)
            for a in alphabet:
                    x = ord(a)
                    x = left_rotate(x, 3)
                    x = (x + som) & 0xFF
                    x = x ^ tab1[i]
                    x = right_rotate(x, 4)
                    x = x ^ tab2[i]
                    if x == 0:
                            return s + a

            print "No solutions"
            sys.exit(1)


    val = ""
    for i in xrange(0x18):
            val = brute_force(val)
            print val
and here we go:

    N
    NO
    NOH
    NOHA
    NOHAC
    NOHACK
    NOHACK4
    NOHACK4U
    NOHACK4UX
    NOHACK4UXW
    NOHACK4UXWR
    NOHACK4UXWRA
    NOHACK4UXWRAT
    NOHACK4UXWRATH
    NOHACK4UXWRATHO
    NOHACK4UXWRATHOF
    NOHACK4UXWRATHOFK
    NOHACK4UXWRATHOFKF
    NOHACK4UXWRATHOFKFU
    NOHACK4UXWRATHOFKFUH
    NOHACK4UXWRATHOFKFUHR
    NOHACK4UXWRATHOFKFUHRE
    NOHACK4UXWRATHOFKFUHRER
    NOHACK4UXWRATHOFKFUHRERX
