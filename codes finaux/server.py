from flask import Flask, render_template_string, request, jsonify, Response
import requests
import json
import queue

app = Flask(__name__)

# IP of Raspberry Pi Pico (for LED control)
PICO_IP = "http://192.168.129.49"

# Quiz questions
questions = [
    {
        "question": "What is the unit of electrical resistance?",
        "options": {"A": "Ohm", "B": "Watt", "C": "Volt", "D": "Ampere"},
        "answer": "A"
    },
    {
        "question": "What does a capacitor store?",
        "options": {"A": "Heat", "B": "Current", "C": "Energy", "D": "Resistance"},
        "answer": "C"
    },
    {
        "question": "Which component restricts the flow of electric current?",
        "options": {"A": "Diode", "B": "Resistor", "C": "Transistor", "D": "Capacitor"},
        "answer": "B"
    },
    {
        "question": "What does LED stand for?",
        "options": {"A": "Low Energy Device", "B": "Light Emission Diode", "C": "Light Emitting Diode", "D": "Linear Electrical Device"},
        "answer": "C"
    },
    {
        "question": "What kind of current flows in one direction only?",
        "options": {"A": "AC", "B": "DC", "C": "PC", "D": "MC"},
        "answer": "B"
    },
    {
        "question": "Which tool is used to measure voltage?",
        "options": {"A": "Thermometer", "B": "Voltmeter", "C": "Ammeter", "D": "Barometer"},
        "answer": "B"
    },
    {
        "question": "Which device can amplify signals?",
        "options": {"A": "Capacitor", "B": "Transistor", "C": "Resistor", "D": "Fuse"},
        "answer": "B"
    },
    {
        "question": "What does a diode do?",
        "options": {"A": "Amplifies signal", "B": "Stores charge", "C": "Converts AC to DC", "D": "Increases resistance"},
        "answer": "C"
    },
    {
        "question": "Which component protects circuits from overcurrent?",
        "options": {"A": "Resistor", "B": "Inductor", "C": "Transistor", "D": "Fuse"},
        "answer": "D"
    },
    {
        "question": "What does AC stand for?",
        "options": {"A": "Active Current", "B": "Amplified Current", "C": "Alternating Current", "D": "Accelerated Charge"},
        "answer": "C"
    },
    {
        "question": "What is the typical voltage of a household battery (AA)?",
        "options": {"A": "1.5V", "B": "5V", "C": "3V", "D": "9V"},
        "answer": "A"
    },
    {
        "question": "Which of these is a passive component?",
        "options": {"A": "Transistor", "B": "Diode", "C": "Resistor", "D": "Op-amp"},
        "answer": "C"
    },
    {
        "question": "Which quantity is measured in Amperes?",
        "options": {"A": "Voltage", "B": "Current", "C": "Resistance", "D": "Power"},
        "answer": "B"
    },
    {
        "question": "Which material is commonly used as a semiconductor?",
        "options": {"A": "Gold", "B": "Copper", "C": "Silicon", "D": "Iron"},
        "answer": "C"
    },
    {
        "question": "What does a breadboard help you do?",
        "options": {"A": "Measure resistance", "B": "Connect circuits without soldering", "C": "Store charge", "D": "Amplify current"},
        "answer": "B"
    }
]

# State
current_question_index = 0
selected_answer = None
score = 0

# SSE clients
clients = []

# HTML page


HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Quiz Bombe</title>
    <style>
        body {
            font-family: monospace;
            background: #181818;
            color: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }
        .quiz-container {
            background: #232323;
            border-radius: 10px;
            padding: 2em;
            width: 500px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.4);
        }
        #question {
            font-size: 1.2em;
            margin-bottom: 1.5em;
            text-align: center;
        }
        #options {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.8em;
        }
        .answer {
            background: #333;
            color: white;
            border: none;
            padding: 1em;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }
        #status {
            font-size: 1.4em;
            color: #fac355;
            margin-bottom: 1em;
            display: block;
            text-align: center;
        }
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            20%, 60% { transform: translateX(-8px); }
            40%, 80% { transform: translateX(8px); }
        }
    #title {
            position: absolute;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 2em;
            margin: 0;
            color: #fac355;
    }
        .hidden { display: none; }
    </style>
    <script>
        async function loadQuestion() {
            const res = await fetch('/question');
            const data = await res.json();
            const qElem = document.getElementById("question");
            const optionsDiv = document.getElementById("options");
            const statusDiv = document.getElementById("status");

            if (data.finished) {
                qElem.textContent = "Quiz Finished! Final Score: " + data.score;
                optionsDiv.innerHTML = "";
                return;
            }

            qElem.textContent = data.question;
            optionsDiv.innerHTML = "";
            for (const [key, value] of Object.entries(data.options)) {
                const p = document.createElement("p");
        p.className = "answer";
                p.textContent = `${key}: ${value}`;
                optionsDiv.appendChild(p);
            }
        }

        const eventSource = new EventSource('/events');
         eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);

    // 1) If server told us the bomb exploded:
    if (data.game_over) {
      // Show “Game Over” screen
      document.getElementById("question").textContent = "💥 BOOM! Game Over!";
      document.getElementById("options").innerHTML = "";
      document.getElementById("status").textContent = "You’ve reached 3 strikes.";
      return;
    }

    // 2) Otherwise fall back to your existing logic:
    const status = `You answered ${data.selected} — ${data.result.toUpperCase()}<br>Score: ${data.score}`;
    document.getElementById("status").innerHTML = status;
    if (data.next || data.finished) {
      loadQuestion();
    }
  };

        window.onload = loadQuestion;
    </script>
</head>
<body>
    <h1 id="title">Live Quiz</h1>
    <div class="quiz-container">
        <p id="question">Loading...</p>
        <div id="options"></div>
        <p id="status"></p>
    </div>

</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/question")
def get_question():
    global current_question_index
    print(f"avzantline223 {current_question_index}")
    print(f"questionsssz {len(questions)}")
    if current_question_index < len(questions)-1:
        q = questions[current_question_index]
        return jsonify({
            "question": q["question"],
            "options": q["options"],
            "index": current_question_index,
            "score": score
        })
    else :
        print('cacamaca')
        return jsonify({"finished": True, "score": score})

@app.route("/submit_answer", methods=["POST"])
def submit_answer():
    global selected_answer, current_question_index, score
    data = request.get_json()
    if "answer" in data:
        selected_answer = data["answer"]
        correct = questions[current_question_index]["answer"]
        result = "correct" if selected_answer == correct else "incorrect"
        if result == "correct":
            score += 1
        if result == "incorrect":
            score -= 1
        print(f"✅ Received: {selected_answer} — {result}")

        # Prepare SSE update
        update_data = {
            "selected": selected_answer,
            "result": result,
            "score": score,
            "next": False,
            "finished": False
        }

        # Move to next question
        if current_question_index + 1 < len(questions):
            current_question_index += 1
            update_data["next"] = True
        else:
            update_data["finished"] = True

        # Push update to all clients
        for q in clients:
            q.put(json.dumps(update_data))

        return jsonify({"status": "ok", **update_data})

    return jsonify({"status": "error", "message": "Missing answer"}), 400

@app.route("/events")
def events():
    def event_stream():
        q = queue.Queue()
        clients.append(q)
        try:
            while True:
                data = q.get()
                yield f"data: {data}\n\n"
        except GeneratorExit:
            clients.remove(q)
    return Response(event_stream(), mimetype='text/event-stream')

@app.route("/led/on", methods=["POST"])
def led_on():
    try:
        requests.get(f"{PICO_IP}/on")
        return "LED turned ON! <a href='/'>Go back</a>"
    except Exception as e:
        return f"Error: {e}"
@app.route("/game_over")
def game_over():
    # push a game_over event to all clients
    update_data = {"game_over": True}
    for q in clients:
        q.put(json.dumps(update_data))
    return jsonify({"status": "ok"})

@app.route("/led/off", methods=["POST"])
def led_off():
    try:
        requests.get(f"{PICO_IP}/off")
        return "LED turned OFF! <a href='/'>Go back</a>"
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
