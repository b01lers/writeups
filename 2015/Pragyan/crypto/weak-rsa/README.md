# Pragyan : Weak RSA

#### Author: GSAir

**Description**:
> The name of the challenge was Weak RSA. We get one public certificate and an encrypted message.

* Get the modulus
```bash
openssl req -noout -modulus -in rsa/domain.csr
Modulus=E8953849F11E932E9127AF35E1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000051F8EB7D0556E09FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFBAD55
```
* "Weak" implies that it should be easy to factorize it and obtain the private key. I used the website http://www.alpertron.com.ar/ECM.HTM for factorisation and https://github.com/ius/rsatool/blob/master/rsatool.py for creating the private key.
```
python rsatool.py -p 12779877140635552275193974526927174906313992988726945426212616053383820179306398832891367199026816638983953765799977121840616466620283861630627224899026453 -q 12779877140635552275193974526927174906313992988726945426212616053383820179306398832891367199026816638983953765799977121840616466620283861630627224899027521 -o private.pem -v
```
It creates a file private.pem which is used by openssl for decryption.


We can verify that the certificate and the private key match:

```
openssl x509 -noout -modulus -in certificate.crt | openssl md5
openssl rsa -noout -modulus -in privateKey.key | openssl md5
openssl req -noout -modulus -in CSR.csr | openssl md5
```
It is only checking that the modulus is identical.
```
openssl rsa -noout -modulus -in private.pem | openssl md5
(stdin)= fbd011dd90acac675c33d00f6d9ca00f
openssl req -noout -modulus -in rsa/domain.csr | openssl md5
(stdin)= fbd011dd90acac675c33d00f6d9ca00f
```
* OK so now we have the private key, we just have to decipher the message. It is first base64 encoded, we can use:
```
base64 -d rsa/cipher.enc > cipher.bin
```
* Unfortunately, the cipher text is longer than the modulus...
But when I open cipher.bin with a text editor I noticed that all characters were printable and were decimal digits!! I had to convert the decimal value into its binary form. And... :
```
openssl rsautl -in flag.bin -inkey private.pem -decrypt -raw
Congrats! The flag is too_close_primes
```
