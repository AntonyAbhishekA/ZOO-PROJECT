from flask import Flask, request, render_template, jsonify
import json
import os
import qrcode
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Load animal data (fixing path case sensitivity for deployment)
def load_animal_data():
    if os.path.exists('data/animals.json'):
        with open('data/animals.json') as f:
            return json.load(f)
    return {}

# Route to homepage
@app.route('/')
def home():
    return "<h2>Welcome to the Zoo Project 🦁</h2><p>Use a QR code or visit <code>/animal?id=AnimalID</code> to view animal details.</p>"

# Route to display animal info
@app.route('/animal')
def animal_info():
    animal_id = request.args.get('id')
    animal_data = load_animal_data()
    animal = animal_data.get(animal_id)
    if animal:
        return render_template('animal.html', animal=animal)
    else:
        return "Animal not found", 404

# Route to add animal
@app.route('/add', methods=['GET', 'POST'])
def add_animal():
    animals = load_animal_data()
    animal_file = "data/animals.json"

    # Ensure folders exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("static/qrcodes", exist_ok=True)
    os.makedirs("static/images", exist_ok=True)

    if request.method == 'POST':
        animal_id = request.form['id'].strip()
        if animal_id in animals:
            return "❌ Animal ID already exists. Please go back and use a unique ID.", 400

        animal_data = {
            "id": animal_id,
            "name": request.form['name'],
            "species": request.form['species'],
            "age": request.form['age'],
            "fun_facts": request.form['fun_facts'],
            "emotion": request.form['emotion'],
            "location": request.form['location'],
            "image_filename": request.form.get("image_filename", ""),
            "classification": {
                "type": request.form['type'],
                "class": request.form['class']
            }
        }

        animals[animal_id] = animal_data

        # Save to JSON
        with open(animal_file, "w") as f:
            json.dump(animals, f, indent=4)

        # Create QR Code using live site URL
        qr_link = f"https://zoo-project-kiny.onrender.com/animal?id={animal_id}"
        img = qrcode.make(qr_link)
        qr_path = f"static/qrcodes/{animal_id}_qr.png"
        img.save(qr_path)

        return f"✅ Animal '{animal_data['name']}' added!<br><a href='{qr_link}'>View Animal</a><br>QR code saved at: {qr_path}"

    return render_template("add_animal.html")

# Route to handle image uploads
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    image = request.files['image']
    if image.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(image.filename)
    image_path = os.path.join('static/images', filename)
    image.save(image_path)

    return jsonify({"filename": filename})

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
