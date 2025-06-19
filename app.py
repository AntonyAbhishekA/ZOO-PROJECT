from flask import Flask, request, render_template, jsonify
import psycopg2
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 🔌 PostgreSQL connection function for Supabase
def get_db_connection():
    return psycopg2.connect(
        host="aws-0-ap-south-1.pooler.supabase.com",
        database="postgres",
        user="postgres.nlkanqqdyuigbczycpuy",
        password="#Njr10wins2026",  # 👈 paste here
        port=5432
    )

# 🏠 Homepage
@app.route('/')
def home():
    return "<h2>Welcome to the Zoo Project 🦁</h2><p>Use a QR code or visit <code>/animal?id=AnimalID</code> to view animal details.</p>"

# 🔍 Animal info page
@app.route('/animal')
def animal_info():
    animal_id = request.args.get('id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM animals WHERE id = %s", (animal_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row:
        animal = {
            "id": row[0],
            "name": row[1],
            "species": row[2],
            "age": row[3],
            "fun_facts": row[4],
            "emotion": row[5],
            "location": row[6],
            "classification": {
                "type": row[7],
                "class": row[8]
            },
            "image_filename": row[9]
        }
        return render_template("animal.html", animal=animal)
    else:
        return "Animal not found", 404

# ➕ Add new animal (form)
@app.route('/add', methods=['GET', 'POST'])
def add_animal():
    os.makedirs("static/images", exist_ok=True)

    if request.method == 'POST':
        animal_id = request.form['id'].strip()
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM animals WHERE id = %s", (animal_id,))
        exists = cursor.fetchone()

        if exists:
            cursor.close()
            conn.close()
            return "❌ Animal ID already exists. Please go back and use a unique ID.", 400

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
            INSERT INTO animals (
                id, name, species, age, fun_facts, emotion, location,
                classification_type, classification_class, image_filename
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, data)

        conn.commit()
        cursor.close()
        conn.close()

        # ✨ No QR generation here anymore
        animal_link = f"https://zoo-project-kiny.onrender.com/animal?id={animal_id}"
        return f"✅ Animal '{request.form['name']}' added!<br><a href='{animal_link}'>View Animal</a>"

    return render_template("add_animal.html")

# 🖼️ Handle image upload
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

# 🚀 Run
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)