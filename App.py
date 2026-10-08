import hashlib, secrets, json

def create_new_wallet():
    private = secrets.token_hex(32)
    public = hashlib.sha256(private.encode()).hexdigest()
    address = "vkt1" + hashlib.sha256(public.encode()).hexdigest()[:34]
    wallet = {
        "address": address,
        "private_key": private,
        "public_key": public,
        "balance": 1400
    }
    return wallet

def export_wallet_json(wallet):
    return json.dumps(wallet, indent=2)

def import_wallet_from_json(json_text):
    try:
        w = json.loads(json_text)
        if "address" in w and "private_key" in w:
            return w
    except:
        return None
    return None

def get_short(addr):
    return addr[:10] + "..." + addr[-6:]
