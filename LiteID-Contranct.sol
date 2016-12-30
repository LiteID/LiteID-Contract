// Targeting the 0.4.x mainline
pragma solidity ^0.4.0;

contract ID {
	// Owner of this Identity
	address owner;

	// Arrays to store Hash entry information
	bytes32[] HashArray;
	bytes32[] SaltArray;
	uint256[] TimeStampArray;

	// Add Hash (only the owner can add hashes)
	function addHash(bytes32 Hash, bytes32 Salt){
		if (msg.sender == owner){
		    HashArray.push(Hash);
		    SaltArray.push(Salt);
		    TimeStampArray.push(now);
		} else { throw; }
	}

	// This function can only be called offline
	// The EVM does not allow CALL to be used with variably-sized return values
	// (https://github.com/ethereum/wiki/wiki/Solidity-Features)
	function dumpSaltedHashArray() returns (bytes32[] Hashes, bytes32[] Salts, uint256[] Timestamps){
	    Hashes = HashArray;
	    Salts = SaltArray;
	    Timestamps = TimeStampArray;
	}

	// Initilazation
	function ID(bytes32 Hash, bytes32 Salt){
		owner = msg.sender;
		addHash(Hash, Salt);
	}
}