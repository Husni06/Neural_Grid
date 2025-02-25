from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
from pymongo.server_api import ServerApi


# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Inisialisasi koneksi ke MongoDB
client = MongoClient("mongodb+srv://neuralgrid:123@cluster0.p8r9p.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0", server_api=ServerApi('1'))  # Sesuaikan URL MongoDB Anda
db = client['sensor_data']  # Nama database
collection = db['iot_sensors']  # Nama collection

# Endpoint untuk menyimpan data sensor
@app.route('/api/sensor', methods=['POST'])
def save_sensor_data():
    try:
        # Ambil data JSON dari body request
        data = request.get_json()

        # Validasi data
        #if not data or 'device_id' not in data or 'temp' not in data or 'humidity' not in data or 'light' not in data or 'type' not in data:
            #return jsonify({"error": "Data tidak lengkap"}), 400
        
        # Menambahkan waktu ke data (timestamp)
        data['timestamp'] = datetime.now()

        # Simpan data ke MongoDB
        collection.insert_one(data)

        return jsonify({"message": "Data berhasil disimpan"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sensor', methods=['GET'])
def get_sensor_data():
    try:
        # Ambil semua data dari collection
        data = collection.find()

        # Format data ke dalam bentuk list of dictionaries
        result = [{"temp": item["temp"],
                   "humidity": item["humidity"],
                   "ldr_value": item["ldr_value"],
                   "timestamp": item["timestamp"]} for item in data]

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Run server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
