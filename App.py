import streamlit as st
import hashlib
import time
import json
import os
import secrets

# ===== REAL BITCOIN PROTOCOL =====
MAX_SUPPLY = 21000000
INITIAL_REWARD = 50
HALVING_BLOCKS = 21
GENESIS_TIME = "03/Jan/2009 Chancellor on brink of second bailout"

DB_FILE = "bitcoin_chain.json"

def sha256(s):
    return hashlib.sha256(s.encode()).hexdigest()

def double_sha256(s):
    return hashlib.sha256(hashlib.sha256(s.encode()).digest()).hexdigest()

def merkle_root(txs):
    if not txs: return sha256("no-tx")
    hashes = [sha256(json.dumps(tx)) for tx in txs]
    while len(hashes) > 1:
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])
        new_hashes = []
        for i in range(0, len(hashes), 2):
           
