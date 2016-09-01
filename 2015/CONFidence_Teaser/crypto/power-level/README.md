# CONFidence Teaser : Power Level

#### Author: GSAir

**Description**:
> Here's a C file. Decode this
>
> 8,223,137,2,42,8,28,186,97,114,42,74,163,238,163,23,121,2,74,158,163,23,135,2,193,158,2,62,2,184,44,20,2,137,217,196,62,249,159,137,44,111,106,111,217,50,106,111,2,62,196,217,137,2,20,106,146,111,151

- The cipher which is given to use has been enciphered using the C file. The encryption process is the following:

        unsigned int a,b,c,d,v;

        unsigned int f(unsigned int x)
        {
            return a*x*x*x + b*x*x + c*x + d;
        }

        // Somewhere in the main
        a = (unsigned int)plaintext[0];
        b = (unsigned int)plaintext[1];
        c = (unsigned int)plainext[2];
        d = (unsigned int)plaintext[3];
        for(i=0;i<len;i++)
        {
            v = f(plaintext[i]);
            v = e[v%1000](plainext[i]) ^ (v%251);
            printf("%d ", v);
        }

  - So first the plaintext is split per characters, and each character is encrypted based on the four first character (through f) and then with 1000 different functions (derteministic and very small) which are not displayed here (through the e array).

  - My first idea was to use 'D', 'r', 'g' and 'n' for the first letters, but unfortunately it didn't match the beginning of the ciphertext... So I realized that each character has only 256 possible value, 4 characters => 2^32 possibility pretty easy for nowday computer:

        for (a = 0 ; a < 256 ; a++) {
            for (b = 0 ; b < 256 ; b++) {
                for (c = 0 ; c < 256 ; c++) {
                    for (d = 0 ; d < 256 ; d++) {
                        v = f(d);
                        if ((e[v%1000](d) ^ (v%251)) == 2) {
                            v = f(c);
                            if ((e[v%1000](c) ^ (v%251)) == 137) {
                                v = f(b);
                                if ((e[v%1000](b) ^ (v%251)) == 223) {
                                    v = f(a);
                                    if ((e[v%1000](a) ^ (v%251)) == 8) {
                                        printf("yes : %c, %c, %c, %c\n", a, b, c, d);
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

 - in about 2min we get: `yes : ~, F, 1, a`. So only one quadruplet match for the beginning of the ciphertext, that is good new. Let's make a rainbow table for all the characters (256 entries...).

        a = (unsigned int)'~';
        b = (unsigned int)'F';
        c = (unsigned int)'1';
        d = (unsigned int)'a';

        for (i = 0 ; i < 256 ; i++) {
            v = f((char)i);
            rainbow[i] = e[v%1000]((char)i) ^ (v%251);
        }

- We see that the encryption is not completely invertible,  `P f v` have the same ciphertext... Therefore I output all possible printable characters for each numbers:

        for (i = 0 ; i == 0 || cipher[i-1] != 151 ; i++) {
            j = 0;
            printf("(%u)\t-> ", cipher[i]);
            for (j = 0 ; j < 256 ; j++) {
                if ((cipher[i] == rainbow[j]) && ISLETTER(j)) {
                    printf("%c ", j);
                }
            }
            printf("\n");
        }

 - the output is:

        (8)    	-> ~
        (223)	-> F
        (137)	-> 1
        (2)    	-> ; a
        (42)  	-> O g
        (8)    	-> ~
        (28)  	-> :
        (186)	->   
        (97)  	-> D
        (114)	-> = r
        (42)  	-> O g
        (74)  	-> n
        (163)	-> S U
        (238)	-> {
        (163)	-> S U
        (23)  	-> o
        (121)	-> M h
        (2)    	-> ; a
        (74)  	-> n
        (158)	-> y
        (163)	-> S U
        (23)  	-> o
        (135)	-> E Q
        (2)    	-> ; a
        (193)	-> s
        (158)	-> y
        (2)    	-> ; a
        (62)  	-> P f v
        (2)    	-> ; a
        (184)	-> 5
        (44)  	-> 6
        (20)  	-> b
        (2)    	-> ; a
        (137)	-> 1
        (217)	-> 9
        (196)	-> c
        (62)	-> P f v
        (249)	-> d
        (159)	-> 8
        (137)	-> 1
        (44)	-> 6
        (111)	-> e
        (106)	-> 3
        (111)	-> e
        (217)	-> 9
        (50)	-> , 7
        (106)	-> 3
        (111)	-> e
        (2)    	-> ; a
        (62)	-> P f v
        (196)	-> c
        (217)	-> 9
        (137)	-> 1
        (2)    	-> ; a
        (20)	-> b
        (106)	-> 3
        (146)	-> 4
        (111)	-> e
        (151)	-> }

- The first part is easy to filter: `~F1ag~: Drgn{SoManySoEasy` but the next part doesn't make any sense... Looking closer every single character are a hex digits, and there is only one hex digits when there are multiple possibilities :)

###Flag: DrgnS{SoManySoEasyafa56ba19cfd816e3e973eafc91ab34e}
