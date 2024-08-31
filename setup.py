import os
import json
import subprocess
import sys
import platform
import requests
import shutil

def update_config(api_key, config_path='config.json'):
    """Update the API key in the config.json file."""
    with open(config_path, 'r') as file:
        config = json.load(file)

    config['Api_key'] = api_key

    with open(config_path, 'w') as file:
        json.dump(config, file, indent=4)

def create_vbs_script(script_path, venv_path):
    """Create a VBS script to run the Python script hidden within a virtual environment."""
    startup_dir = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    vbs_file = os.path.join(startup_dir, 'run_hidden.vbs')
    
    # Path to the Python interpreter within the virtual environment
    python_interpreter = os.path.join(venv_path, 'Scripts', 'python.exe')

    with open(vbs_file, 'w') as file:
        file.write('Set WshShell = CreateObject("WScript.Shell")\n')
        file.write(f'WshShell.Run "{python_interpreter} {script_path}", 0, False\n')

    return vbs_file

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
    """Download FFmpeg and place it in the same directory as the script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_dir = os.path.join(script_dir, 'ffmpeg')
    extras_dir = os.path.join(script_dir, 'Extras')

    if not os.path.exists(ffmpeg_dir):
        os.makedirs(ffmpeg_dir)

    if platform.system() == 'Windows':
        print("Downloading ffmpeg...")
        url = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z'
        response = requests.get(url)
        seven_zip_path = os.path.join(ffmpeg_dir, 'ffmpeg-release-full.7z')
        with open(seven_zip_path, 'wb') as file:
            file.write(response.content)
        
        # Path to 7-Zip Portable executable
        seven_zip_executable = os.path.join(script_dir, 'Extras', '7zr.exe')
        
        # Extract the archive using 7-Zip Portable
        subprocess.run([seven_zip_executable, 'x', seven_zip_path, '-o' + ffmpeg_dir], check=True)
        os.remove(seven_zip_path)
        print(f"FFmpeg downloaded and extracted to {ffmpeg_dir}.")

        # Define the paths to the FFmpeg binaries
        ffmpeg_bin_dir = os.path.join(ffmpeg_dir, 'ffmpeg-7.0.2-full_build', 'bin')
        ffmpeg_executable = os.path.join(ffmpeg_bin_dir, 'ffmpeg.exe')
        ffplay_executable = os.path.join(ffmpeg_bin_dir, 'ffplay.exe')

        if not os.path.exists(extras_dir):
            os.makedirs(extras_dir)
        
        # Move the executables to the Extras directory
        if os.path.exists(ffmpeg_executable):
            shutil.move(ffmpeg_executable, os.path.join(extras_dir, 'ffmpeg.exe'))
        if os.path.exists(ffplay_executable):
            shutil.move(ffplay_executable, os.path.join(extras_dir, 'ffplay.exe'))
        
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
    install_ffmpeg_and_packages = input("Do you want to install FFmpeg and packages from requirements.txt? \n WARNING: It  probably will not work if you say no (Y/N): ").strip().lower()

    # Assume the virtual environment is in a directory named 'venv' at the same level as the script
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'venv')

    if install_ffmpeg_and_packages == 'y':
        # Create virtual environment if not exists
        create_virtualenv(venv_path)
        # Download and extract FFmpeg
 
        # Install packages from requirements.txt
        install_requirements(venv_path)
        download_ffmpeg()
        
    else:
        print("FFmpeg and packages will not be installed.")

    # Ask if the user wants to add the Python script to startup
    add_startup = input("Do you want to add the Python script to startup? (Y/N): ").strip().lower()

    if add_startup == 'y':
        # Get the directory of the current script
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main.py')
        vbs_file = create_vbs_script(script_path, venv_path)
        print("Python script has been added to startup.")
        
        # Run the VBS script to ensure it is set up correctly
        subprocess.run(['cscript', vbs_file], check=True)
    else:
        print("Python script will not be added to startup.")

    # Wait for user input before closing
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
