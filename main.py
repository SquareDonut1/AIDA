import os
import json
import google.generativeai as genai
import sys
from TTS import piper_tts_client as piper
from STT import SpeechToText as stt
import pygame
import subprocess
import time
from pynput import keyboard  # Import pynput for global key listening

# Set console encoding to UTF-8


# Set up Gemini API key




# Initialize global variables
pressed_keys = set()
recording = False
LastRecording = False
last_release_time = 0  # Timestamp of the last key release
cooldown_period = 0   # Cooldown period in seconds
audio_process = None

with open("config.json", "r") as config_file:
    config = json.load(config_file)

sys.stdout.reconfigure(encoding='utf-8')
generation_config = config.get("generation_config", {})
safety_settings = config.get("safety_settings", [])
system_instruction = config.get("system_instruction", "")
model_name = config.get("model_name", "")
genai.configure(api_key=config.get("Api_key", ""))



def on_press(key):
    global recording, LastRecording, last_release_time, cooldown_period

    # Check if enough time has passed since the last release
    current_time = time.time()
    if (current_time - last_release_time) < cooldown_period:
        return  # Skip processing if cooldown period has not passed

    # Handle key press
    try:
        key_char = key.char
        if key_char is not None:
            pressed_keys.add(key_char)
    except AttributeError:
        # Handle special keys (e.g., Cmd, Ctrl)
        if key in {keyboard.Key.cmd, keyboard.Key.ctrl_l}:
            pressed_keys.add(str(key))

    # Check if "Cmd + Ctrl + R" is pressed
    if 'Key.cmd' in pressed_keys and '\x12' in pressed_keys:
        stop_audio()

    # Update recording status based on keys pressed
    recording = 'Key.cmd' in pressed_keys and '\x12' in pressed_keys

    if recording and not LastRecording:
        LastRecording = recording
        try:
            play_audio("sounds/recording-start.wav", 1)
            recorder.start_recording()
            print("Started Recording")
        except Exception as e:
            print(f"Error starting recording: {e}") 

def on_release(key):
    global recording, LastRecording, last_release_time

    if hasattr(key, 'char') and key.char is not None:
        pressed_keys.discard(key.char)
    else:
        key_str = str(key)
        pressed_keys.discard(key_str)

    try:
        pressed_keys.discard('Key.cmd')
        pressed_keys.discard('\x12')
    except:
        ""
    
    # Update recording status based on keys pressed
    recording = 'Key.cmd' in pressed_keys and '\x12' in pressed_keys

    if not recording and LastRecording:
        LastRecording = recording
        try:
            play_audio("sounds/recording-end.wav", 1)
            user_input = recorder.stop_recording()
            print("Stopped Recording")
            if "No speech detected." not in user_input:
                print(f"user: {user_input}")
                Get_Response(user_input)
            else:
                print("No speech detected, TTS not triggered.")
        except Exception as e:
            print(f"Error stopping recording: {e}")

    # Update the last release time
    last_release_time = time.time()

 
def load_functions(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data.get('functions', [])

def parse_custom_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        json_part, python_part = content.split('----------')
        metadata = json.loads(json_part.strip())
        return metadata, python_part.strip()

def load_plugins(python_code):
    exec(python_code, globals())
    return python_code

def call_function(func_string):
    try:
        # Find the first '(' and the last ')'
        open_paren_index = func_string.find('(')
        close_paren_index = func_string.rfind(')')

        # Ensure '(' comes before ')' and both are present
        if open_paren_index != -1 and close_paren_index != -1 and open_paren_index < close_paren_index:
            func_name = func_string[:open_paren_index].strip()
            args_str = func_string[open_paren_index + 1:close_paren_index].strip()

            if func_name == 'set_clipboard':
                # Treat everything inside parentheses as a single argument
                args = (args_str,)
            else:
                # For other functions, split arguments by commas and handle them
                args = eval(f"({args_str},)") if args_str else ()

            # Retrieve the function from globals
            func = globals().get(func_name)
            if func:
                return func(*args)
            else:
                raise ValueError(f"Function {func_name} not found.")
        else:
            raise ValueError("Function call format is invalid.")
    except (SyntaxError, ValueError, Exception) as e:
        print(f"Error executing function: {e}")
        return None



def upload_to_gemini(path, mime_type=None):
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def load_and_parse_ex_files(directory_path):
    parsed_files = []
    for file_name in os.listdir(directory_path):
        if file_name.endswith('.ex'):
            file_path = os.path.join(directory_path, file_name)
            print(f"Loaded: {file_name}")
            with open(file_path, 'r') as file:
                content = file.read()
                json_part, python_part = content.split('----------')
                metadata = json.loads(json_part.strip())
                parsed_files.append((metadata, python_part.strip()))
    return parsed_files

# Load and inspect custom Python code
directory_path = 'plugins'  # Change this to your directory path
all_parsed_files = load_and_parse_ex_files(directory_path)

# Combine all function metadata from each .ex file
combined_functions_data = [item for metadata, _ in all_parsed_files for item in metadata.get('functions', [])]

# Load all Python code from each .ex file
for _, python_code in all_parsed_files:
    load_plugins(python_code)

def play_audio(file_path, speed_factor):
    global audio_process
    audio_process = subprocess.Popen(
        ['Extras/ffplay', '-nodisp', '-autoexit', '-af', f'atempo={speed_factor}', file_path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

def stop_audio():
    global audio_process
    if audio_process is not None:
        audio_process.terminate()
        audio_process = None

model = genai.GenerativeModel(
    model_name=model_name,
    safety_settings=safety_settings,
    generation_config=generation_config,
    system_instruction=f"{system_instruction} {combined_functions_data}"
)

chat = model.start_chat(history=[])
tts_client = piper.PiperTTSClient(verbose=True)
voice_path = os.path.abspath("TTS/models")
pygame.mixer.init()

# Set up the global keyboard listener with pynput
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    recorder = stt.MicrophoneRecorder()

    def Get_Response(user_input):
        response = chat.send_message(user_input)

        if "[api]" in response.text:
            function_string = response.text.replace("[api]", "").strip()
            try:
                print("Computer:", response.text)
                result = call_function(function_string)
                if result is not None:
                    print(f"[api-response] {result}")
                    response = chat.send_message(["[api-response]",result])
                else:
                    print("Failed to execute the function.")
            except Exception as e:
                print(f"Error executing function: {e}")

        try:
            print("Computer:", response.text)
        except UnicodeEncodeError as e:
            print("Encoding error: ", e)
            print("Assistant response could not be displayed properly.")

        result = tts_client.tts(response.text, "temp.wav", voice_path)
        print(f"TTS Result: {result}")
        if result == "success":
            play_audio("temp.wav", 1.3)
            print("done")

    while True:
        time.sleep(1)