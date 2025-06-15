import json
import os
import qrcode
import socket

# Step 1: Make sure folders exist
os.makedirs("data", exist_ok=True)
os.makedirs("static/qrcodes", exist_ok=True)

# Step 2: Load existing animal data or start fresh
animal_file = "data/animals.json"
if os.path.exists(animal_file):
    with open(animal_file, "r") as f:
        try:
            animals = json.load(f)
        except json.JSONDecodeError:
            animals = {}
else:
    animals = {}

# Step 3: Get animal details from user
animal_id = input("Enter a unique animal ID (e.g., lion01): ").strip()
if animal_id in animals:
    print(f"❌ Error: Animal ID '{animal_id}' already exists!")
    exit()

name = input("Enter animal name (e.g., African Lion): ").strip()
species = input("Enter species (e.g., Panthera leo): ").strip()
fun_facts = input("Enter fun facts: ").strip()
emotion = input("Current emotion (e.g., Happy, Sad, Hungry): ").strip()
location = input("Location inside enclosure: ").strip()

# Step 4: Ask for classification using choices
classification = {}

print("\nIs the animal a:")
print("1. Vertebrate")
print("2. Invertebrate")
main_choice = input("Enter choice (1 or 2): ").strip()

if main_choice == "1":
    classification["type"] = "vertebrate"
    print("\nVertebrate is:")
    print("1. Warm-blooded")
    print("2. Cold-blooded")
    blood_choice = input("Enter choice (1 or 2): ").strip()
    if blood_choice == "1":
        classification["vertebrate_type"] = "warm-blooded"
        print("\nWarm-blooded animals:")
        print("1. Mammal")
        print("2. Bird")
        warm_choice = input("Enter choice (1 or 2): ").strip()
        if warm_choice == "1":
            classification["class"] = "mammal"
        elif warm_choice == "2":
            classification["class"] = "bird"
    elif blood_choice == "2":
        classification["vertebrate_type"] = "cold-blooded"
        print("\nCold-blooded animals:")
        print("1. Reptile")
        print("2. Fish")
        print("3. Amphibian")
        cold_choice = input("Enter choice (1–3): ").strip()
        if cold_choice == "1":
            classification["class"] = "reptile"
        elif cold_choice == "2":
            classification["class"] = "fish"
        elif cold_choice == "3":
            classification["class"] = "amphibian"

elif main_choice == "2":
    classification["type"] = "invertebrate"
    print("\nInvertebrate types:")
    print("1. Insect")
    print("2. Arachnid")
    print("3. Mollusk")
    print("4. Crustacean")
    print("5. Worm")
    inv_choice = input("Enter choice (1–5): ").strip()
    inv_map = {
        "1": "insect",
        "2": "arachnid",
        "3": "mollusk",
        "4": "crustacean",
        "5": "worm"
    }
    classification["class"] = inv_map.get(inv_choice, "unknown")

# Step 5: Save data
animal_data = {
    "id": animal_id,
    "name": name,
    "species": species,
    "fun_facts": fun_facts,
    "emotion": emotion,
    "location": location,
    "classification": classification
}
animals[animal_id] = animal_data

with open(animal_file, "w") as f:
    json.dump(animals, f, indent=4)

# Step 6: Detect local IP address
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
        s.close()
    except Exception:
        ip = "127.0.0.1"
    return ip

local_ip = get_local_ip()

# Step 7: Generate QR Code
base_url = f"http://{local_ip}:5000/animal?id="
qr_link = base_url + animal_id
img = qrcode.make(qr_link)
qr_path = f"static/qrcodes/{animal_id}_qr.png"
img.save(qr_path)

# Step 8: Output
print(f"\n✅ Animal '{name}' added successfully!")
print(f"📁 Data saved to: {animal_file}")
print(f"🧾 QR Code saved to: {qr_path}")
print(f"🔗 Scan this QR or open: {qr_link}")
