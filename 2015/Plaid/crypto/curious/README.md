# Plaid : Curious

#### Author: GSAir

**Description**:
> We captured a list of tuple {N : e : c} with the information that the flag has been encrypted several time.

- Based on the notation used, we assumed that it is an RSA cipher, and looking at the file we noticed that the values of `e` are quite larger than usual. It may mean that the corresponding `d` is small let's try a Wiener factorization!
  - I found this nice python code online : https://github.com/pablocelayes/rsa-wiener-attack and here my code:

        import ContinuedFractions, Arithmetic, RSAvulnerableKeyGenerator

        def hack_RSA(e,n):
            '''
            Finds d knowing (e,n)
            applying the Wiener continued fraction attack
            '''
            frac = ContinuedFractions.rational_to_contfrac(e, n)
            convergents = ContinuedFractions.convergents_from_contfrac(frac)

            for (k,d) in convergents:

                #check if d is actually the key
                if k!=0 and (e*d-1)%k == 0:
                    phi = (e*d-1)//k
                    s = n - phi + 1
                    # check if the equation x^2 - s*x + n = 0
                    # has integer roots
                    discr = s*s - 4*n
                    if(discr>=0):
                        t = Arithmetic.is_perfect_square(discr)
                        if t!=-1 and (s+t)%2==0:
                            print("Hacked!")
                            return d

            return None

        l = []

        with open("captured", "r") as f:
        for line in f:
            l.append([eval(x) for x in line.split(":")])

        for N, e, c in l:
            d = hack_RSA(e, N)
            if (d):
                val = pow(c, d, N)
                print hex(long(val))[2:-1:].decode('hex')
                break

:)))))


###Flag flag_S0Y0UKN0WW13N3R$4TT4CK!
