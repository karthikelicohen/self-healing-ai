from flask import Flask, jsonify, render_template_string
import threading
import time
import random

app = Flask(__name__)

logs = []
attack_count = 0
normal_count = 0
attack_history = []
normal_history = []

def simulate():
    global attack_count, normal_count

    while True:
        fake_ip = f"192.168.{random.randint(0,255)}.{random.randint(1,255)}"

        prediction = random.random()  # simulate AI

        if prediction > 0.7:
            attack_count += 1
            logs.append({"msg": f"⚠️ Attack detected from {fake_ip}", "type": "attack"})
        else:
            normal_count += 1
            logs.append({"msg": f"Normal traffic from {fake_ip}", "type": "normal"})

        attack_history.append(attack_count)
        normal_history.append(normal_count)

        if len(logs) > 20:
            logs.pop(0)

        if len(attack_history) > 20:
            attack_history.pop(0)
            normal_history.pop(0)

        time.sleep(1)

@app.route("/data")
def data():
    return jsonify({
        "attack": attack_count,
        "normal": normal_count,
        "logs": logs,
        "attack_history": attack_history,
        "normal_history": normal_history
    })

@app.route("/")
def home():
    return render_template_string("""
    <html>
    <head>
    <title>☁️ Cloud AI Security</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
    body { background:#0f172a; color:white; text-align:center; font-family:Arial; }
    .card { background:#1e293b; padding:20px; margin:10px; border-radius:10px; display:inline-block; }
    </style>
    </head>
    <body>

    <h1>☁️ Cloud AI Security Dashboard</h1>

    <div class="card">⚠️ Attacks: <span id="attack">0</span></div>
    <div class="card">✅ Normal: <span id="normal">0</span></div>

    <canvas id="chart"></canvas>

    <h2>Logs</h2>
    <div id="logs"></div>

    <script>
    let chart = new Chart(document.getElementById('chart'), {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {label:'Attack', data:[]},
                {label:'Normal', data:[]}
            ]
        }
    });

    function update(){
        fetch('/data')
        .then(res=>res.json())
        .then(d=>{
            document.getElementById("attack").innerText=d.attack;
            document.getElementById("normal").innerText=d.normal;

            chart.data.labels = d.attack_history.map((_,i)=>i);
            chart.data.datasets[0].data = d.attack_history;
            chart.data.datasets[1].data = d.normal_history;
            chart.update();

            let html="";
            d.logs.forEach(l=>{
                html += "<div>"+l.msg+"</div>";
            });
            document.getElementById("logs").innerHTML=html;
        });
    }

    setInterval(update,1000);
    </script>

    </body>
    </html>
    """)

if __name__ == "__main__":
    threading.Thread(target=simulate, daemon=True).start()
    app.run()
