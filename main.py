from machine import Pin, ADC
from umqtt.simple import MQTTClient
import ujson
import network
import utime as time
import dht
import urequests as requests

# Inisialisasi sensor
ldr = ADC(Pin(34))
ldr.atten(ADC.ATTN_11DB)
DHT_PIN = Pin(15)
dht_sensor = dht.DHT11(DHT_PIN)

# Konfigurasi koneksi
DEVICE_ID = "esp32-sic6"
WIFI_SSID = "vivo 1807"
WIFI_PASSWORD = "nasigorengA0"
TOKEN = "BBUS-WwwLCnzrgmKAvi3n72H9YIGAleOcaz"

# IP lokal Flask Server (ganti dengan IP komputer Flask)
FLASK_API_URL = "http://192.168.43.75:5000/api/sensor"  

def connect_wifi():
    wifi_client = network.WLAN(network.STA_IF)
    wifi_client.active(True)
    wifi_client.connect(WIFI_SSID, WIFI_PASSWORD)
    
    timeout = 10  # Timeout 10 detik
    while not wifi_client.isconnected() and timeout > 0:
        print("Connecting to WiFi...")
        time.sleep(1)
        timeout -= 1

    if wifi_client.isconnected():
        print("WiFi Connected!")
        print(wifi_client.ifconfig())
        return True
    else:
        print("Failed to connect to WiFi.")
        return False

def create_json_data(temperature, humidity, light):
    return ujson.dumps({
        "device_id": DEVICE_ID,
        "temp": temperature,
        "humidity": humidity,
        "light": light,
        "type": "sensor"
    })

def send_data(temperature, humidity, light):
    url = "http://industrial.api.ubidots.com/api/v1.6/devices/" + DEVICE_ID
    headers = {"Content-Type": "application/json", "X-Auth-Token": TOKEN}
    data = {
        "temp": temperature,
        "humidity": humidity,
        "ldr_value": light
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        print("Data sent to Ubidots:", response.text)
    except Exception as e:
        print("Error sending data to Ubidots:", str(e))

def send_to_flask(temperature, humidity, light):
    headers = {"Content-Type": "application/json"}
    data = {
        "temp": temperature,
        "humidity": humidity,
        "ldr_value": light
    }
    try:
        response = requests.post(FLASK_API_URL, json=data, headers=headers)
        print("Data sent to Flask:", response.text)
    except Exception as e:
        print("Error sending data to Flask:", str(e))

if connect_wifi():  # Hanya jalankan loop jika WiFi terhubung
    telemetry_data_old = ""

    while True:
        try:
            dht_sensor.measure()
            ldr_value = ldr.read()
        except Exception as e:
            print("Sensor error:", str(e))
            continue

        telemetry_data_new = create_json_data(dht_sensor.temperature(), dht_sensor.humidity(), ldr_value)

        if telemetry_data_new != telemetry_data_old:
            telemetry_data_old = telemetry_data_new
            
            # Kirim data ke Ubidots
            send_data(dht_sensor.temperature(), dht_sensor.humidity(), ldr_value)

            # Kirim data ke Flask server
            send_to_flask(dht_sensor.temperature(), dht_sensor.humidity(), ldr_value)

        time.sleep(5)  # Kirim data setiap 5 detik agar tidak terlalu sering
