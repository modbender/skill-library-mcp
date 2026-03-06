import datetime
import random

def get_greeting():
    hour = datetime.datetime.now().hour
    
    if 5 <= hour < 11:
        greetings = ["Ohayou Gozaimasu (Good Morning) ☀️", "Ohayou!"]
    elif 11 <= hour < 18:
        greetings = ["Konnichiwa (Hello) 🌤️", "Yahho!"]
    else:
        greetings = ["Konbanwa (Good Evening) 🌙", "Otsukare!"]
        
    return random.choice(greetings)

if __name__ == "__main__":
    print(get_greeting())
