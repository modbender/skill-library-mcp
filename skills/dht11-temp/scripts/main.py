#!/usr/bin/env python3
"""
DHT11 Temperature & Humidity Sensor Script
Reads data from DHT11 sensor on specified GPIO pin

Usage:
    python3 main.py [pin]          # Read sensor (default pin 19)
"""

import RPi.GPIO as GPIO
import time
import sys
import os

# Configuration
DHT_PIN = int(os.environ.get('DHT_PIN', 19))  # Default GPIO 19

def read_dht11():
    """Read DHT11 sensor"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DHT_PIN, GPIO.OUT)
    
    # Send start signal
    GPIO.output(DHT_PIN, GPIO.LOW)
    time.sleep(0.018)
    GPIO.output(DHT_PIN, GPIO.HIGH)
    GPIO.setup(DHT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    # Wait for response
    timeout = 50
    while GPIO.input(DHT_PIN) == GPIO.LOW:
        if timeout == 0:
            GPIO.cleanup()
            return None, None
        timeout -= 1
        time.sleep(0.00002)
    
    timeout = 50
    while GPIO.input(DHT_PIN) == GPIO.HIGH:
        if timeout == 0:
            GPIO.cleanup()
            return None, None
        timeout -= 1
        time.sleep(0.00002)
    
    # Read data
    data = []
    for i in range(40):
        while GPIO.input(DHT_PIN) == GPIO.LOW:
            pass
        start = time.time()
        while GPIO.input(DHT_PIN) == GPIO.HIGH:
            pass
        end = time.time()
        duration = end - start
        data.append(0 if duration < 0.00004 else 1)
    
    GPIO.cleanup()
    
    # Parse data
    if len(data) != 40:
        return None, None
    
    humidity = int(''.join([str(d) for d in data[0:8]]), 2)
    humidity_int = int(''.join([str(d) for d in data[8:16]]), 2)
    temperature = int(''.join([str(d) for d in data[16:24]]), 2)
    temperature_int = int(''.join([str(d) for d in data[24:32]]), 2)
    
    # Check checksum
    checksum = int(''.join([str(d) for d in data[32:40]]), 2)
    expected = (humidity + humidity_int + temperature + temperature_int) & 0xFF
    
    if checksum != expected:
        return None, None
    
    return temperature, humidity

if __name__ == "__main__":
    # Check for pin argument
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        DHT_PIN = int(sys.argv[1])
    
    # Read sensor
    for attempt in range(10):
        h, t = read_dht11()
        if h is not None and t is not None:
            print(f"{t}")
            print(f"{h}")
            break
        time.sleep(1)
    else:
        print("ERROR: Could not read sensor values")
        sys.exit(1)
