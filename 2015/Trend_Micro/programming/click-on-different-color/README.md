# Trend Micro : Click on the Different Color

#### Author: Wh1t3Fox

**Description**:
> We were provided with a website that contained a PNG image of a NxN grid. The task was to select the
square was a different color than the others. The challenge started with 2x2 a grew each level.
>
> I started to do this manually to get a feel for the challenge and soon realized the colors were so close
in color it was nearly impossible to tell with the naked eye so I wrote a script to automate the process.

First the idea was to get the center pixel of each block and find the different color. This worked great
until we got up to level 50 or so when the blocks became so small and each box was roughly 2px X 2px. After
that we decided to get the upper left most pixel in each box instead. We ran the code and after 81 levels we
got the flag.

**Code**

    #!/usr/bin/env python2

    import requests
    from bs4 import BeautifulSoup as bs
    from PIL import Image
    from StringIO import StringIO

    BASE_URL = 'http://ctfquest.trendmicro.co.jp:43210'
    BLOCK_SIZE = 2

    def get_page(x=None, y=None, url=None):
        if not x and not y:
            r = requests.get('{0}/click_on_the_different_color'.format(BASE_URL))
        else:
            r = requests.get("{0}{1}?x={2}&y={3}".format(BASE_URL,url,x,y))
        return r.text

    def get_imgsrc(html):
        soup = bs(html, "lxml")
        img = soup.findAll('img')
        return img[0].get('src')

    def find_first_color(img, size):
        for i in xrange(size):
            if img[i,i] != (255,255,255):
                return i

    def find_wide(img, size, start):
        for i in xrange(start, size):
            if img[i,i] == (255,255,255):
                return i

    def get_coord(img):
        global BLOCK_SIZE
        colors = {}
        r = requests.get('{0}{1}'.format(BASE_URL,img))
        im = Image.open(StringIO(r.content))
        pix = im.load()
        size = im.size[0]
        cx = find_first_color(pix, size)
        dx = find_wide(pix, size, cx + 1)

        for i in xrange(BLOCK_SIZE):
            for j in xrange(BLOCK_SIZE):
                x = i * dx + cx
                y = cx + j * dx
                try:
                    colors[pix[x,y]][1] += 1
                except:
                    colors[pix[x,y]] = [(x,y), 1]

        BLOCK_SIZE += 1
        for v in colors.itervalues():
            if v[1] == 1:
                return v[0]


    def main():
        page_text = get_page()
        while True:
            print page_text
            image_url = get_imgsrc(page_text)
            x, y = get_coord(image_url)
            page_text = get_page(x, y, image_url[4:-4])


    if __name__ == '__main__':
        main()
