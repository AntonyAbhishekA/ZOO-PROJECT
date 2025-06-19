from flask import Flask, request, render_template, jsonify, redirect, url_for, session
import psycopg2
import os
import qrcode
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'c6f519b2cfdb44aeadcbb0f5d098e8b8e58d2d7e7e16cfdff933e5f39c5dcb3d' # 🔐 Set a strong secret key for session security


# 🔌 PostgreSQL connection function for Supabase
def get_db_connection():
    return psycopg2.connect(
        host="aws-0-ap-south-1.pooler.supabase.com",
        database="postgres",
        user="postgres.nlkanqqdyuigbczycpuy",
        password="#Njr10wins2026",  # 👈 paste here
        port=5432
    )

# 🏠 Home
@app.route('/')
def home():
    return "<h2>Welcome to the Zoo Project 🦁</h2><p>Scan a QR code or visit /animal?id=AnimalID to view animal details.</p>"

# 🔍 View Animal Info
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
        return render_template('animal.html', animal=animal)
    else:
        return "Animal not found", 404

# 🔐 Admin Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'zoo123':
            session['admin'] = True
            return redirect(url_for('add_animal'))
        else:
            return "❌ Invalid credentials", 401
    return render_template('login.html')

# 🚪 Admin Logout
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

# ➕ Add Animal (Admin Only)
@app.route('/add', methods=['GET', 'POST'])
def add_animal():
    if not session.get('admin'):
        return redirect(url_for('login'))

    os.makedirs("static/qrcodes", exist_ok=True)
    os.makedirs("static/images", exist_ok=True)

    if request.method == 'POST':
        data = {
            "id": request.form['id'],
            "name": request.form['name'],
            "species": request.form['species'],
            "age": request.form['age'],
            "fun_facts": request.form['fun_facts'],
            "emotion": request.form['emotion'],
            "location": request.form['location'],
            "classification_type": request.form['type'],
            "classification_class": request.form['class'],
            "image_filename": request.form.get("image_filename", "")
        }

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM animals WHERE id = %s", (data["id"],))
        if cursor.fetchone():
            conn.close()
            return "❌ Animal ID already exists!", 400

        cursor.execute("""
            INSERT INTO animals (id, name, species, age, fun_facts, emotion, location,
                                 classification_type, classification_class, image_filename)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data["id"], data["name"], data["species"], data["age"], data["fun_facts"],
            data["emotion"], data["location"], data["classification_type"],
            data["classification_class"], data["image_filename"]
        ))

        conn.commit()
        cursor.close()
        conn.close()

        # QR Code
        qr_link = f"https://zoo-project-kiny.onrender.com/animal?id={data['id']}"
        qr_path = f"static/qrcodes/{data['id']}_qr.png"
        qrcode.make(qr_link).save(qr_path)

        return f"✅ Animal '{data['name']}' added!<br><a href='{qr_link}'>View Animal</a><br>QR saved at: {qr_path}"

    return render_template("add_animal.html")

# 📁 Upload Image
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    image = request.files['image']
    if image.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(image.filename)
    image.save(os.path.join('static/images', filename))
    return jsonify({"filename": filename})

# ▶️ Run
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
