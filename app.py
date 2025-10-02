from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

# Load FAQ knowledge base
with open("faqs.json", "r", encoding="utf-8") as f:
    faqs = json.load(f)

# To track user session handoff state
user_state = {"awaiting_handoff": False}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = (request.json.get("message") or "").strip().lower()

    # If bot previously asked about human handoff
    if user_state.get("awaiting_handoff") and user_msg in ["sure", "okay", "yes", "please"]:
        user_state["awaiting_handoff"] = False
        return jsonify({"response": "Connecting you to a human agent for assistance..."})

    # Human request always triggers Tawk.to
    if "human" in user_msg:
        return jsonify({"response": "Connecting you to a human agent for assistance..."})

    # Exact match for thanks
    if "thank" in user_msg:
        return jsonify({"response": "You're welcome! If you have any more questions, feel free to ask."})

    # Check FAQs using smarter matching
    faq_answer = None
    for key, answer in faqs.items():
        if all(word in user_msg for word in key.lower().split()):
            faq_answer = answer
            break

    if faq_answer:
        return jsonify({"response": faq_answer})

    # Safe fallback
    user_state["awaiting_handoff"] = True
    return jsonify({"response": "I'm not sure about that. Would you like me to connect you to a human agent?"})

if __name__ == "__main__":
    app.run(debug=True)
