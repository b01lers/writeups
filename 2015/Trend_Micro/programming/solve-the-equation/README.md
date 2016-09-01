# Trend Micro : Solve the Equation

#### Author: yfb76

You connect, they send you and equation ending with an '='.  First reaction, this is too easy!  Just write some python to connect, parse out the '=' and pass the string to eval().  

Note: if for some reason you want to parse the equation and do order of operations etc yourself, this is a cool but little known algorithm that is easier to implement than a full grammar (unless you use lex / yacc - but that's another story):

[Dijkstra's Shunting Yard Algorithm](https://en.wikipedia.org/wiki/Shunting-yard_algorithm "Dijkstra's Shunting Yard Algorithm")

Yes But...
-------------

That worked, until it didn't ;).  First problem was that numbers > 999 have commas.  Fine, we add some python to strip all commas out.  That was just the tip of the iceberg though.

Here there be Romans!
--------------------------------

Just to mess with us, they started sending Roman numerals instead of numbers.  Cute.  Somebody somewhere must have dealt with this before right?  To Google we go, and sure enough there is some decent code (I adapted it a bit) on stack overflow.  Cool beans, we've made like the Visigoths and sacked Rome!

Here there be English!
-------------------------------

Not content with Roman numerals they started writing out numbers: "nine + four" etc.  We created a massive dicitonary for every number we use (1 - 20, 30, 40, ..., 100, 1000, etc).  We can now look everything up.  Now we just need a strategy to recreate large numbers.  Notice that when we spell numbers out, they all follow the pattern: (some number <= 999) (PLACE) .... where PLACE can be thousand, million, or billion for this challenge.  We calculate the hundreds, then multiply by place and store it, and so on until we are out of number.  Add them back together and et voila.  This will be clearer in the code.  

1337 > Newb
-------------------

they then started to mix together numbers, roman numerals, and the spelled out numbers.  However, b/c we are 1337 programmers and wrote good code, this phased us not at all.

Set our code loose on their input, and eventually they surrender and give us the FLAG!!!

Code
===

        #!/bin/usr/local/python

        import socket

        table=[('M',1000),('CM',900),('D',500),('CD',400),('C',100),('XC',90),('L',50),('XL',40),('X',10),('IX',9),('V',5),('IV',4),('I',1)]

        def rom_to_int(equation):
            print "converting " + equation + " =" ,
            result = 0
            for letter, value in table:
                while equation.startswith(letter):
                    result += value
                    equation = equation[len(letter):]
            print str(result)
            return str(result)

        numbers = {'one' : 1, 'two' : 2, 'three' : 3, 'four' : 4, 'five' : 5, 'six' : 6, 'seven' : 7, 'eight' : 8,
                    'nine' : 9, 'zero' : 0 , 'ten' : 10, 'eleven' : 11, 'twelve' : 12, 'thirteen' : 13,
                    'fourteen' : 14, 'fifteen' : 15, 'sixteen' : 16, 'seventeen' : 17, 'eighteen' : 18,
                    'nineteen' : 19, 'twenty' : 20, 'thirty' : 30, 'forty' : 40, 'fifty' : 50,
                    'sixty': 60, 'seventy' : 70, 'eighty' : 80, 'ninety' : 90}

        def convert(equation):
            tmp = equation.split(' ')
            result = ""
            bill = 0
            mill = 0
            thou = 0
            hund = 0
            use_cur = False
            for tok in tmp:
                if(tok.isalpha()):
                    if(tok[0].isupper()):
                        result += rom_to_int(tok) + " "
                    else:
                        use_cur = True
                        if tok in numbers.keys():
                            hund += numbers[tok]
                        elif tok == 'hundred':
                            hund *= 100    
                        elif tok == 'thousand':
                            thou += hund
                            thou *= 10 ** 3
                            hund = 0
                        elif tok == 'million':
                            mill += hund
                            mill *= 10 ** 6
                            hund = 0
                        elif tok == 'billion':
                            bill += hund
                            bill *= 10 ** 9
                            hund = 0
                else:
                    if use_cur:
                        num = bill + mill + thou + hund
                        result += str(num) + " "
                        print num
                        use_cur = False
                        bill = hund = thou = mill = 0
                    result += tok + " "
            if use_cur:
                num = bill + mill + thou + hund
                result += str(acc) + " "
            return result

        ip = "ctfquest.trendmicro.co.jp"
        port = 51740

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))

        while(1):
            equation = sock.recv(1024)
            if equation.startswith("Congratulations!"):
                print sock.recv(1024)
            equation = equation.split('=')[0].replace(',', '')
            print equation
            equation = convert(equation)
            answer = str(eval(equation))
            print "= " + answer
            print "---------"
            sock.sendall(answer+"\n")
