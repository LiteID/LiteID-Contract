from ethjsonrpc import EthJsonRpc
import hashlib
import random
import time
import json

class LiteIDContract:
	def __init__(self, ip='127.0.0.1', port=8545, contract_id=None):
		self.connection = EthJsonRpc(ip, port)
		self.contract_id = contract_id
		self.abi_def = [
							{
								"constant": False,
								"inputs": [],
								"name": "dumpSaltedHashArray",
								"outputs": [
									{
										"name": "Hashes",
										"type": "bytes32[]"
									},
									{
										"name": "Salts",
										"type": "bytes32[]"
									},
									{
										"name": "Timestamps",
										"type": "uint256[]"
									}
								],
								"payable": False,
								"type": "function"
							},
							{
								"constant": False,
								"inputs": [
									{
										"name": "Hash",
										"type": "bytes32"
									},
									{
										"name": "Salt",
										"type": "bytes32"
									}
								],
								"name": "addHash",
								"outputs": [],
								"payable": False,
								"type": "function"
							},
							{
								"inputs": [
									{
										"name": "Hash",
										"type": "bytes32"
									},
									{
										"name": "Salt",
										"type": "bytes32"
									}
								],
								"payable": False,
								"type": "constructor"
							}
						]

	def _caculate_hash(self, data):
		salt = bytearray(random.getrandbits(8) for i in range(32))
		origanal_hash = hashlib.sha256(data)
		salted_hash = hashlib.sha256(origanal_hash.digest() + salt)
		salt = (''.join('{:02x}'.format(x) for x in salt)).decode("hex")
		origanal_hash = origanal_hash.hexdigest().decode("hex")
		salted_hash = salted_hash.hexdigest().decode("hex")
		return salted_hash, salt, origanal_hash

	def unlockAccount(self, account, password):
		self.connection._call('personal_unlockAccount',params=[account, password, 36000])

	def addHash(self, data):
		if self.contract_id is None:
			raise IOError
		salted_hash, salt, origanal_hash = self._caculate_hash(data)
		tx = self.connection.call_with_transaction(self.connection.eth_coinbase(),
												self.contract_id,
												'addHash(bytes32,bytes32)',
												[salted_hash, salt])
		print "Waiting for addHash to be mined"
		while self.connection.eth_getTransactionReceipt(tx) is None:
			time.sleep(1)
		return origanal_hash

	def create_contranct(self, data):
		if not hasattr(self,'byte_code'):
			file = open('LiteID-Contranct.sol')
			code_data = self.connection.eth_compileSolidity(file.read())
			self.byte_code = code_data['ID']['code']
			self.abi_def = code_data['ID']['info']['abiDefinition']
		salted_hash, salt, origanal_hash = self._caculate_hash(data)
		tx_id = self.connection.create_contract(self.connection.eth_coinbase(),
												self.byte_code, 300000,
												sig='addHash(bytes32,bytes32)',
												args=[salted_hash, salt])
		print "Waiting for contranct to be mined"
		while self.connection.eth_getTransactionReceipt(tx_id) is None:
			time.sleep(1)
		self.contract_id = self.connection.eth_getTransactionReceipt(tx_id)['contractAddress']
		return self.contract_id

	def dump_hashes(self):
		return_types = list()
		for item in self.abi_def:
			try:
				if item['name'] == 'dumpSaltedHashArray':
					for i in item['outputs']:
						return_types.append(i['type'])
			except KeyError:
				pass
		return_types = ['bytes32[]', 'bytes32[]', 'uint256[]']
		return self.connection.call(self.contract_id, 'dumpSaltedHashArray()', [], return_types)

if __name__ == "__main__":
	a = LiteIDContract(contract_id=u'0xB2a045bb7D0eb64BD044763ae572077E5182247B')
	a.unlockAccount("0x2fe84be2806ecef45adef9699d5a6f1939d0a377", "mypassword")
	#a.create_contranct("lol")

	a.addHash("hi")

	c = EthJsonRpc('127.0.0.1', 8545)

	tx = c.call_with_transaction(c.eth_coinbase(), a.contract_id, 'addHash(bytes32,bytes32)', ['79d3b5b20c84c399e403048359def1398b729ac9a2d88485972be2e691af46de'.decode("hex"),'5e408dafb1164edde8e95527f9a4bd2abb3bd55fb4e32f8f5ea806a683fccbd6'.decode("hex")])

	while c.eth_getTransactionReceipt(tx) is None:
				pass

	print "Contranct id: {}".format(a.contract_id)

	for item in a.dump_hashes():
		print item





# Salted Hash: 0x62335b41ea49e29b99bd8767324dc4b5e3453a77c74883078ebcafc7589f0605
# Salt: 0xecf438e57277a4191c1875ccc9fedefb4b5feb9b62a4f38de457392a30814822
# 0x64ec88ca00b268e5ba1a35678a1b5316d212f4f366b2477232534a8aeca37f3c
