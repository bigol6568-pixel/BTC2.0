from flask import Flask, jsonify
from blockchain import Blockchain

app = Flask(__name__)
chain = Blockchain()

@app.route('/chain')
def get_chain():
    return jsonify({"length":len(chain.chain), "chain":[b.__dict__ for b in chain.chain]})

@app.route('/mine/<miner>')
def mine(miner):
    block = chain.mine(miner)
    return jsonify(block.__dict__ if block else {"error":"Supply full"})

if __name__ == '__main__':
    app.run(port=5000)
