from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/customer')
def customer():
    return render_template('customer.html')




# # Run the application
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)




# new code these 3 if not owrk remove and uncomment following 2
import os
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "pets.db")}'


# # database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pets.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pet_type = db.Column(db.String(50), nullable=False)
    age = db.Column(db.String(50), nullable=False)
    characteristics = db.Column(db.PickleType, nullable=False)  # Save as a list

# Initialize the database
with app.app_context():
    db.create_all()  # This will create the 'pets.db' file and tables

# Your routes and application logic
@app.route("/save_pet", methods=["POST"])
def save_pet():
    data = request.get_json()  # Get data from the form
    pet_type = data["selectedPet"]
    age = data["ageSelect"]
    characteristics = data["characteristics"]

    new_pet = Pet(pet_type=pet_type, age=age, characteristics=characteristics)
    
    db.session.add(new_pet)
    db.session.commit()

    return jsonify({"message": "Pet data saved!"}), 200


@app.route("/get_pet_for_model/<int:pet_id>", methods=["GET"])
def get_pet_for_model(pet_id):
    pet = Pet.query.get(pet_id)
    
    if not pet:
        return jsonify({"error": "Pet not found"}), 404
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)