from flask import Flask, request, render_template
import json

app = Flask(__name__)

# Load animal data
with open('data/animals.json') as f:
    animal_data = json.load(f)

# Route to display animal info
@app.route('/animal')
def animal_info():
    animal_id = request.args.get('id')
    animal = animal_data.get(animal_id)
    if animal:
        return render_template('animal.html', animal=animal)
    else:
        return "Animal not found", 404

# Start the server and allow connections from other devices
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
