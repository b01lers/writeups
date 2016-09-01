# 9447 : darklang

#### Author: GSAir

**Description**:
> if you see this task while scroling
> 
> you have been visited by the reversing task of the 9447 ctf
> good flags and points will come to you
>
> but only if you submit '9447{`dankcode main.dc`}' to this task.

Look at this amazing code:

    >wewlad fail(memes, calcium)
    	>be dank like :^)
    	>implying calcium < memes
    		>implying memes % calcium is 0
    			>be dank like :^(
    		>or not
    			>wew fail(memes, calcium + 1)
    			>be dank like wew
    		>done implying
    	>done implying
    	>tfw dank

    >wewlad epicfail(memes)
    	>be wow like 0
    	>be dank like :^)
    	>implying memes > 1
    		>wew fail(memes, 2)
    		>be dank like wew
    		>implying dank
    			>wew bill(memes - 1)
    			>be wow like wew + 1
    		>or not
    			>wew such(memes - 1)
    			>be wow like wew
    		>done implying
    	>done implying
    	>tfw wow

    >wewlad dootdoot(memes, seals)
    	>be doritos like 0
    	>implying seals > memes
    	>or not
    		>implying seals is 0
    			>be doritos like 1
    		>or not
    			>implying seals is memes
    				>be doritos like 1
    			>or not
    				>wew dootdoot(memes - 1, seals - 1)
    				>be doritos like wew
    				>wew dootdoot(memes - 1, seals)
    				>be doritos like wew + doritos
    			>done implying
    		>done implying
    	>done implying
    	>tfw doritos

    >wewlad such(memes)
    	>wew dootdoot(memes, 5)
    	>be wow like wew
    	>implying wow % 7 is 0
    		>wew bill(memes - 1)
    		>be wow like wow + 1
    	>or not
    		>wew epicfail(memes - 1)
    	>done implying
    	>be wow like wew + wow
    	>tfw wow

    >wewlad brotherman(memes)
    	>be hues like 0
    	>implying memes isn't 0
    		>implying memes < 3
    			>be hues like 1
    		>or not
    			>wew brotherman(memes - 1)
    			>be hues like wew
    			>wew brotherman(memes - 2)
    			>be hues like wew + hues
    		>done implying
    	>done implying
    	>be hues like hues % 987654321
    	>tfw hues

    >wewlad bill(memes)
    	>wew brotherman(memes)
    	>be wow like wew
    	>implying wow % 3 is 0
    		>wew such(memes - 1)
    		>be wow like wow + 1
    	>or not
    		>wew epicfail(memes - 1)
    	>done implying
    	>be wow like wew + wow
    	>tfw wow

    >be me
    	>be memes like 13379447
    	>wew epicfail(memes)
    	>mfw wew
    	>thank mr skeltal



The first idea was to convert this language into a python script and run it. Of course this was not that easy.

There were 6 functions heavily recursive, we need to remove that because all were useless.

Three were three well- known functions:

 1. `fail` was a primary test function.
 2. `brotherman` was modular Fibonacci
 3. `dootdoot` was computing combinations

We know that the highest input for all these function is  13379447. So here are our optimizations:

 1. make a sieve of size 13379447
 2. make a table with the value of all Fibonacci numbers up to 13379447 (take a couple of hour)
 3. the size of the combinations was always 5, so the computation can be made in 5 multiplication and one division

The three other functions were calling each other based on the result of the three previous. I in-lined them in a state machine, here is the code:


There were

    import json
    import math

    # primality test
    memes = 13379447
    sieve = [1] * (memes + 1)
    for i in xrange(2, int(math.sqrt(memes + 1)) + 2):
        if sieve[i] == 1:
            j = i + i
            while j < len(sieve):
                sieve[j] = 0
                j += i

    def fail(memes, calcium):
        return sieve[memes] == 1

    # combinations
    def dootdoot(memes, seals):
        num = 1
        den = 1
        for i in xrange(seals):
            num *= (memes - i)
            den *= (i + 1)

        return num/den

    # Fibonacci
    with open("fibo.json") as f:
        dic_br = json.load(f)

    def brotherman(memes):
        return dic_br[str(memes)]

    # state machine
    def epicfail(memes):
        wow = 0
        state = "epicfail"
        while True:
            if state == "epicfail":
                if memes > 1:
                    if fail(memes, 2):
                        state = "bill"
                        memes -= 1
                        wow += 1
                    else:
                        state = "such"
                        memes -= 1
                else:
                    return wow
            elif state == "bill":
                bwow = brotherman(memes)
                if bwow % 3 == 0:
                    state = "such"
                    memes -= 1
                    wow += 1
                else:
                    state = "epicfail"
                    memes -= 1

                wow += bwow
            elif state == "such":
                swow = dootdoot(memes, 5)
                if swow % 7 == 0:
                    state = "bill"
                    memes -= 1
                    wow += 1
                else:
                    state = "epicfail"
                    memes -= 1

                wow += swow

    print "9447{" + epicfail(memes) + "}"
