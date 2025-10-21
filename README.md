# Team Fortress 2 Custom Cosmetic Disabler
<img width="75%" alt="github" src="https://github.com/user-attachments/assets/aca92ded-300f-48fa-a7f8-dba37d268957" />

## What does this program do?
The Cosmetic Disabler allows you to disable cosmetics of your choice, stopping them from rendering in-game, while leaving every other cosmetic unaffected.

It will ***dynamically update*** with Team Fortress 2 and should not need to be updated after seasonal updates to detect new cosmetics.
## How do I use it?

### Windows
Download the latest release and run 'Cosmetic Disabler.exe' to start the program. On first time start-up you will have to provide your 'Team Fortress 2' directory if the program can't auto-detect.
Once the directory is selected the program will load every cosmetic in TF2 into a list.

### Linux
1. Download the repository:
   ```bash
   git clone https://github.com/dilbertron2/Cosmetic-Disabler.git && cd Cosmetic-Disabler
   ```
   Or click the green **"Code"** button at the top right of the GitHub page and select "Download ZIP", then extract it.

2. Install Python and tkinter:

   - **Debian/Ubuntu**: `sudo apt install python3 python3-pip python3-tk python3-venv`
   - **Arch**: `sudo pacman -S python python-pip tk`
   - **Fedora**: `sudo dnf install python3 python3-pip python3-tkinter python3-virtualenv`

3. Make the launcher executable and run it:
   ```bash
   chmod +x run.sh && ./run.sh
   ```
   For subsequent runs, just use `./run.sh`


You can select cosmetics from the list by left-clicking, left-click and dragging, shift-clicking and ctrl-clicking. Press the relevant "... Selected" button to add/remove cosmetics from your target list. When you are ready to create a VPK with your changes, click the 'Create VPK' button to generate the VPK file. You will be given a choice on behavior regarding cosmetic bodygroups, and then the VPK file will be created in the same folder as the program.

# [Latest Release](https://github.com/dilbertron2/Cosmetic-Disabler/releases)

## FAQ

**Q:** Where do I put the VPK after creation?

**A:** Place the VPK file in your 'Team Fortress 2/tf/custom' folder. The outputted VPK is also compatible with [Cukei's Casual Preloader](https://github.com/cueki/casual-pre-loader), if Voodoo-Cursed Souls are disabled it is recommended to use the Casual Preloader to avoid errors/crashes.
