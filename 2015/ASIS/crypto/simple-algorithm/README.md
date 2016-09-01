# ASIS : Simple Algorithm

#### Author: Doomkin

**Description**:
> The flag is encrypted by this code, can you decrypt it after finding the system?

We are given a function and a while loop that is encrypting each..


	flag = '[censored]'
	hflag = flag.encode('hex')
	iflag = int(hflag[2:], 16)

	def FAN(n, m):
		i = 0
		z = []
		s = 0
		while n > 0:
			if n % 2 != 0:
				z.append(2 - (n % 4))
			else:
				z.append(0)
			n = (n - z[i])/2
			i = i + 1
		z = z[::-1]
		l = len(z)
		for i in range(0, l):
			s += z[i] * m ** (l - 1 - i)
		return s

	i = 0
	r = ''
	while i < len(str(iflag)):
		d = str(iflag)[i:i+2]
		nf = FAN(int(d), 3)
		r += str(nf)
		i += 2

	print r

Ok so we see from a string, encode it to hex, convert to decimal, then start the loop.
In the loop, it picks out every 2 digits, calls our method FAN and concats the result.

Since we only use 2 digit combinations, we can just map all the possibilities into a list.
Simple enough..

	vals=[0]*100
	for i in range(100):
		vals[i]=str(FAN(i,3))

Important note: Max length produced is 4 digits long
Now we can reverse brute force the FAN method, doesn't matter what it actually does!

	def decrypt(vals, r):
		l = len(r)
		i=0
		result=[]
		while i < l:
			built=''
			last=''
			f=1
			lasti=0
			for k in range(4):
				if i+k >= l:
					break
				built+=r[i+k]
				for j in range(len(vals)):
					if vals[j] == built:
						f=k+1   
						last=built
						lasti=j

			if(lasti != 0 and last != '0'):
				result.append(str(lasti))           
			i+=f
		return result

How this is done:
* Iterate over each number in our encrypted string
* From each character, check if the 1-4 digit numbers are mapped
  * For the string '12345' we check '1' then '12' then '123' then '1234'
  * Problem! There are collisions!
    * We tried greedily taking smallest and largest, turns out taking largest worked!
    * So the function above takes the last-most found match and appends it to our result
	* lasti of 0 and last of '0' typically meant nothing was found
* Lastly, increment our i by the number of digits we just parsed

Since we know the string is ASIS{md5 sum}, we encrypted two dummy texts, a max and a min.
For the flag: ASIS{ffffffffffffffffffffffffffffffff} we get
* 41420276958743086674184599393451194364747753431213139249921972481178760143812899843237501
For the flag: ASIS{aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa} we get
* 41420276958161855794875718098776014518429633736890842856306208081294424035851610408182141

Taking a look, we see a predetermined length and the start of the sequence is '41420276958'

Now, let's run our input through the decrypt method and see what we get!
* 414227695814376328653498326238859617348245863283796564325543769593976761661865423288189
Something looks off.. comparing it side by side with the two above, we see we're missing leading zeros!
So digit combinations like 02 are being added as 2. Write a quick fixup since we're using strings already, so not sure where the leading zero is being dropped..

	fix=''
	l=len(result)
	for x in result:
		if int(x) < 10:
			fix+='0'
		fix+=x

This gives us..
* 414202769581437632865349832623885906173482458632837965643255437695939767616618654232881809

Hmm.. it's one digit too long.. some quick thinking and -- the last digit in our list could be a single digit without a leading zero if there are an uneven number of digits.
Changing that 09 at the end to 9, and convert it back to string..

	print "answer: " + hex(int(fix))[2:-1].decode('hex')

* answer: SIS{a9ab115c488a311896dac4e8bc20a6d7}

Easy enough, add that A to the start and we get some points!
