import time

def create_transaction(from_addr, to_addr, amount, balances):
    if not to_addr.startswith("vkt1"):
        return False, "Address vkt1 se start hona chahiye"
    if balances.get(from_addr,0) < amount:
        return False, "Balance kam hai"
    if amount <=0:
        return False, "Amount galat hai"
    
    balances[from_addr] -= amount
    balances[to_addr] = balances.get(to_addr,0) + amount
    
    tx = {
        "from": from_addr,
        "to": to_addr,
        "amount": amount,
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "txid": f"tx_{int(time.time())}"
    }
    return True, tx
