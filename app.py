from flask import Flask, render_template
import firebase_admin
from firebase_admin import credentials, firestore

# Path to your downloaded Service Account Key JSON file
cred = credentials.Certificate("firebase-key.json")  # Replace with the actual file name if different
firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

app = Flask(__name__)

# Example route to test Firebase connection
@app.route('/test_firebase')
def test_firebase():
    try:
        # Add a document to Firestore
        doc_ref = db.collection('testCollection').document('testDoc')
        doc_ref.set({'message': 'Hello, Firebase!'})
        return "Firebase connection successful!"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/customer')
def customer():
    return render_template('customer.html')

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
