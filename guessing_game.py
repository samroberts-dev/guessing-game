import os
import json
import hashlib
import random
import time

### =============== LOG IN SYSTEM ================= ###
user_data_directory = "guessing_game_data_stores"

if not os.path.exists(user_data_directory):
    os.makedirs(user_data_directory)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_file(username):
    safe_username = "".join(char for char in username if char.isalnum() or char in ('_', '-'))
    return os.path.join(user_data_directory, f"{safe_username}.json")

def create_user(username, password):
    file_path = get_user_file(username)
    if os.path.exists(file_path):
        print(f"User '{username}' already exists.")
        return False
    user_data = {
        "username": username,
        "password_hash": hash_password(password),
        "games_played": 0,
        "total_guesses": 0,
        "average_guesses": 0,
        "best_game": None
    }
    with open(file_path, "w") as f:
        json.dump(user_data, f, indent=4)
    print(f"User '{username}' created successfully.")
    return True

def load_user(username):
    file_path = get_user_file(username)
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r") as f:
        return json.load(f)

def save_user(user_data):
    file_path = get_user_file(user_data["username"])
    with open(file_path, "w") as f:
        json.dump(user_data, f, indent=4)

def login(username, password):
    user_data = load_user(username)
    if not user_data:
        print("User not found.")
        return False
    if user_data["password_hash"] == hash_password(password):
        print(f"Welcome back, {username}!")
        return True
    print("Incorrect password.")
    return False

def login_setup():
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    if not os.path.exists(get_user_file(username)):
        create_user(username, password)
    else:
        if not login(username, password):
            return login_setup()
    return username

### ================== GUESSING GAME SYSTEM ===================== ###

def typewriter(text):
    print()
    for char in text:
        print(char, end="", flush=True)
        time.sleep(random.uniform(0.02,0.05))
    print("\n")

def number_validation(lowest, highest):
    while True:
        try:
            number = int(input(f"Please enter a number between {lowest} and {highest}: "))
            if number < lowest or number > highest:
                typewriter(f"Hey! That number is out of range. Enter a number between {lowest} and {highest}.")
                continue
            return number
        except ValueError:
            typewriter("Are we serious?? Just enter a number please...")
        except SystemError:
            typewriter("Sorry, the number you have entered is too large.")

def check_guess(guess, correct_number, highest_guess, lowest_guess, counter, username):
    if guess == correct_number:
        typewriter(f"Congratulations, you guessed the number correctly after {counter} turns!")
        update_user_stats(username, counter)
        update_global_stats(username, counter)
    elif guess > correct_number:
        typewriter("Too high, try again.")
        highest_guess = guess
    elif guess < correct_number:
        typewriter("Too low, try again.")
        lowest_guess = guess
    return highest_guess, lowest_guess

def initialise():
    counter = 0
    guess = 0
    correct_number = random.randint(1,1000)
    highest_guess = 1000
    lowest_guess = 1
    return counter, guess, correct_number, highest_guess, lowest_guess

def update_user_stats(username, guesses_taken):
    user_data = load_user(username)
    if not user_data:
        return
    user_data["games_played"] += 1
    user_data["total_guesses"] += guesses_taken
    user_data["average_guesses"] = round(user_data["total_guesses"] / user_data["games_played"],2)
    if user_data["best_game"] is None or guesses_taken < user_data["best_game"]:
        user_data["best_game"] = guesses_taken
    save_user(user_data)

### ================= GLOBAL STATS ================= ###

global_stats_file = os.path.join(user_data_directory, "global_stats.json")

def load_global_stats():
    if not os.path.exists(global_stats_file):
        stats = {
            "total_games":0,
            "total_guesses":0,
            "global_average":0,
            "lowest_guess":None,
            "player_with_most_games":None,
            "player_with_lowest_guess":None,
            "player_with_lowest_average":None,
            "player_with_highest_average":None
        }
        save_global_stats(stats)
        return stats
    with open(global_stats_file,"r") as f:
        return json.load(f)

def save_global_stats(stats):
    with open(global_stats_file,"w") as f:
        json.dump(stats,f,indent=4)

def update_global_stats(username, guesses_taken):
    global_stats = load_global_stats()
    user_data = load_user(username)
    if not user_data:
        return

    # total games and guesses
    global_stats["total_games"] += 1
    global_stats["total_guesses"] += guesses_taken
    global_stats["global_average"] = round(global_stats["total_guesses"] / global_stats["total_games"],2)

    # player with most games
    if (global_stats["player_with_most_games"] is None or
        user_data["games_played"] > load_user(global_stats["player_with_most_games"])["games_played"]):
        global_stats["player_with_most_games"] = username

    # lowest single guess ever
    if global_stats["lowest_guess"] is None or guesses_taken < global_stats["lowest_guess"]:
        global_stats["lowest_guess"] = guesses_taken
        global_stats["player_with_lowest_guess"] = username

    # lowest average
    if global_stats["player_with_lowest_average"] is None:
        global_stats["player_with_lowest_average"] = username
    else:
        lowest_avg_user = load_user(global_stats["player_with_lowest_average"])
        if user_data["average_guesses"] < lowest_avg_user["average_guesses"]:
            global_stats["player_with_lowest_average"] = username

    # highest average
    if global_stats["player_with_highest_average"] is None:
        global_stats["player_with_highest_average"] = username
    else:
        highest_avg_user = load_user(global_stats["player_with_highest_average"])
        if user_data["average_guesses"] > highest_avg_user["average_guesses"]:
            global_stats["player_with_highest_average"] = username

    save_global_stats(global_stats)

### ================= MAIN GAME LOOP ================= ###

def main(username):
    counter, guess, correct_number, highest_guess, lowest_guess = initialise()
    while guess != correct_number:
        guess = number_validation(lowest_guess, highest_guess)
        counter += 1
        highest_guess, lowest_guess = check_guess(
            guess,
            correct_number,
            highest_guess,
            lowest_guess,
            counter,
            username
        )

### ================= PROGRAM START ================= ###
username = login_setup()
main(username)


