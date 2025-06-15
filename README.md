# **MiSTer Batch Launcher & Attract Mode Scripts**

This project contains two Python scripts designed to streamline and enhance the experience of launching games on a MiSTer FPGA, especially for use with front-ends like [LaunchBox](https://www.launchbox-app.com/).

1. **Launcher Generator**: Scans your MiSTer's game directories via FTP and automatically creates individual Windows .bat files for every game.  
2. **Attract Mode**: Uses the generated .bat files to cycle through your game collection randomly, launching a new game at a set interval.

## **Prerequisites**

Before using these scripts, please ensure your MiSTer setup meets the following requirements:

* **Python 3**: You must have Python installed on your Windows PC to run these scripts.  
* **FTP Server Enabled**: The FTP server must be running on your MiSTer. You can enable this in the MiSTer's main menu scripts.  
* **mrext Remote Control**: The mrext remote control service must be installed and active on your MiSTer. This is what allows the scripts to send launch commands. You can find installation instructions here: [mrext GitHub Page](https://github.com/wizzomafizzo/mrext?tab=readme-ov-file#remote).

## **The Scripts**

### **1\. Launcher Generator (create\_launchers\_v2.py)**

This is the core script for setting up your game launchers.

#### **How it Works**

The script connects to your MiSTer via FTP and asks you where to scan for games (/media/fat/games/ on the SD card or /media/usb0/games/ on a USB drive). It recursively scans the specified directories and generates two types of files on your local PC:

1. **Launcher.bat**: A master script that acts as the "emulator" in LaunchBox. It handles the pre-launch commands, such as triggering an autosave, before running the specific game's batch file.  
2. **Individual Game Launchers (\[Game Name\].bat)**: For every game file found, a corresponding .bat file is created inside a matching local directory structure (e.g., games from /media/fat/games/N64 will have launchers created in a local N64 folder). These individual files contain the specific curl command to launch that one game.

This two-step process makes the setup extremely flexible and easy to configure in front-ends.

### **2\. Attract Mode (Attract mode.py)**

This script provides a fun "attract mode" or "demo mode" for your MiSTer setup.

#### **How it Works**

After you have generated your game launchers, run this script from the same directory.

1. **Scan**: On its first run, it scans all the subdirectories for the .bat files you created and saves this list in a local cache file (attract\_mode\_gamelist.dat) for faster startup on subsequent runs.  
2. **Launch**: The script asks for a time interval (in seconds). It then enters a loop where it randomly picks a game from the list, launches it via the Launcher.bat script, and displays a countdown timer on screen.  
3. **Exit**: You can press the SPACEBAR at any time to gracefully exit the attract mode.

This is not only a great way to showcase your collection but also an **excellent method for testing your generated .bat files** to ensure they all launch correctly.

## **Credits**

A huge thank you to **PointNClickPops** for the original inspiration and foundational knowledge. Much of the logic for the curl commands and the Launcher.bat structure is based on their excellent guide, which you can find here:

* [**GUIDE: Launching MiSTer files from LaunchBox**](https://github.com/PointNClickPops/MiSTerBox/wiki/GUIDE:-Launching-MiSTer-files-from-LaunchBox)
