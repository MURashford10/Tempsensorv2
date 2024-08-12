import os
import glob
import time
import sqlite3

# Initialize the temperature sensor
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    with open(device_file, 'r') as f:
        lines = f.readlines()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f
    return None, None

def log_temperature():
    temp_c, temp_f = read_temp()
    if temp_c is not None:
        conn = sqlite3.connect('temperature_data.db')
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS temperature (timestamp TEXT, temp_c REAL, temp_f REAL)')
        c.execute('INSERT INTO temperature (timestamp, temp_c, temp_f) VALUES (CURRENT_TIMESTAMP, ?, ?)', (temp_c, temp_f))
        conn.commit()
        conn.close()
    return temp_c, temp_f
