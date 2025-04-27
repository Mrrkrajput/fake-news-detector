document.addEventListener('DOMContentLoaded', function() {
    // Toggle between text and URL input
    const inputType = document.getElementById('input-type');
    const textInput = document.getElementById('input-text');
    const urlInput = document.getElementById('input-url');

    inputType.addEventListener('change', function() {
        if (this.value === 'text') {
            textInput.style.display = 'block';
            urlInput.style.display = 'none';
        } else {
            textInput.style.display = 'none';
            urlInput.style.display = 'block';
        }
    });

    // Handle form submission
    document.getElementById('predict-form').addEventListener('submit', function(event) {
        event.preventDefault();
        const type = inputType.value;
        const input = type === 'text' ? textInput.value.trim() : urlInput.value.trim();
        
        if (!input) {
            alert('Please enter text or a URL.');
            return;
        }

        document.getElementById('loading').style.display = 'block';
        document.getElementById('result').style.display = 'none';
        document.getElementById('feedback-btn').style.display = 'none';

        const data = type === 'text' ? { text: input } : { url: input };

        fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('loading').style.display = 'none';
            if (data.error) {
                document.getElementById('result-text').innerText = 'Error: ' + data.error;
            } else {
                document.getElementById('result-text').innerText = `The news is ${data.result.toUpperCase()}`;
                document.getElementById('confidence').innerText = `Confidence: ${(data.confidence * 100).toFixed(2)}%`;
                document.getElementById('feedback-btn').style.display = 'block';
            }
            document.getElementById('result').style.display = 'block';
        })
        .catch(error => {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('result-text').innerText = 'Error: Unable to analyze. Please try again.';
            document.getElementById('result').style.display = 'block';
            console.error('Error:', error);
        });
    });

    // Feedback modal
    document.getElementById('feedback-btn').addEventListener('click', function() {
        document.getElementById('feedback-modal').style.display = 'flex';
    });

    document.querySelector('.close').addEventListener('click', function() {
        document.getElementById('feedback-modal').style.display = 'none';
    });

    document.getElementById('submit-feedback').addEventListener('click', function() {
        const feedback = document.getElementById('feedback-text').value.trim();
        if (feedback) {
            alert('Thank you for your feedback!');
            document.getElementById('feedback-modal').style.display = 'none';
            document.getElementById('feedback-text').value = '';
        } else {
            alert('Please enter some feedback.');
        }
    });
});
