# blockchain.py - 100% REAL BTC LIKE BLOCKCHAIN - 0 SCAM
import hashlib, time, json

class Block:
    def __init__(self, index, prev_hash, transactions, nonce=0):
        self.index = index
        self.prev_hash = prev_hash
        self.transactions = transactions # [{"from":"miner","to":"addr","amount":50}]
        self.timestamp = int(time.time())
        self.nonce = nonce
        self.hash = self.calc_hash()

    def calc_hash(self):
        data = f"{self.index}{self.prev_hash}{json.dumps(self.transactions)}{self.timestamp}{self.nonce}"
        return hashlib.sha256(data.encode()).hexdigest()

class RealBlockchain:
    def __init__(self):
        self.chain = []
        self.supply = 0
        self.max_supply = 21_000_000
        self.create_genesis()

    def create_genesis(self):
        # BTC jaisa genesis - 1400 BTC aapka pehla reward
        genesis_tx = [{"from": "GENESIS", "to": "VKT_FOUNDER", "amount": 1400, "msg": "VKT BTC 2.0 Genesis - 0 Scam"}]
        genesis = Block(0, "0"*64, genesis_tx)
        # PoW - Hash 0000 se start hona chahiye
        while not genesis.hash.startswith("0000"):
            genesis.nonce += 1
            genesis.hash = genesis.calc_hash()
        self.chain.append(genesis)
        self.supply = 1400
        print(f"GENESIS MINED: {genesis.hash}")

    def mine_block(self, miner_address):
        if self.supply >= self.max_supply:
            return "Supply khatam - 21M ho gaye"

        reward = 50 # BTC jaisa halving baad me add karenge
        if self.supply + reward > self.max_supply:
            reward = self.max_supply - self.supply

        tx = [{"from": "REWARD", "to": miner_address, "amount": reward}]
        prev_hash = self.chain[-1].hash
        new_block = Block(len(self.chain), prev_hash, tx)

        # REAL MINING - PoW
        print(f"Mining Block #{new_block.index}...")
        while not new_block.hash.startswith("0000"):
            new_block.nonce += 1
            new_block.hash = new_block.calc_hash()

        self.chain.append(new_block)
        self.supply += reward
        return new_block

    def is_valid(self):
        # Koi bhi verify kar sakta hai - 0 SCAM ka saboot
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i-1]
            if curr.prev_hash!= prev.hash: return False
            if curr.hash!= curr.calc_hash(): return False
            if not curr.hash.startswith("0000"): return False
        return True

# TEST - REAL RUN
btc2 = RealBlockchain()
block1 = btc2.mine_block("bc1q_YOUR_ADDRESS")
print(f"Block Mined: {block1.hash} Nonce: {block1.nonce}")
print(f"Valid? {btc2.is_valid()} Supply: {btc2.supply}/21M")
