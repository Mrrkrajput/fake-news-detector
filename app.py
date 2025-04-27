from flask import Flask, request, jsonify, render_template
import joblib
from utils import preprocess_text
import newspaper

app = Flask(__name__)

# Load model and vectorizer
model = joblib.load('model/model.pkl')
vectorizer = joblib.load('model/vectorizer.pkl')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    if 'text' in data:
        text = data['text']
    elif 'url' in data:
        try:
            article = newspaper.Article(data['url'])
            article.download()
            article.parse()
            text = article.text
        except Exception:
            return jsonify({'error': 'Failed to fetch article'}), 400
    else:
        return jsonify({'error': 'No text or URL provided'}), 400

    # Preprocess and predict
    processed_text = preprocess_text(text)
    vec_text = vectorizer.transform([processed_text])
    prediction = model.predict(vec_text)[0]
    probability = model.predict_proba(vec_text)[0]

    # Format result (0 = fake, 1 = real)
    result = 'fake' if prediction == 0 else 'real'
    confidence = probability[prediction]

    return jsonify({'result': result, 'confidence': confidence})

if __name__ == '__main__':
    app.run(debug=True)