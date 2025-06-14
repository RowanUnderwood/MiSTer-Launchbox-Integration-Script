import ftplib
import os
from tqdm import tqdm

def is_directory(ftp, name):
    """
    Checks if a given path on the FTP server is a directory.
    """
    try:
        # If we can change into it and back out, it's a directory
        ftp.cwd(name)
        ftp.cwd('..')
        return True
    except ftplib.error_perm:
        # This error typically means it's a file, not a directory
        return False

def process_directory(ftp, remote_path, local_path, drive_type):
    """
    Recursively scans an FTP directory, recreates the structure locally,
    and generates .bat files for each game.
    """
    # --- Skip any directory named "Palettes" (case-insensitive) ---
    if os.path.basename(remote_path).lower() == 'palettes':
        print(f"Skipping 'Palettes' directory: {remote_path}")
        return

    try:
        ftp.cwd(remote_path)
    except ftplib.error_perm as e:
        print(f"Warning: Could not access {remote_path}. Skipping. Error: {e}")
        return

    items = ftp.nlst()
    files = []
    dirs = []

    # --- Determine if the current path is inside a PSX or Saturn directory ---
    remote_path_lower = remote_path.lower()
    is_in_cd_system_dir = '/psx/' in remote_path_lower or '/saturn/' in remote_path_lower

    # Separate files from directories
    for item in items:
        # --- Skip any file named "boot.rom" (case-insensitive) ---
        if item.lower() == 'boot.rom':
            continue

        # --- Skip .bin files ONLY if we are inside a PSX or Saturn path ---
        if is_in_cd_system_dir and item.lower().endswith('.bin'):
            print(f"DEBUG: Skipping .bin file '{item}' in path '{remote_path}'")
            continue
            
        full_item_path = f"{remote_path}/{item}"
        if is_directory(ftp, full_item_path):
            dirs.append(item)
        else:
            files.append(item)
    
    # --- Skip directories that are completely empty ---
    if not files and not dirs:
        print(f"Skipping empty directory: '{remote_path}'")
        return

    # --- Create local directory if there are files to place in it ---
    if files:
        os.makedirs(local_path, exist_ok=True)
        print(f"\nProcessing directory: {remote_path}")

        # --- Create individual game .bat files with a progress bar ---
        for filename in tqdm(files, desc=f"Creating launchers in '{os.path.basename(remote_path)}'"):
            local_bat_filename = os.path.splitext(filename)[0] + ".bat"
            full_local_bat_path = os.path.join(local_path, local_bat_filename)
            
            full_remote_game_path = f"{remote_path}/{filename}"
            
            # --- Generate the correct path for the curl command ---
            if drive_type == 'usb0':
                # For USB scans, hardcode the path, ignoring %MISTERDRIVE%
                path_for_curl = full_remote_game_path
            else: # fat, arcade, etc.
                # For SD card scans, use the %MISTERDRIVE% variable for flexibility
                relative_path = full_remote_game_path.replace('/media/fat/', '', 1)
                path_for_curl = f"/media/%MISTERDRIVE%/{relative_path}"

            game_bat_content = f'curl --request POST --url "http://%MISTERIP%/api/launch" --data "{{\\"path\\":\\"{path_for_curl}\\"}}"'

            try:
                with open(full_local_bat_path, "w", encoding='utf-8') as f:
                    f.write(game_bat_content)
            except IOError as e:
                print(f"Error creating file {full_local_bat_path}: {e}")

    # --- Recurse into subdirectories ---
    for d in dirs:
        new_remote_path = f"{remote_path}/{d}"
        new_local_path = os.path.join(local_path, d)
        process_directory(ftp, new_remote_path, new_local_path, drive_type)
        ftp.cwd(remote_path)


def main():
    """
    Main function to drive the MiSTer launcher creation process.
    """
    # --- User Configuration Section ---
    print("--- MiSTer Launcher Configuration ---")
    print("Press Enter to use the default value shown in [brackets].")

    ftp_host = input("Enter FTP Host IP [192.168.2.56]: ") or "192.168.2.56"
    ftp_user = input("Enter FTP Username [root]: ") or "root"
    ftp_pass = input("Enter FTP Password [1]: ") or "1"
    
    # --- Create the main Launcher.bat file with user-defined settings ---
    launcher_content = f"""@echo off
set "MISTERIP={ftp_host}:8182"

rem Note: will likely be fat (for SD) or usb0 (for external/usb drive):
set "MISTERDRIVE=fat"

rem Launches the OSD Menu to trigger the Autosave before launching another title.
curl --request POST --url "http://%MISTERIP%/api/controls/keyboard/osd"

rem Uncomment the rem in the next line to open the mister remote control website/app when launching.
rem start "" http://%MISTERIP%/control

rem Increase or decrease time (sec) for waiting for Autosave to complete.
timeout /t 5

rem For calling/launching the passed-in batch for a title.
"%~1"
"""
    try:
        with open("Launcher.bat", "w") as f:
            f.write(launcher_content)
        print("\nSuccessfully created Launcher.bat in the root directory.")
    except IOError as e:
        print(f"Error creating Launcher.bat: {e}")
        return

    # --- Get user input for scanning scope ---
    print("\n--- Scan Scope ---")
    scan_arcade_input = input("Include /media/fat/_Arcade directory? (y/n) [y]: ").lower()
    scan_arcade = scan_arcade_input != 'n'

    print("\nSelect a source to scan:")
    print("1: Scan a single directory on SD Card (/media/fat/games/)")
    print("2: Scan ALL directories on SD Card (/media/fat/games/)")
    print("3: Scan a single directory on USB Drive (/media/usb0/games/)")
    print("4: Scan ALL directories on USB Drive (/media/usb0/games/)")
    choice = input("Enter your choice (1-4): ")

    dirs_to_scan = []
    local_base = os.getcwd()
    base_path = ""
    drive_type = ""

    if choice in ['1', '2']:
        base_path = "/media/fat/games"
        drive_type = "fat"
    elif choice in ['3', '4']:
        base_path = "/media/usb0/games"
        drive_type = "usb0"

    try:
        with ftplib.FTP(ftp_host, ftp_user, ftp_pass) as ftp:
            ftp.encoding = "utf-8"
            print(f"\nSuccessfully connected to FTP host: {ftp_host}")
            
            # --- Process /media/fat/games/ or /media/usb0/games/ directories ---
            if base_path:
                ftp.cwd(base_path)
                if choice in ['1', '3']: # Single directory scan
                    subdir = input(f"Enter the subdirectory to scan under {base_path}/: ")
                    if subdir:
                        dirs_to_scan.append(subdir)
                elif choice in ['2', '4']: # Full scan
                    print(f"Fetching all directories from {base_path}/...")
                    all_items = ftp.nlst()
                    for item_name in all_items:
                        if is_directory(ftp, f"{base_path}/{item_name}"):
                            dirs_to_scan.append(item_name)
                    print(f"Found directories to scan: {', '.join(dirs_to_scan)}")
                
                for directory in dirs_to_scan:
                    full_remote_path = f"{base_path}/{directory}"
                    local_path = os.path.join(local_base, directory)
                    process_directory(ftp, full_remote_path, local_path, drive_type)
                    ftp.cwd(base_path)

            # --- Process /media/fat/_Arcade/ directory if requested ---
            if scan_arcade:
                arcade_base_path = "/media/fat/_Arcade"
                arcade_local_path = os.path.join(local_base, "_Arcade")
                print("\nStarting scan of Arcade directory...")
                # The drive_type for arcade is 'fat' to ensure it uses %MISTERDRIVE%
                process_directory(ftp, arcade_base_path, arcade_local_path, 'fat')

        print("\nScript finished. All specified game launchers have been created!")

    except ftplib.all_errors as e:
        print(f"\nFTP Error: {e}")
        print("Please check your FTP server address, credentials, and if the directory exists.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
