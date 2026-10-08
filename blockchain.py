import hashlib, time, json

class Blockchain:
    def __init__(self):
        self.chain = []
        self.max_supply = 21_000_000
        self.mined = 0
        self.create_genesis()

    def create_genesis(self):
        block = {
            "index": 0,
            "hash": "0"*64,
            "prev_hash": "0"*64,
            "nonce": 0,
            "txs": [{"from":"GENESIS","to":"GENESIS","amount":1400}],
            "time": time.strftime("%H:%M:%S")
        }
        # PoW 0000
        while not block["hash"].startswith("0000"):
            block["nonce"]+=1
            txt = f"{block['index']}{block['prev_hash']}{block['nonce']}"
            block["hash"] = hashlib.sha256(txt.encode()).hexdigest()
        self.chain.append(block)
        self.mined = 1400

    def mine(self, miner_addr):
        if self.mined >= self.max_supply:
            return None
        prev = self.chain[-1]["hash"]
        index = len(self.chain)
        nonce = 0
        while True:
            txt = f"{index}{prev}{miner_addr}{nonce}{time.time()}"
            h = hashlib.sha256(txt.encode()).hexdigest()
            if h.startswith("0000"):
                block = {
                    "index": index,
                    "hash": h,
                    "prev_hash": prev,
                    "nonce": nonce,
                    "txs": [{"from":"REWARD","to":miner_addr,"amount":50}],
                    "time": time.strftime("%H:%M:%S")
                }
                self.chain.append(block)
                self.mined+=50
                return block
            nonce+=1
