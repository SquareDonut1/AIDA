import os
import json
import subprocess
import sys
import platform
import requests
import shutil
import win32com.client

def update_config(api_key, config_path='config.json'):
    """Update the API key in the config.json file."""
    with open(config_path, 'r') as file:
        config = json.load(file)

    config['Api_key'] = api_key

    with open(config_path, 'w') as file:
        json.dump(config, file, indent=4)

def create_ps1_script(script_path, venv_path):
    """Create a PowerShell script to run the Python script hidden within a virtual environment."""
    ps1_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run_hidden.ps1')

    # Path to the Python interpreter within the virtual environment
    python_interpreter = os.path.join(venv_path, 'Scripts', 'python.exe')

    with open(ps1_file, 'w') as file:
        file.write(f"$psi = New-Object System.Diagnostics.ProcessStartInfo\n")
        file.write(f"$psi.FileName = '{python_interpreter}'\n")
        file.write(f"$psi.Arguments = '{script_path}'\n")
        file.write("$psi.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden\n")
        file.write("$psi.UseShellExecute = $true\n")
        file.write("[System.Diagnostics.Process]::Start($psi)\n")

    return ps1_file

def create_shortcut(ps1_file):
    """Create a shortcut to the PowerShell script in the Startup folder."""
    startup_dir = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    shortcut_path = os.path.join(startup_dir, 'run_hidden.lnk')

    # Create the shortcut
    shell = win32com.client.Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(shortcut_path)

    # Set target to PowerShell and pass the script file as an argument
    shortcut.TargetPath = "powershell.exe"
    shortcut.Arguments = f"-ExecutionPolicy Bypass -File \"{ps1_file}\""
    shortcut.WorkingDirectory = os.path.dirname(ps1_file)
    shortcut.IconLocation = "powershell.exe"  # Optional: Change icon if desired
    shortcut.Save()

def create_virtualenv(venv_path):
    """Create a virtual environment if it doesn't exist."""
    if not os.path.exists(venv_path):
        print(f"Creating virtual environment at {venv_path}...")
        subprocess.run([sys.executable, '-m', 'venv', venv_path], check=True)
        print("Virtual environment created.")
    else:
        print("Virtual environment already exists.")

def install_requirements(venv_path):
    """Install the packages from requirements.txt into the virtual environment."""
    pip_executable = os.path.join(venv_path, 'Scripts', 'pip.exe')
    requirements_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'requirements.txt')
    
    if os.path.isfile(requirements_file):
        print("Installing packages from requirements.txt...")
        subprocess.run([pip_executable, 'install', '-r', requirements_file], check=True)
    else:
        print("requirements.txt not found. No packages installed.")

def download_ffmpeg():
    """Download FFmpeg and place it in the Extras directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_dir = os.path.join(script_dir, 'ffmpeg')
    extras_dir = os.path.join(script_dir, 'Extras')

    # Create the directories if they do not exist
    if not os.path.exists(ffmpeg_dir):
        os.makedirs(ffmpeg_dir)
    if not os.path.exists(extras_dir):
        os.makedirs(extras_dir)

    if platform.system() == 'Windows':
        print("Downloading ffmpeg...")
        url = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z'
        response = requests.get(url)
        seven_zip_path = os.path.join(ffmpeg_dir, 'ffmpeg-release-full.7z')
        
        # Write the response content to a file
        with open(seven_zip_path, 'wb') as file:
            file.write(response.content)

        # Path to 7-Zip Portable executable
        seven_zip_executable = os.path.join(script_dir, 'Extras', '7zr.exe')
        
        # Check if 7z executable exists
        if not os.path.exists(seven_zip_executable):
            print("7zr.exe not found in Extras. Please ensure it's available.")
            return
        
        # Extract the archive using 7-Zip Portable
        subprocess.run([seven_zip_executable, 'x', seven_zip_path, '-o' + ffmpeg_dir], check=True)
        os.remove(seven_zip_path)
        print(f"FFmpeg downloaded and extracted to {ffmpeg_dir}.")

        # Find the first subdirectory inside the ffmpeg directory
        for item in os.listdir(ffmpeg_dir):
            subfolder_path = os.path.join(ffmpeg_dir, item)
            if os.path.isdir(subfolder_path):
                ffmpeg_bin_dir = os.path.join(subfolder_path, 'bin')  # Look for the 'bin' folder
                break
        else:
            print("No subdirectory found in the FFmpeg folder.")
            return

        ffmpeg_executable = os.path.join(ffmpeg_bin_dir, 'ffmpeg.exe')
        ffplay_executable = os.path.join(ffmpeg_bin_dir, 'ffplay.exe')

        # Move the executables to the Extras directory
        try:
            if os.path.exists(ffmpeg_executable):
                shutil.move(ffmpeg_executable, os.path.join(extras_dir, 'ffmpeg.exe'))
            else:
                print("ffmpeg.exe was not found after extraction.")
            
            if os.path.exists(ffplay_executable):
                shutil.move(ffplay_executable, os.path.join(extras_dir, 'ffplay.exe'))
            else:
                print("ffplay.exe was not found after extraction.")
        except Exception as e:
            print(f"Error moving FFmpeg executables: {e}")
        
        # Remove the extracted FFmpeg directory
        shutil.rmtree(ffmpeg_dir)
        print(f"FFmpeg executables have been moved to {extras_dir} and the FFmpeg directory has been deleted.")
    elif platform.system() == 'Linux':
        subprocess.run(['sudo', 'apt', 'install', '-y', 'ffmpeg'], check=True)
        print("FFmpeg installed.")
    else:
        raise NotImplementedError('Platform not supported for FFmpeg installation.')




def main():
    print("You will NEED a Gemini API key, which has a free tier.")
    print("The free tier has a limit, but it's so high that it's probably enough.")
    print("The key will be saved to config.json\n")

    # Get API key from user
    api_key = input("Please enter your Gemini API key: ")

    # Update the API key in config.json
    update_config(api_key)
    print("API key has been updated in config.json\n")

    # Ask if the user wants to install FFmpeg and packages
    install_ffmpeg_and_packages = input("Do you want to install FFmpeg and packages from requirements.txt? \n WARNING: It probably will not work if you say no (Y/N): ").strip().lower()

    # Assume the virtual environment is in a directory named 'venv' at the same level as the script
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'venv')

    if install_ffmpeg_and_packages == 'y':
        # Create virtual environment if not exists
        create_virtualenv(venv_path)
        # Download and extract FFmpeg
        download_ffmpeg()
        # Install packages from requirements.txt
        install_requirements(venv_path)
        
    else:
        print("FFmpeg and packages will not be installed.")

    # Ask if the user wants to add the Python script to startup
    add_startup = input("Do you want to add the Python script to startup? (Y/N): ").strip().lower()

    if add_startup == 'y':
        # Get the directory of the current script
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main.py')
        ps1_file = create_ps1_script(script_path, venv_path)
        create_shortcut(ps1_file)
        print("Python script has been added to startup.")
        subprocess.run(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", ps1_file])
    else:
        print("Python script will not be added to startup.")


    # Wait for user input before closing
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
