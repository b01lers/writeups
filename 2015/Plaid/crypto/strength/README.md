# Plaid : Strength

#### Author: GSAir

**Description**:
> We captured a list of tuple {N : e : c} with the information that the flag has been encrypted several time.

- Based on the notation used, we assumed that it is an RSA cipher, and looking at the file we noticed that the modulus is constant for every tuple... BAD IDEAA but good for us :)
 - We now look for `(e1, e2)` such that `gcd(e1, e2) = 1`

       import gmpy
       import fractions

       l = []

       with open("captured", "r") as f:
           for line in f:
               l.append([eval(x) for x in line.split(":")])

       match = []
       num = 0

       for N, e, c in l:
           for nN, ne, nc in l:
               if (fractions.gcd(e, ne) == 1):
                   match.append([[N, e, c],[nN, ne, nc]])

       N, e1, c1 = match[0][0]
       N, e2, c2 = match[0][1]

- We compute `(a, b)` such that `e1 * a + e2 * b = 1` and then the message is recover `flag = c1^a * c2^b mod N`
-  Unfortunately `a` is negative, we then compute `i = c1^(-1) mod N` and `flag = i^(-a) * c2^b mod N`

       t, a, b = gmpy.gcdext(e1, e2)

       i = gmpy.invert(c1, N)

       val = (pow(i, -a, N) * pow(c2, b, N)) % N

       print hex(long(val))[2:-1:].decode('hex')

Youpi we have the flag :)

### Flag flag\_Strength\_Lies\_In\_Differences
