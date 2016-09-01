# ASIS : KeyLead

#### Author: Doomkin

**Description**:
> Find the flag in this file.

Let's run it and see what it does!

	hi all ----------------------
	Welcome to dice game!
	You have to roll 5 dices and get 3, 1, 3, 3, 7 in order.
	Press enter to roll.

	You rolled 5, 6, 1, 4, 4.
	You DID NOT roll as I said!
	Bye bye~

Looks simple enough. Loading in IDA, we see the following:
* Several calls to rand() that is seeded by time()
* Several checks if time() is 2+ seconds after the seeded time() call - telling us not to cheat, heh
* Each check is coupled with a check for 3 then 1 then 3, etc.
* If each is passed, we've got a function call. I'll assume that gives us the flag.

Checking the funtion we suspect has the flag, nothing seems constant we can pull from it so..
From this point, we thought OK - let's find a time() I can set the system to that seeds it to produce the results since RNG aren't random.
But then, oh wait.. let's just nop all the conditions, beautiful \x90 how we love you. Running our new program we get..

	hi all ----------------------
	Welcome to dice game!
	You have to roll 5 dices and get 3, 1, 3, 3, 7 in order.
	Press enter to roll.

	You rolled 1, 6, 5, 4, 6.
	You rolled as I said! I'll give you the flag.
	ASIS{1fc1089e328eaf737c882ca0b10fcfe6}

Easy enough :) fun points!
