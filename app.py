from flask import Flask, request, jsonify, render_template
import joblib
from utils import preprocess_text
import newspaper
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Load model and vectorizer
model = joblib.load('model/model.pkl')
vectorizer = joblib.load('model/vectorizer.pkl')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        data = request.json
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')

        if not all([name, email, message]):
            return jsonify({'success': False, 'message': 'All fields are required.'}), 400

        # Email configuration
        sender_email = os.getenv('EMAIL_ADDRESS')
        sender_password = os.getenv('EMAIL_PASSWORD')
        recipient_email = 'rkrajputrks@gmail.com'

        # Compose email
        email_body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
        msg = MIMEText(email_body)
        msg['Subject'] = 'New Contact Form Submission - Fake News Detector'
        msg['From'] = sender_email
        msg['To'] = recipient_email

        try:
            # Send email via Gmail SMTP
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient_email, msg.as_string())
            return jsonify({'success': True, 'message': 'Message sent successfully!'})
        except Exception as e:
            return jsonify({'success': False, 'message': 'Failed to send message. Please try again later.'}), 500

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
