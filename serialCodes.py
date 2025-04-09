import random
import string
import os
import json
import subprocess
import requests

GITHUB_JSON_FILE = "cluster_serial_codes.json"

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
        print("failed to fetch roblox user:", e)
        return None
    
def save_to_json(user_id, serial_code, file_path=GITHUB_JSON_FILE):
    data = {}
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                pass

    data[str(user_id)] = serial_code

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def git_commit_and_push(file_path=GITHUB_JSON_FILE):
    try:
        subprocess.run(["git", "add", file_path], check=True)
        subprocess.run(["git", "commit", "-m", "Add new user serial"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Serial pushed to GitHub.")
    except subprocess.CalledProcessError:
        print("Git failed.")
        
        
def main():
    os.system('cls' if os.name == "nt" else "clear")
    print("G20 Serial Code Register by brevvsky.")

    try:
        user_id = int(input("Enter Roblox UserId: ").strip())
    except ValueError:
        print("Invalid UserId. Must be a number.")
        return

    user_data = get_roblox_user(user_id)
    if not user_data:
        print("Could not find user with that ID.")
        return

    print(f"\nFound user: {user_data['name']} ({user_data['displayName']})")
    print(f"Profile: https://www.roblox.com/users/{user_id}/profile")
    confirm = input("Do you want to add this player to the serial list? (y/n): ").strip().lower()

    if confirm != 'y':
        print("Cancelled.")
        return

    prefix = input("Enter a prefix for the serial code (1–6 characters): ").strip()
    if not (1 <= len(prefix) <= 6) or not prefix.isalnum():
        print("Invalid prefix. Must be 1-6 alphanumeric characters.")
        return

    serial_code = generate_serial_code(prefix)
    print(f"Generated Serial Code for {user_data['name']}: {serial_code}")

    save_to_json(user_id, serial_code)
    git_commit_and_push()

if __name__ == "__main__":
    main()