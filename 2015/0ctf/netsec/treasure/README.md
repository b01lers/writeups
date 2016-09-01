# 0ctf : Treasure

#### Author: gannimo

We are told that there's a treasure waiting at "treasure.ctf.0ops.sjtu.cn"
so we have to start digging!

Firing up dig:

	dig treasure.ctf.0ops.sjtu.cn -t ANY

tells us that the target is a IPv6 address.

Let's do a traceroute to that address:

	$ traceroute6 treasure.ctf.0ops.sjtu.cn
	...
	25  0000000110001101110000000 (2001:470:d:b28::14:2)  79.101 ms  78.517 ms
		74.130 ms
	26  0111110111100111110111110 (2001:470:d:b28::15:2)  79.776 ms  74.481 ms
		79.247 ms
	27  0100010110001100110100010 (2001:470:d:b28::16:2)  73.597 ms  78.433 ms
		88.964 ms
	28  0100010101000011010100010 (2001:470:d:b28::17:2)  89.942 ms  88.982 ms
		89.823 ms
	29  0100010101010101110100010 (2001:470:d:b28::18:2)  88.834 ms  89.702 ms
		92.050 ms
	30  0111110110011011010111110 (2001:470:d:b28::19:2)  91.862 ms  79.223 ms
		79.132 ms


These look like bit patterns. But unfortunately traceroute stops after 30
hops. So let's resolve the remaining entries as well until we reach the
target address (we see that linearly increasing pattern for the addresses).

Let's continue with the remaining IPv6 addresses using a reverse lookup
using dig -x to the remaining addresses and we get the following bit
patterns:

	0000000110001101110000000 14
	0111110111100111110111110 15
	0100010110001100110100010 16
	0100010101000011010100010 17
	0100010101010101110100010 18
	0111110110011011010111110 19
	0000000101010101010000000 20
	1111111110111100111111111 21
	0011100010001010011100111 22
	0100011011001101101000000 23
	0101010000111110110010100 24
	0011111011010110011010101 25
	1001010100000111010010000 26
	0001111100000101001010110 27
	0110110100110010110100000 28
	0100101001101111101000010 29
	0110100101100000000001010 30
	1111111100111011011101001 31
	0000000101101110010101100 32
	0111110101111100011100110 33
	0100010110011010000001101 34
	0100010111011101000011000 35
	0100010110010110111010010 36
	0111110100101111000010110 37
	0000000100000010010100110 38

After unsuccessfully trying  gazillion of 5, 6, and 8-bit encodings we saw a
pattern: at the top left there's box of 1's (as at the lower left and upper
right). So this actually looks like a QR code.

Dumping the bits into a file and hacking together a python script that
generates an image allows us to decode the QR code using a mobile app and QR
decoder. This results in the flag and 50 points.
