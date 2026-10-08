import hashlib, secrets

def new_wallet():
    private_key = secrets.token_hex(32)
    public_key = hashlib.sha256(private_key.encode()).hexdigest()
    address = "vkt1" + hashlib.sha256(public_key.encode()).hexdigest()[:34]
    return {"private":private_key, "public":public_key, "address":address}

if __name__ == "__main__":
    w = new_wallet()
    print(w)
