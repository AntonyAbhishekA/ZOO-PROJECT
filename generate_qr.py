import qrcode
import os

# Create folder if not exists
os.makedirs("static/qrcodes", exist_ok=True)

# Input
animal_id = input("Enter the animal ID: ").strip()

# Render-hosted live URL
base_url = "https://zoo-project-kiny.onrender.com/animal?id="

# Full link
qr_link = base_url + animal_id

# Generate QR Code
img = qrcode.make(qr_link)
qr_path = f"static/qrcodes/{animal_id}_qr.png"
img.save(qr_path)

print(f"\n✅ QR Code generated for {animal_id}")
print(f"📁 Saved to: {qr_path}")
print(f"🔗 Link: {qr_link}")
