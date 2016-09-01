# Internetwache : SPIM

#### Author: yfb76

So, this challenge gives us a brief SPIM (ie MIPS) file.  Looking at it reveals that it is a loop over the flag, that XOR's the flag with the loop index (0 based of course ;)).  A quick python script on the garbled string they supplied yields the flag.  Hooray SPIM!
