# ASIS : Golden Metal

#### Author: GSAir

**Description**:
> The flag is encrypted by this code, can you decrypt it after finding the system?

- The crypto system is using a public key (N,x)
- It is encrypting the plaintext one bits `b` at a time:

y = random value
c = (x^(y << 1 | b) * y^2) mod N

- First the modulus `N` is a Blum number, however it is quite useless for this challenge, maybe a false lead. So `N = pq` for two different prime numbers.
- Secondly `x` is chosen to be a  Quadratic Non Residu modulo `p` and `q`. Therefore `x^(2n)`  is a Quadratic Residu modulo `p` and `q`, `x^(2n + 1)` is a Quadratic Non Residu modulo `p` and `q`. And any `y^2` is a Quadratic Residu modulo `p`and `q`. Therefore with he factorization of `N` we can decide if `c` is a QNR => 1, QR => 0.
- Note every `c` are QR modulo `N`, the problem is difficult without factorization.

We used msieve to factorize `N`:

   import gmpy

   with open('pub.txt') as f:
       exec(f.read())

   with open('enc.txt') as f:
       exec(f.read())

   N = key[1]
   x = key[0]

   p = 1285380609783825451015579898011805465763518244839
   q = 1358902095093762824984385249873903079031552839163

   assert(N == p * q)

   flag = ""
   for c in enc:
       if (gmpy.jacobi(c, p) == 1 and gmpy.jacobi(c, p) == 1):
           flag += "0"
       else:
           flag += "1"

   print hex(int(flag, 2))[2:-1].decode('hex')

###Flag: ASIS{3c4cbc2d6bc6ebbbbbe967b8af5ac414}
