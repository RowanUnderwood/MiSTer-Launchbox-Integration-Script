import os
import time
import random
import subprocess
import pickle
import msvcrt  # For Windows-specific non-blocking keyboard input
from tqdm import tqdm

GAMELIST_FILENAME = 'attract_mode_gamelist.dat'

def scan_for_games(root_dir):
    """
    Recursively scans all subdirectories for .bat files, excluding Launcher.bat.
    Shows a progress bar during the scan.
    """
    print("Scanning for game launchers... this may take a moment.")
    bat_files = []
    
    # First, collect all files to get a total for the progress bar
    all_files_to_check = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            all_files_to_check.append(os.path.join(root, file))

    # Now, process the files with a progress bar
    for file_path in tqdm(all_files_to_check, desc="Scanning files"):
        if file_path.lower().endswith('.bat'):
            # Exclude the main launcher itself
            if os.path.basename(file_path).lower() != 'launcher.bat':
                bat_files.append(os.path.abspath(file_path))
                
    return bat_files

def save_gamelist(gamelist, filename=GAMELIST_FILENAME):
    """Saves the list of game paths to a data file."""
    with open(filename, 'wb') as f:
        pickle.dump(gamelist, f)
    print(f"Saved gamelist with {len(gamelist)} games to {filename}")

def load_gamelist(filename=GAMELIST_FILENAME):
    """Loads the list of game paths from a data file."""
    try:
        with open(filename, 'rb') as f:
            gamelist = pickle.load(f)
        print(f"Loaded gamelist with {len(gamelist)} games from {filename}")
        return gamelist
    except FileNotFoundError:
        return []

def main():
    """Main function to run the attract mode loop."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("--- MiSTer Attract Mode ---")
    
    gamelist = []
    
    # Check if a gamelist file exists and ask the user if they want to rescan
    if os.path.exists(GAMELIST_FILENAME):
        rescan_input = input("Gamelist found. Rescan for new games? (y/n) [n]: ").lower()
        if rescan_input != 'y':
            gamelist = load_gamelist()
    
    # If no gamelist was loaded (or user chose to rescan), perform a new scan
    if not gamelist:
        gamelist = scan_for_games('.')
        if gamelist:
            save_gamelist(gamelist)

    if not gamelist:
        print("\nNo game .bat files found in any subdirectories. Nothing to do.")
        input("Press Enter to exit.")
        return

    # Get the time interval from the user
    while True:
        try:
            interval_str = input(f"\nEnter time between game launches (in seconds) [60]: ") or "60"
            interval = int(interval_str)
            if interval > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a number.")
            
    # --- Main Attract Mode Loop ---
    try:
        while True:
            # Randomly select a game and get its display name
            game_path = random.choice(gamelist)
            game_name = os.path.splitext(os.path.basename(game_path))[0]
            
            # Launch the game using Launcher.bat in a new process
            print(f"\nLaunching {game_name}...")
            subprocess.Popen(['.\\Launcher.bat', game_path], shell=True)
            
            # Start the countdown timer
            for i in range(interval, 0, -1):
                os.system('cls' if os.name == 'nt' else 'clear')
                print("--- MiSTer Attract Mode ---")
                print(f"\nCurrently Running: {game_name}")
                print(f"\nNext game in: {i} seconds...")
                print("\nPress the SPACEBAR to exit.")
                
                # Check for spacebar press without blocking
                if msvcrt.kbhit():
                    if msvcrt.getch() == b' ':
                        print("\nSpacebar pressed. Exiting attract mode...")
                        return # Exit the function completely
                
                time.sleep(1)

    except KeyboardInterrupt:
        print("\nExiting attract mode...")
    finally:
        # Ensure any running game process is terminated on exit
        # This is a bit aggressive but ensures a clean state.
        subprocess.run("taskkill /im curl.exe /f", shell=True, capture_output=True)
        print("Goodbye!")


if __name__ == "__main__":
    main()
