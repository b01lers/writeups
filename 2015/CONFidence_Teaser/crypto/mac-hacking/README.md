# CONFidence Teaser : Power Level

#### Author: Wh1t3Fox & GSAir

We are given the following source code:

    <?php
    // secret vars
    include('secrets.php');
    function do_xor($a,$b) {
      $s = '';
      for ($i=0; $i < max(strlen($a),strlen($b)); $i++) {
        $x = $i < strlen($a) ? ord($a[$i]) : 0;
        $y = $i < strlen($b) ? ord($b[$i]) : 0;
        $s .= chr($x ^ $y);
      }
      return $s;
    }
    if (!$_GET) {
       highlight_file(__FILE__);
       exit(0);
    }
    // user vars
    $action = $_GET['a'];
    $method = $_GET['m'];
    $data = $_GET['d'];
    $signature = $_GET['s'];
    if ($action == 'sign') {
       $to_sign = $data;
       if (strstr($data,'get')) {
          die('get word not allowed');
       }
       if ($method == 'old') {
          echo md5(do_xor($data,$secret));
       } else {
          echo hash_hmac('md5',$data, $secret);
       }
    } else if ($action == 'verify') {
      if ($method == 'old')
         die('deprecated');
      if ($signature == hash_hmac('md5',$data, $secret)) {
        if (strstr($data, 'get flag')) {
          echo $flag;
        }
      }
    }
    ?>

HMAC is constructed using the following formula:

    HMAC(hash, data, key) = hash(key XOR (0x5c repeated 64 times) + hash(key XOR (0x36 repeated 64 times) + data))

If we use a method=old, and action=sign when can get the value of this, which lead us to believe it was a hash length extension attack.

First we define a function to query the remote server:

    def query(m, a, d, s):
        payload = {'m':m, 'a':a, 'd':d, 's':s}
        r = requests.get("http://95.138.166.219/", params=payload)
        return r



Next, we crafted our first payload using (0x36 repeated 64 times) + "a"

    digest  =  query('old', 'sign', '\x36'*64+'a', '')

After getting the output we performed the hash length extension attack which gives us our new data and a new hash.

    result = hashpump(digest.text.strip(), 'a', ' get flag', 64)

the next payload we use is (0x5c repeated 64 times) + previous_hash.

    r2 = query('old', 'sign', '\x5c'*64+result[0].decode('hex'), '')

Finally, we want to send a verify request with the data from our extension attack and the the signature from our last payload

    r3 = query('', 'verify', result[1], r2.text.strip())

After printing out the result we get the flag:

    DrgnS{MyHardWorkByTheseWordsGuardedPleaseDontStealMasterCryptoProgrammer}

###Full Code

    from hashpumpy import hashpump
    import requests


    def query(m, a, d, s):
        payload = {'m':m, 'a':a, 'd':d, 's':s}
        r = requests.get("http://95.138.166.219/", params=payload)
        return r



    digest  =  query('old', 'sign', '\x36'*64+'a', '')
    print digest.url
    print
    print digest.text.strip()
    print

    result = hashpump(digest.text.strip(), 'a', ' get flag', 64)
    print
    print result
    print

    r2 = query('old', 'sign', '\x5c'*64+result[0].decode('hex'), '')
    print
    print r2.url
    print
    print r2.text.strip()
    print

    r3 = query('', 'verify', result[1], r2.text.strip())
    print
    print r3.url
    print
    print r3.text.strip()
    print
