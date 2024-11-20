from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route('/home.html', methods=['GET'])
def home():
    return app.send_static_file('home.html')

@app.route('/submit', methods=['POST'])
def submit_data():
    data = request.json
    if not data or 'input' not in data:
        return jsonify({'error': 'Invalid request'}), 400

    # Save to database
    user_request = UserRequest(input=data['input'], status='pending')
    db.session.add(user_request)
    db.session.commit()

    orchestrator_response = send_to_orchestrator(data)
    return jsonify(orchestrator_response)

def send_to_orchestrator(data):
    # Simulating orchestrator delegation
    return {'status': 'success', 'message': 'Processed by orchestrator'}

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Route not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

class UserRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    input = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), nullable=False)

@app.before_first_request
def create_tables():
    db.create_all()

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)