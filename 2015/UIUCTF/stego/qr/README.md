# UIUCTF : QR

#### Author: GSAir

**Description**:
> This QR code might not be as quick a response as usual!

- The original image has been randomized using the following scheme

        def get_color(x, y, r):
            n = (pow(x, 7) + pow(y, 8)) ^ r
            return (n ^ ((n >> 8) << 8))

        for x in range(flag_img.size[0]):
            for y in range(flag_img.size[1]):
                s = enpix[x,y]
                a = ()
                if im[x,y][0] < 250:
                    a += (get_color(x, y, r),)
                else:
                    a += (enpix[x,y][0],)
                if im[x,y][1] < 250:
                    a += (get_color(x, y, g),)
                else:
                    a += (enpix[x,y][1],)
                if im[x,y][2] < 250:
                    a += (get_color(x, y, b),)
                else:
                    a += (enpix[x,y][2],)
                enpix[x,y] = a


where `enpix` is a truly random image.

 - We realize that the `get_color` is only using the lower byte of the input `n`,  `(n ^ ((n >> 8) << 8)) <=> n & 0xFF` then it may be "bruteforcable".

        from PIL import Image
        import random

        flag_img = Image.open("enc.png")
        im = flag_img.load()

        def breakc(r, i):
           count = 0
           for x in xrange(flag_img.size[0]):
               for y in xrange(flag_img.size[1]):
                   if (get_color(x, y, r) == im[x, y][i]):
                       count = count + 1
            return count

        lr = [breakc(i, 0) for i in xrange(1, 256)]
        lg = [breakc(i, 1) for i in xrange(1, 256)]
        lb = [breakc(i, 2) for i in xrange(1, 256)]


 - We count how many pixels match the pseudo-random value, checking the arrays `lr, lg, lb` we see that only one value has a high matching rate, seems good :)

        r = lr.index(max(lr)) + 1
        g = lg.index(max(lg)) + 1
        b = lb.index(max(lb)) + 1

 -  So now we can reconstruct the original image. Like we know that the QR is black or white, we assume that if one of the channel match the PRGN value then it was lower than 250 therefore was black!

        for x in xrange(flag_img.size[0]):
            for y in xrange(flag_img.size[1]):
                a = ()
                if im[x,y][0] == get_color(x, y, r) or im[x,y][1] == get_color(x, y, g) or im[x,y][2] == get_color(x, y, b):
                    a = (0,0,0)
                else:
                    a = (255,255,255)
                tmp[x, y] = a

 - Now the image looks like a QR code but there are some black points in the white. We see that the black square are clean and can figure out that the QR code uses a block size of 10 x 10. So we filter each block and if the is any white pixel then fill the block with white:

        for z in xrange(49):
            for t in xrange(49):
                count = 0;
                val = 0
            white = False
            for x in xrange(10 * z, 10 * (z + 1)):
                for y in xrange(10 * t, 10 * (t + 1)):
                    if (tmp[x, y][0] > 0):
                        white = True
                        break
                if white:
                    break
            if (white):
                for x in xrange(10 * z, 10 * (z + 1)):
                    for y in xrange(10 * t, 10 * (t + 1)):
                        tmp[x, y] = (255, 255, 255)

            tmp_img.save('flag.png')

Youpi we have the flag :)

### Flag
flag{565d0e73673562c998b2d915d7cb950123c4aa5170737714ec93288d211d9059baa815c015a2dbff9ef73e0d372d9c9057762c03970394df92f08b2065de86ba}
