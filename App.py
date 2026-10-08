from flask import Flask, render_template_string
import time, hashlib, json
app = Flask(__name__)
chain=[]
def mk(data="Genesis BTC 2.0", prev="0"):
 b={"index":len(chain)+1,"time":time.time(),"data":data,"prev":prev,"hash":""}
 b["hash"]=hashlib.sha256(json.dumps({k:b[k] for k in b if k!="hash"},sort_keys=True).encode()).hexdigest()
 return b
chain.append(mk())
HTML="""
<html><head><title>BTC 2.0 - Permanent</title><meta name='viewport' content='width=device-width'>
<style>body{background:#0a0f1e;color:#fff;text-align:center;font-family:sans-serif;padding:15px}
h1{color:#f2a900;font-size:38px}.card{background:#151b2f;padding:15px;margin:12px auto;border-radius:15px;border-left:4px solid #f2a900;max-width:500px;text-align:left}
button{background:linear-gradient(90deg,#f2a900,#ffcc4d);color:#000;padding:14px 30px;border:none;border-radius:25px;font-weight:bold;font-size:16px}
.hash{font-size:8px;color:#667;word-break:break-all;font-family:monospace}</style></head>
<body><h1>₿ BTC 2.0 PERMANENT</h1><p>Blocks: {{c|length}} | Global Mining LIVE | Mangla AJK</p>
<a href='/mine'><button>⛏️ MINE BTC 2.0 BLOCK</button></a>
{% for b in c[::-1] %}<div class=card><b>#{{b.index}} {{b.data}}</b><div class=hash>{{b.hash}}<br>Prev: {{b.prev}}</div></div>{% endfor %}
<p style="color:#0f8;margin-top:20px">● PERMANENT LIVE - Anyone can mine now</p></body></html>
"""
@app.route('/')
def home(): return render_template_string(HTML,c=chain)
@app.route('/mine')
def mine():
 chain.append(mk(f"BTC 2.0 Block {len(chain)+1} Mined",chain[-1]["hash"]))
 return render_template_string(HTML,c=chain)
if __name__ == '__main__': app.run(host='0.0.0.0',port=10000)
