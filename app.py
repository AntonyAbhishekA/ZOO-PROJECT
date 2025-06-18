from flask import Flask, request, render_template, jsonify
import mysql.connector
import os
import qrcode
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 🔌 MySQL connection function
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        port=3307,                      # ✅ updated from 3306
        user="root",     # Replace with your actual MySQL user
        password="root", # Replace with your password
        database="zoo_db"
    )

# 🏠 Home route
@app.route('/')
def home():
    return "<h2>Welcome to the Zoo Project 🦁</h2><p>Use a QR code or visit <code>/animal?id=AnimalID</code> to view animal details.</p>"

# 🔍 Display animal info from MySQL
@app.route('/animal')
def animal_info():
    animal_id = request.args.get('id')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM animals WHERE id = %s", (animal_id,))
    animal = cursor.fetchone()
    cursor.close()
    conn.close()

    if animal:
        animal["classification"] = {
            "type": animal["classification_type"],
            "class": animal["classification_class"]
        }
        return render_template('animal.html', animal=animal)
    else:
        return "Animal not found", 404

# 🐾 Add a new animal via form
@app.route('/add', methods=['GET', 'POST'])
def add_animal():
    # Ensure folders exist
    os.makedirs("static/qrcodes", exist_ok=True)
    os.makedirs("static/images", exist_ok=True)

    if request.method == 'POST':
        animal_id = request.form['id'].strip()

        # Check if animal exists
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM animals WHERE id = %s", (animal_id,))
        exists = cursor.fetchone()

        if exists:
            cursor.close()
            conn.close()
            return "❌ Animal ID already exists. Please go back and use a unique ID.", 400

        # Insert animal into MySQL
        data = (
            animal_id,
            request.form['name'],
            request.form['species'],
            request.form['age'],
            request.form['fun_facts'],
            request.form['emotion'],
            request.form['location'],
            request.form['type'],
            request.form['class'],
            request.form.get("image_filename", "")
        )

        cursor.execute("""
            INSERT INTO animals (id, name, species, age, fun_facts, emotion, location,
                                 classification_type, classification_class, image_filename)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, data)

        conn.commit()
        cursor.close()
        conn.close()

        # Generate QR code
        qr_link = f"https://zoo-project-kiny.onrender.com/animal?id={animal_id}"
        img = qrcode.make(qr_link)
        qr_path = f"static/qrcodes/{animal_id}_qr.png"
        img.save(qr_path)

        return f"✅ Animal '{request.form['name']}' added!<br><a href='{qr_link}'>View Animal</a><br>QR code saved at: {qr_path}"

    return render_template("add_animal.html")

# 📷 Upload animal image
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

# ▶️ Run the server
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
