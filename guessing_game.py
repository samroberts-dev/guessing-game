## IMPORT THE REQUIRED LIBRARIES ##
import os
import json
import hashlib
import random
import time
import math

## SET THE FOLDER NAME FOR ALL THE DATA STORAGE ##
user_data_directory = "guessing_game_data_stores" ## Please keep in mind that wherever you have the python file saved, is where the folder will spawn in. ##

## SECURITY FOR THE PASSWORD ##
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

## FIND THE SPECIFIC USERS FILE ##
def get_user_file(username):
    safe_username = "".join(char for char in username if char.isalnum() or char in ('_', '-'))
    return os.path.join(user_data_directory, f"{safe_username}.json")

## CREATE NEW USERS DATA ##
def create_user(username, password):
    file_path = get_user_file(username)
    if os.path.exists(file_path):
        print(f"User '{username}' already exists.")
        return False

    user_data = {
        "username": username,
        "password_hash": hash_password(password),
        "games_played": "0"
    }
    with open(file_path, "w") as f:
        json.dump(user_data, f, indent = 4)
    print(f"User '{username}' created successfully.")
    return True

## LOAD USERS FILE ##
def login(username, password):
    user_data = load_user(username)
    if not user_data:
        print(f"User not found.")
        return False
    if user_data["password_hash"] == hash_password(password):
        print(f"Welcome back, {username}!")
        return True
    else:
        print("Incorrect password")
        return False

def main():
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    if not os.path.exists(get_user_file(username)):
        create_user(username, password)
    else:
        login(username, password)

main()

        
