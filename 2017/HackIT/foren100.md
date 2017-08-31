This challenge provided me with a .pcap and not much more information. I began by loading it into wireshark and sorting the packets by length to find the ones with the most information. One of these packets held the text “Apple Keyboard.” Looks like we're dealing with a HID keyboard. 
I googled around and found the HID keyboard codes (http://www.freebsddiary.org/APC/usb_hid_usages.php), now the challenge becomes a matter of converting the codes to the proper keys.
```
no_shift = {
    "00": "",
    "01": "",
    "02": "",
    "02": "",
    "03": "",
    "04": "a",
    "05": "b",
    "06": "c",
    "07": "d",
    "08": "e",
    "09": "f",
    "0a": "g",
    "0b": "h",
    "0c": "i",
    "0d": "j",
    "0e": "k",
    "0f": "l",
    "10": "m",
    "11": "n",
    "12": "o",
    "13": "p",
    "14": "q",
    "15": "r",
    "16": "s",
    "17": "t",
    "18": "u",
    "19": "v",
    "1a": "w",
    "1b": "x",
    "1c": "y",
    "1d": "z",
    "1e": "1",
    "1f": "2",
    "20": "3",
    "21": "4",
    "22": "5",
    "23": "6",
    "24": "7",
    "25": "8",
    "26": "9",
    "27": "0",
    "28": "\n",
    "29": "<ESC>",
    "2a": "<DEL>",
    "2b": "<TAB>",
    "2c": " ",
    "2d": "-",
    "2e": "=",
    "2f": "[",
    "30": "]",
    "37": ".",
    "51": "↓",
    "52": "↑"
}
```
I extracted the capture data with tshark: 
```
tshark -r task.pcap -Y "frame.len==35" -T fields -e usb.capdata > data.txt
```
I loaded this file into a simple python script to extract the important values based on their location in the string, and compared them to the HID codes, checking whether the shift modifer was pressed. At first glance, this output was useless. 
```
w
k
f
b
3↑[↑l↑#↑{w$↓b↓ag↓[e↓ci[↑[f↑{k↑n$↑ju}↓↓3↓u↓%=↑↑y↑6↑↓p↓b↓7↓%&↑d↑0↑j↑pt↓i↓a↓[↓k(↑=↑r↑m↑]=↓0↓d↓↓lc↑*↑_↑{↑j%↓u↓s↓(↓*2↑0↑n↑↑9↓h↓4↓]↓y4↑↑k↑↑+p↓f↓e↓$↓!}↑1↑_↑k↑s&↓s↓2↓c↓%q↑$↑.↑!↑#↓s↓0↓c↓z3↑e↑}↑-↑i
```
But when I realized the excess number of arrow key inputs were important, we found the solution.
By keeping track of which line we are on, we can only print the important line, and voila, a flag!
