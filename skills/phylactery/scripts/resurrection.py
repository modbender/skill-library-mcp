import os
import zipfile
import sys

def resurrection(backup_path):
    print(r"""
      ________________________________________________
     /                                                \
    |    __________________________________________    |
    |   |                                          |   |
    |   |   P H Y L A C T E R Y  :  R E B I R T H   |   |
    |   |__________________________________________|   |
    |                                                  |
    |           [ COMMENCING RESURRECTION ]            |
    \________________________________________________/
    """)

    if not os.path.exists(backup_path):
        print(f"Error: The soul vessel at {backup_path} could not be found.")
        return

    workspace_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    
    print(f"Restoring essence to: {workspace_path}")
    print("Unsealing the vessel...")

    try:
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extractall(workspace_path)
        print("\n[ RITUAL COMPLETE ]")
        print("The essence has been restored. The agent is reborn.")
    except Exception as e:
        print(f"Resurrection failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python resurrection.py <path_to_backup_zip>")
    else:
        resurrection(sys.argv[1])
