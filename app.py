from flask import Flask, request, jsonify, render_template_string
import os
import joblib

app = Flask(__name__)
model = joblib.load("internship_model.pkl")
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>InternSafe AI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #eef3fa;
            margin: 0;
            color: #17243a;
        }

        header {
            background: #102343;
            color: white;
            padding: 22px;
            text-align: center;
        }

        .container {
            max-width: 700px;
            margin: 25px auto;
            padding: 20px;
        }

        .card {
            background: white;
            padding: 22px;
            border-radius: 14px;
            box-shadow: 0 4px 15px #0001;
        }

        label {
            display: block;
            margin-top: 15px;
            font-weight: bold;
        }

        input, textarea, select {
            width: 100%;
            padding: 11px;
            margin-top: 6px;
            box-sizing: border-box;
            border: 1px solid #ccd5e2;
            border-radius: 7px;
            font-size: 15px;
        }

        textarea {
            height: 100px;
        }

        button {
            width: 100%;
            margin-top: 20px;
            padding: 13px;
            border: none;
            border-radius: 8px;
            background: #1768d5;
            color: white;
            font-size: 16px;
            cursor: pointer;
        }

        #result {
            display: none;
            margin-top: 20px;
        }

        .score {
            font-size: 35px;
            font-weight: bold;
        }

        .warning {
            background: #fff0d9;
            padding: 12px;
            margin-top: 10px;
            border-radius: 8px;
        }
    </style>
</head>

<body>
<header>
    <h1>🛡️ InternSafe AI</h1>
    <p>Fake Internship Risk Detector</p>
</header>

<div class="container">
    <div class="card">
        <h2>Check Internship</h2>

        <form id="myForm">
            <label>Company Name *</label>
            <input id="company" required>

            <label>Job Description *</label>
            <textarea id="description" required
                placeholder="Paste internship advertisement"></textarea>

            <label>Company Website</label>
            <input id="website" placeholder="https://example.com">

            <label>Monthly Stipend</label>
            <input id="stipend" placeholder="Example: 15000">

            <label>Contact Information</label>
            <input id="contact">

            <label>Skills and Requirements</label>
            <textarea id="requirements"></textarea>

            <label>Does it ask for payment?</label>
            <select id="payment">
                <option value="no">No / Not mentioned</option>
                <option value="yes">Yes</option>
            </select>

            <button type="submit">Analyze Internship</button>
        </form>
    </div>

    <div class="card" id="result">
        <h2>Analysis Report</h2>
        <p id="companyResult"></p>
        <div class="score" id="score"></div>
        <h3 id="verdict"></h3>
        <p id="mlPrediction"></p>
        <div id="warnings"></div>
        <p id="message"></p>
    </div>
</div>

<script>
document.getElementById("myForm").addEventListener("submit",
async function(event) {
    event.preventDefault();

    const data = {
        company: document.getElementById("company").value,
        description: document.getElementById("description").value,
        website: document.getElementById("website").value,
        stipend: document.getElementById("stipend").value,
        contact: document.getElementById("contact").value,
        requirements: document.getElementById("requirements").value,
        payment: document.getElementById("payment").value
    };

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (!response.ok) {
            alert(result.error);
            return;
        }

        document.getElementById("result").style.display = "block";
        document.getElementById("companyResult").textContent =
            "Company: " + result.company;
        document.getElementById("score").textContent =
            "Risk Score: " + result.risk_score + "%";
        document.getElementById("verdict").textContent =
            result.verdict;

        const warnings = document.getElementById("warnings");
        warnings.replaceChildren();

        result.flags.forEach(function(flag) {
            const item = document.createElement("div");
            item.className = "warning";
            item.textContent = flag.title + ": " + flag.detail;
            warnings.appendChild(item);
        });

        document.getElementById("message").textContent =
            result.message;

       document.getElementById("mlPrediction").textContent =
    "ML Prediction: " + (result.ml_prediction ?? "Not available");

        document.getElementById("result").scrollIntoView({
            behavior: "smooth"
        });

    } catch (error) {
        alert("Server सुरू आहे का ते तपासा.");
    }
});
</script>
</body>
</html>
"""

@app.get("/")
def home():
    return render_template_string(HTML)


@app.post("/analyze")
def analyze():
    data = request.get_json(silent=True) or {}

    company = str(data.get("company", "")).strip()
    description = str(data.get("description", "")).strip()

    if not company or not description:
        return jsonify({
            "error": "Company name and job description required."
        }), 400

    text = description.lower()
    ml_prediction = model.predict([description])[0]
    print("ML Prediction:", ml_prediction)
    ml_label = "Suspicious" if int(ml_prediction) == 1 else "Less Suspicious"
    score = 0
    flags = []

    suspicious = [
        "registration fee"
        "security deposit",
        "guaranteed selection",
        "no interview",
        "pay now",
        "send otp",
        "bank details",
        "training fee"
    ]

    found = [phrase for phrase in suspicious if phrase in text]

    if found:
        score += min(40, len(found) * 15)
        flags.append({
            "title": "Suspicious phrases",
            "detail": ", ".join(found)
        })

    if data.get("payment") == "yes":
        score += 40
        flags.append({
            "title": "Payment requested",
            "detail": "Verify the company before paying."
        })

    website = str(data.get("website", "")).strip()
    if not website.startswith(("http://", "https://")):
        score += 10
        flags.append({
            "title": "Website not provided or invalid",
            "detail": "Verify the employer independently."
        })

    contact = str(data.get("contact", "")).strip()
    if not contact:
        score += 10
        flags.append({
            "title": "Contact missing",
            "detail": "Official contact details were not supplied."
        })

    score = min(score, 100)

    if score >= 70:
        verdict = "High Risk"
    elif score >= 40:
        verdict = "Medium Risk"
    else:
        verdict = "Lower Risk"

    if not flags:
        flags.append({
            "title": "No listed warning signs",
            "detail": "This does not prove the internship is genuine."
        })

    return jsonify({
        "company": company,
        "ml_prediction": ml_label,
        "risk_score": score,
        "verdict": verdict,
        "flags": flags,
        "message": (
            "ML prediction and rule-based risk assessment."
            "Check the company independently."
        )
    })


if __name__ == "__main__":
    app.run(debug=False, port=5000)