from flask import Flask, request, render_template
import json
import os

app = Flask(__name__)

# Load animal data
if os.path.exists('data/animals.json'):
    with open('data/animals.json') as f:
        animal_data = json.load(f)
else:
    animal_data = {}

# Route to homepage
@app.route('/')
def home():
    return "<h2>Welcome to the Zoo Project 🦁</h2><p>Use a QR code or visit <code>/animal?id=AnimalID</code> to view animal details.</p>"

# Route to display animal info
@app.route('/animal')
def animal_info():
    animal_id = request.args.get('id')
    animal = animal_data.get(animal_id)
    if animal:
        return render_template('animal.html', animal=animal)
    else:
        return "Animal not found", 404

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
