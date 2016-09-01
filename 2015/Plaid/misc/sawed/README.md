# Plaid : Sawed

#### Author: Wh1t3fox & GSAir

**Description**:
> We are given the string:
>
>	ddddddwwwwwwaaaaaasssssssssssssseddddddddddddddddddewwawwawwawwawwawwawwaedddssssssddddssssssssewwdwwdwwdwwdwwddssdssdssdssdsswwdwwdwwdwwdwwdwwdwwdassassassassassassassedddddddddddddddewwwwwwwwwwwwwwdssdssdssdssdssdssdsswwwwwwwwwwwwwwssssssssssssssedddddddddddewwwwwwwwwwwwweddddddddddessssssssssssssedddddddewwwwwwwwwwwwwweaaaaaaaedssdssdssdssdssdssdssewdwdwdddwddwdwwddwddwddwddewawwawawaaasasassasssasssdsssdsddsddddwdwwdwwwaaaessdddsddsddddsddddewdwdwdwdwdwdwdwawawawawawawaedddddddddddddddeddddddddaaaaaaaasssssssssssssswwwwwwwwdddddeddddddddeddddddwwwwwwaaaaaassssssssssssssedddddddddddddwwesdsddsdddwddwdwwwawwawawaawaawawwdwwdwdddsddsdsedddwwwdddesssssssssesssssess

After looking at it for a while we noticed the only characters are WASDE. We interpreted this as movement on a keyboard just like a game, and used the 'e' character as a newline which gave us the follow:

	ddddddwwwwwwaaaaaassssssssssssss
	dddddddddddddddddd
	wwawwawwawwawwawwawwa
	dddssssssddddssssssss
	wwdwwdwwdwwdwwddssdssdssdssdsswwdwwdwwdwwdwwdwwdwwdassassassassassassass
	ddddddddddddddd
	wwwwwwwwwwwwwwdssdssdssdssdssdssdsswwwwwwwwwwwwwwssssssssssssss
	ddddddddddd
	wwwwwwwwwwwww
	dddddddddd
	ssssssssssssss
	ddddddd
	wwwwwwwwwwwwww
	aaaaaaa
	dssdssdssdssdssdssdss
	wdwdwdddwddwdwwddwddwddwdd
	wawwawawaaasasassasssasssdsssdsddsddddwdwwdwwwaaa
	ssdddsddsddddsdddd
	wdwdwdwdwdwdwdwawawawawawawa
	ddddddddddddddd
	ddddddddaaaaaaaasssssssssssssswwwwwwwwddddd
	dddddddd
	ddddddwwwwwwaaaaaassssssssssssss
	dddddddddddddww
	sdsddsdddwddwdwwwawwawawaawaawawwdwwdwdddsddsds
	dddwwwddd
	sssssssss
	sssss
	ss

After that I created a simple Python script to draw the movements on the screen.

	import turtle

	wn = turtle.Screen()
	t = turtle.Turtle()
	t.color('white')
	t.left(180)
	t.forward(800)
	t.right(180)
	t.color('black')
	t.speed(0)
	distance = 10

	with open('sawed.txt', 'r') as fr:
        for idx, line in enumerate(fr):
            if idx % 2 == 0:
                t.color('black')
            else:
                t.color('white')

            for c in line:
                if c == 'a':
                    t.left(180)
                    t.forward(distance)
                    t.right(180)
                elif c == 's':
                    t.right(90)
                    t.forward(distance)
                    t.left(90)
                elif c == 'd':
                    t.forward(distance)
                elif c == 'w':
                    t.left(90)
                    t.forward(distance)
                    t.right(90)

	raw_input() #keep program open

![PWNING>FPS!](https://i.imgur.com/vezb2LO.gif)

And then we get the flag PWNING>FPS!
