import hashlib, time, json

class Block:
    def __init__(self, index, prev_hash, txs):
        self.index = index
        self.prev_hash = prev_hash
        self.txs = txs
        self.timestamp = int(time.time())
        self.nonce = 0
        self.hash = self.calc_hash()
    def calc_hash(self):
        s = f"{self.index}{self.prev_hash}{json.dumps(self.txs)}{self.timestamp}{self.nonce}"
        return hashlib.sha256(s.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = []
        self.max_supply = 21_000_000
        self.supply = 0
        self.create_genesis()
    def create_genesis(self):
        genesis_tx = [{"from":"GENESIS","to":"VKT","amount":1400}]
        g = Block(0, "0"*64, genesis_tx)
        while not g.hash.startswith("0000"):
            g.nonce+=1
            g.hash=g.calc_hash()
        self.chain.append(g)
        self.supply=1400
    def mine(self, miner):
        if self.supply >= self.max_supply: return None
        reward = 50
        tx = [{"from":"REWARD","to":miner,"amount":reward}]
        nb = Block(len(self.chain), self.chain[-1].hash, tx)
        while not nb.hash.startswith("0000"):
            nb.nonce+=1
            nb.hash=nb.calc_hash()
        self.chain.append(nb)
        self.supply+=reward
        return nb
    def is_valid(self):
        for i in range(1,len(self.chain)):
            if self.chain[i].prev_hash!= self.chain[i-1].hash: return False
            if self.chain[i].hash!= self.chain[i].calc_hash(): return False
        return True
