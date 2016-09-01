# UIUCTF : Hype

#### Author: Wh1t3Fox

**Description**:
> We are given the clue: A lot of Hyperboria related things are often abbreviated with hype

Hyperboria is linked to a website http://a050032a39d870de1be70314b90d0917.tk/ and after some Googling I found out that Hyperboria is a mesh network that uses IPv6 for communication. After fiddling around for a while and getting an IPv6 on my machine I pinged the domain.

    ping6 a050032a39d870de1be70314b90d0917.tk

	PING a050032a39d870de1be70314b90d0917.tk(fcbe:4b13:cb2d:6d85:b2e6:f8ec:d290:39b8) 56 data bytes
	64 bytes from fcbe:4b13:cb2d:6d85:b2e6:f8ec:d290:39b8: icmp_seq=1 ttl=42 time=263 ms
	64 bytes from fcbe:4b13:cb2d:6d85:b2e6:f8ec:d290:39b8: icmp_seq=2 ttl=42 time=263 ms
	64 bytes from fcbe:4b13:cb2d:6d85:b2e6:f8ec:d290:39b8: icmp_seq=3 ttl=42 time=333 ms
	^C
	--- a050032a39d870de1be70314b90d0917.tk ping statistics ---
	3 packets transmitted, 3 received, 0% packet loss, time 2002ms
	rtt min/avg/max/mdev = 263.811/286.908/333.039/32.624 ms


After getting the IPv6 address I entered it into the url: http://[fcbe:4b13:cb2d:6d85:b2e6:f8ec:d290:39b8] and was presented with the flag: a440c1fb4e7261fedea3b47740eff9b77bd48382f1164c2e9ca6656125c0eb31
