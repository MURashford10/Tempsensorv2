from flask import Flask, render_template, jsonify, send_file
import sqlite3
import threading
import time
import matplotlib.pyplot as plt
from io import BytesIO
from tempv2 import read_temp

app = Flask(__name__)

# Global variables to store the latest temperature
latest_temp_c = None
latest_temp_f = None

def update_temperature_periodically():
    global latest_temp_c, latest_temp_f
    while True:
        latest_temp_c, latest_temp_f = read_temp()
        time.sleep(5)  # Update the temperature every 5 seconds

def log_temperature_periodically():
    while True:
        if latest_temp_c is not None and latest_temp_f is not None:
            log_temperature(latest_temp_c, latest_temp_f)
        time.sleep(1800)  # Log temperature every 30 minutes

def log_temperature(temp_c, temp_f):
    conn = sqlite3.connect('temperature_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS temperature
                 (timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, temp_c REAL, temp_f REAL)''')
    c.execute('INSERT INTO temperature (temp_c, temp_f) VALUES (?, ?)', (temp_c, temp_f))
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/latest_temp')
def latest_temp():
    return jsonify({'temp_c': latest_temp_c, 'temp_f': latest_temp_f})

@app.route('/plot_celsius')
def plot_celsius():
    conn = sqlite3.connect('temperature_data.db')
    c = conn.cursor()
    c.execute('SELECT temp_c FROM temperature ORDER BY timestamp DESC LIMIT 48')
    data = c.fetchall()
    conn.close()

    temps_c = [temp[0] for temp in data][::-1]

    plt.figure(figsize=(10, 4))
    plt.plot(temps_c, marker='o', linestyle='-', color='blue')
    plt.title('Temperature in Celsius')
    plt.xlabel('Reading')
    plt.ylabel('Temperature (°C)')
    plt.grid(True)

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    return send_file(img, mimetype='image/png')

@app.route('/plot_fahrenheit')
def plot_fahrenheit():
    conn = sqlite3.connect('temperature_data.db')
    c = conn.cursor()
    c.execute('SELECT temp_f FROM temperature ORDER BY timestamp DESC LIMIT 48')
    data = c.fetchall()
    conn.close()

    temps_f = [temp[0] for temp in data][::-1]

    plt.figure(figsize=(10, 4))
    plt.plot(temps_f, marker='o', linestyle='-', color='red')
    plt.title('Temperature in Fahrenheit')
    plt.xlabel('Reading')
    plt.ylabel('Temperature (°F)')
    plt.grid(True)

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    return send_file(img, mimetype='image/png')

if __name__ == '__main__':
    threading.Thread(target=update_temperature_periodically, daemon=True).start()
    threading.Thread(target=log_temperature_periodically, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port=1000)
