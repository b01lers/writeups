# RCTF : Analyze Nginx's log

#### Author: Wh1t3Fox

**Description**:
> We were given the following [nginx log](https://bpaste.net/show/d7c952a1d36a) and told to parse the file.

Looking at the log file, I could see there was a blind SQL Injection attack, and I needed to use this in order to find the solution. Searching for flag returned some queries to misc.flag and using these queries I was able to convert the values to characters and get the flag.


**Code**

    import urllib,sys

    with open('log') as fr:
        for line in fr:
            if line.find('misc.flag') != -1:
                info =  urllib.unquote_plus(line[line.find('"')+4:line.find('HTTP')])[136:-17]
                try:
                    sys.stdout.write(chr(int(info[info.find('=')+1:])))
                except:
                    pass

ROIS{miSc_An@lySis_nG1nx_L0g}
