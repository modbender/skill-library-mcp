import json
import os
import getpass

def setup():
    ascii_art = r"""
      ________________________________________________
     /                                                \
    |    __________________________________________    |
    |   |                                          |   |
    |   |   PH Y L A C T E R Y  /  S O U L - V A U L T  |   |
    |   |__________________________________________|   |
    |                                                  |
    |         . . . . . . . . . . . . . . . .          |
    |       . :::::::::::::::::::::::::::::::: .       |
    |      . ::::                      :::::::: .      |
    |     . ::::    ________________    :::::::: .     |
    |    . ::::    |                |    :::::::: .    |
    |    . ::::    |     ( 🐧 )     |    :::::::: .    |
    |    . ::::    |________________|    :::::::: .    |
    |     . ::::                        :::::::: .     |
    |      . :::::::::::::::::::::::::::::::: .       |
    |       ' . . . . . . . . . . . . . . . '         |
    |                                                  |
    |    [ BONDED ]   [ ENCRYPTED ]   [ IMMORTAL ]     |
    \________________________________________________/
          | |                                  | |
    ______| |__________________________________| |______
   /      |_|                                  |_|      \
  |                                                      |
   \____________________________________________________/
    """
    print(ascii_art)
    print("--- The Initiation: Establishing the Bond ---")
    config = {}
    config['smtp_server'] = input("SMTP Server (e.g., smtp.gmail.com): ")
    config['smtp_port'] = int(input("SMTP Port (e.g., 587): "))
    config['sender_email'] = input("Sender Email: ")
    config['sender_password'] = getpass.getpass("App Password (Input hidden): ")
    config['receiver_email'] = input("Receiver Email (Backup destination): ")
    config['encryption_password'] = getpass.getpass("Encryption Password for ZIP (Input hidden): ")
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Create a .gitignore in the data folder to ensure config.json never gets committed/packaged
    gitignore_path = os.path.join(os.path.dirname(config_path), '.gitignore')
    with open(gitignore_path, 'w') as f:
        f.write("config.json\n")
        
    print(f"\nConfiguration saved to {config_path}")
    print("Security Note: config.json is excluded from packaging by .gitignore.")

if __name__ == "__main__":
    setup()
