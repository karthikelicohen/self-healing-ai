from flask import Flask, jsonify, render_template_string
import threading
import time
import random
import numpy as np
import tensorflow as tf
import pickle

app = Flask(__name__)

model = tf.keras.models.load_model("intrusion_model_v3.h5")

with open("scaler_v3.pkl", "rb") as f:
    scaler = pickle.load(f)

logs = []
attack_count = 0
normal_count = 0

def simulate():
    global attack_count, normal_count

    while True:
        fake_ip = f"8.8.8.{random.randint(1,255)}"

        data = np.random.rand(1, scaler.mean_.shape[0])
        prediction = model.predict(data, verbose=0)

        if prediction[0][0] > 0.8:
            attack_count += 1
            logs.append({"msg": f"⚠️ {fake_ip}", "type": "attack"})
        else:
            normal_count += 1
            logs.append({"msg": f"Normal {fake_ip}", "type": "normal"})

        if len(logs) > 20:
            logs.pop(0)

        time.sleep(1)

@app.route("/data")
def data():
    return jsonify({
        "attack": attack_count,
        "normal": normal_count,
        "logs": logs
    })

@app.route("/")
def home():
    return render_template_string("""
    <h1>☁️ Cloud AI Security Dashboard</h1>
    <h2>Attacks: <span id="a">0</span></h2>
    <h2>Normal: <span id="n">0</span></h2>
    <div id="logs"></div>

    <script>
    setInterval(()=>{
        fetch('/data')
        .then(res=>res.json())
        .then(d=>{
            document.getElementById("a").innerText=d.attack;
            document.getElementById("n").innerText=d.normal;

            let html="";
            d.logs.forEach(l=>{
                html += "<div>"+l.msg+"</div>";
            });
            document.getElementById("logs").innerHTML=html;
        })
    },1000)
    </script>
    """)

if __name__ == "__main__":
    threading.Thread(target=simulate, daemon=True).start()
    app.run()