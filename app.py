from flask import Flask, request, render_template
import json
import os

app = Flask(__name__)

# Load animal data safely, handle if file is missing or invalid
animal_file = 'data/animals.json'
if os.path.exists(animal_file):
    try:
        with open(animal_file) as f:
            animal_data = json.load(f)
    except json.JSONDecodeError:
        animal_data = {}
else:
    animal_data = {}

# Route to display animal info
@app.route('/animal')
def animal_info():
    animal_id = request.args.get('id')
    animal = animal_data.get(animal_id)
    if animal:
        return render_template('animal.html', animal=animal)
    else:
        return "Animal not found", 404

# Only used for local testing (Render uses gunicorn to start app)
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
