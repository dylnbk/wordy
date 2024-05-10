from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/daily_challenge', methods=['GET'])
def daily_challenge():
    daily_words = ["Bliss", "Dance", "Garden", "Journey", "Melody"]
    return jsonify({"daily_words": daily_words})

if __name__ == '__main__':
    app.run(debug=True)