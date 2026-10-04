from flask import Flask, request
from markupsafe import escape
from datetime import datetime, timedelta
from collections import defaultdict
import requests

app = Flask(__name__)

ip_log = defaultdict(list)
blacklist = set()
whitelist = {"127.0.0.1"}

def get_whois_info(ip):
    if ip == "127.0.0.1":
        return "Localhost (Kai, Hassan a Jos)"
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=2).json()
        return f"{r.get('isp','?')} - {r.get('city','')}, {r.get('country','')}"
    except:
        return "Unknown"

CSS = """
<style>
body{background:#0f172a;color:#e2e8f0;font-family:Arial;padding:20px}
.card{background:#1e293b;border-radius:15px;padding:20px;margin:15px 0;box-shadow:0 5px 20px rgba(0,0,0,.5)}
h1{color:#38bdf8;text-align:center}
.badge{padding:5px 12px;border-radius:20px;font-weight:bold}
.red{background:#ef4444}.green{background:#22c55e}.blue{background:#3b82f6}
table{width:100%;border-collapse:collapse}td,th{padding:10px;border-bottom:1px solid #334155}
input{padding:12px;border-radius:8px;border:none;width:70%}
button{padding:12px 20px;border-radius:8px;background:#38bdf8;border:none;font-weight:bold;cursor:pointer}
</style>
"""

@app.route('/')
def dashboard():
    logs = ""
    try:
        with open("karfi_logs.txt","r") as f:
            logs = "<br>".join(f.readlines()[-20:][::-1])
    except:
        logs = "Babu log tukuna"

    return f"""
    {CSS}
    <h1>🛡️ KARFI DEFENDER V6</h1>
    <p style=text-align:center>By Hassan Abubakar | Jos, Nigeria</p>

    <div class=card>
    <h3>📊 Status</h3>
    <p>Whitelist: <span class='badge green'>{len(whitelist)} IPs</span> - {', '.join(whitelist)}</p>
    <p>Blacklist: <span class='badge red'>{len(blacklist)} IPs</span> - {', '.join(blacklist) if blacklist else 'Babu'}</p>
    <p>Rate Limit: 10 requests / min</p>
    </div>

    <div class=card>
    <h3>🔐 Test Login</h3>
    <form method=post action=/login>
    <input name=user placeholder="Saka sunan ka ko OR11 don gwada hari">
    <button>Shiga</button>
    </form>
    </div>

    <div class=card>
    <h3>📜 Littafin 'Yan Sanda (karfi_logs.txt)</h3>
    <div style=background:#0f172a;padding:15px;border-radius:10px;font-family:monospace;font-size:13px>{logs}</div>
    </div>
    """

@app.route('/login', methods=['GET','POST'])
def login():
    ip = request.remote_addr
    now = datetime.now()

    if ip in whitelist and request.method=='POST':
        u=request.form.get('user','')
        return f"{CSS}<div class=card><h2>Sai da safe ADMIN {escape(u)} <span class='badge green'>WHITELISTED</span></h2><p>WHOIS: {get_whois_info(ip)}</p><a href=/><button>Komawa Dashboard</button></a></div>"

    if ip in blacklist:
        return f"{CSS}<div class=card><h2 style=color:#ef4444>⛔ An toshe ka HAR ABADA!</h2><p>IP: {ip}</p><a href=/><button>Dashboard</button></a></div>",403

    ip_log[ip]=[t for t in ip_log[ip] if t>now-timedelta(minutes=1)]
    if len(ip_log[ip])>10:
        blacklist.add(ip)
        with open("karfi_logs.txt","a") as f:
            f.write(f"[{now}] TOSHE: IP {ip} ({get_whois_info(ip)}) - Rate Limit\n")
        return f"{CSS}<div class=card><h2>Rate Limit! Blacklist!</h2></div>",403
    ip_log[ip].append(now)

    if request.method=='POST':
        u=request.form.get('user','')
        if "OR11" in u:
            whois=get_whois_info(ip)
            with open("karfi_logs.txt","a") as f:
                f.write(f"[{now}] HARI: IP {ip} ({whois}) -> {escape(u)}\n")
            blacklist.add(ip)
            return f"{CSS}<div class=card><h2 style=color:#ef4444>🚨 An kama hari!</h2><p>{whois}</p><p>Payload: {escape(u)}</p><a href=/><button>Dashboard</button></a></div>",403
        return f"{CSS}<div class=card><h2>Sai da safe, {escape(u)}</h2><p>{len(ip_log[ip])}/10</p><a href=/><button>Dashboard</button></a></div>"
    return f"{CSS}<div class=card><form method=post><input name=user><button>Shiga</button></form></div>"

if __name__=='__main__':
    app.run(host='127.0.0.1',port=5000,debug=True)

