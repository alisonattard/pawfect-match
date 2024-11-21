from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/customer')
def customer():
    return render_template('customer.html')

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)