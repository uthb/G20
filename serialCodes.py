import random
import string
import os
import json
import subprocess
import requests
import pyperclip
from colorama import init, Fore
from datetime import datetime

# Script written by brevvsky, used Stack overflow for some help.

init(autoreset=True)

GITHUB_JSON_FILE = "cluster_serial_codes.json"
WEBHOOK_URL = "https://discord.com/api/webhooks/1359675223317938438/29eEkC3zylIGKk305LdgvL3c85S2yMBepIts3li6xpF7zxi_-glrceF-B-4Puzd6f3rI" 

def generate_block(length=4):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_serial_code(prefix):
    blocks = [generate_block() for _ in range(3)]
    return f"{prefix.upper()}-" + '-'.join(blocks)

def get_roblox_user(user_id):
    try:
        url = f"https://users.roblox.com/v1/users/{user_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(Fore.RED + "Failed to fetch Roblox user:", e)
        return None

def load_serials(file_path=GITHUB_JSON_FILE):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_to_json(user_id, serial_code, file_path=GITHUB_JSON_FILE):
    data = load_serials(file_path)
    data[str(user_id)] = {
        "serial": serial_code,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def git_commit_and_push(file_path=GITHUB_JSON_FILE):
    try:
        subprocess.run(["git", "add", file_path], check=True)
        subprocess.run(["git", "commit", "-m", "Add new user serial"], check=True)
        subprocess.run(["git", "push"], check=True)
        print(Fore.GREEN + "Serial pushed to GitHub.")
    except subprocess.CalledProcessError:
        print(Fore.RED + "Git push failed.")

def send_webhook(user_data, serial_code):
    try:
        payload = {
            "username": "SerialBot",
            "embeds": [{
                "title": f"New Serial Code Issued",
                "color": 3066993,
                "fields": [
                    {"name": "User", "value": f"{user_data['name']} ({user_data['displayName']})"},
                    {"name": "UserId", "value": str(user_data['id'])},
                    {"name": "Serial Code", "value": serial_code},
                    {"name": "Timestamp", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                ]
            }]
        }
        requests.post(WEBHOOK_URL, json=payload)
    except Exception as e:
        print(Fore.YELLOW + "Webhook failed:", e)

def search_serials():
    data = load_serials()
    if not data:
        print(Fore.YELLOW + "No serials found.")
        return

    choice = input("Search by (u)ser ID or (l)ist all?: ").strip().lower()
    if choice == 'u':
        uid = input("Enter user ID: ").strip()
        if uid in data:
            print(Fore.CYAN + f"User {uid} -> Serial: {data[uid]['serial']} | Added: {data[uid]['timestamp']}")
        else:
            print(Fore.RED + "User not found.")
    elif choice == 'l':
        print(Fore.GREEN + "\nAll Issued Serials:")
        for uid, info in data.items():
            print(f"User ID: {uid} | Serial: {info['serial']} | Time: {info['timestamp']}")
    else:
        print("Invalid choice.")

def main():
    os.system('cls' if os.name == "nt" else "clear")
    print(Fore.MAGENTA + "G20 Serial Code Register by brevvsky\n")

    action = input("Do you want to (r)egister a new user or (s)earch existing serials?: ").strip().lower()
    if action == 's':
        search_serials()
        return
    elif action != 'r':
        print("Cancelled.")
        return

    try:
        user_id = int(input("Enter Roblox UserId: ").strip())
    except ValueError:
        print(Fore.RED + "Invalid UserId. Must be a number.")
        return

    existing_data = load_serials()
    if str(user_id) in existing_data:
        print(Fore.YELLOW + f"User already registered with serial: {existing_data[str(user_id)]['serial']}")
        return

    user_data = get_roblox_user(user_id)
    if not user_data:
        print(Fore.RED + "Could not find user with that ID.")
        return

    print(Fore.CYAN + f"\nFound user: {user_data['name']} ({user_data['displayName']})")
    print(f"Profile: https://www.roblox.com/users/{user_id}/profile")
    confirm = input("Do you want to add this player to the serial list? (y/n): ").strip().lower()

    if confirm != 'y':
        print("Cancelled.")
        return

    prefix = input("Enter a prefix for the serial code (1–6 characters): ").strip()
    if not (1 <= len(prefix) <= 6) or not prefix.isalnum():
        print(Fore.RED + "Invalid prefix. Must be 1-6 alphanumeric characters.")
        return

    serial_code = generate_serial_code(prefix)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(Fore.GREEN + f"\nGenerated Serial Code for {user_data['name']}: {serial_code}")
    print(Fore.BLUE + f"Timestamp: {timestamp}")

    try:
        pyperclip.copy(serial_code)
        print(Fore.GREEN + "Serial code copied to clipboard.")
    except Exception as e:
        print(Fore.YELLOW + "Clipboard copy failed:", e)

    save_to_json(user_id, serial_code)
    git_commit_and_push()
    send_webhook(user_data, serial_code)

if __name__ == "__main__":
    main()
