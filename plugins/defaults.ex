{
  "functions": [
    {
      "function_name": "get_screenshot()",
      "arguments": "none",
      "description": "a function that returns a screenshot of the users computer"
    },
    {
      "function_name": "get_picture()",
      "arguments": "none",
      "description": "a function that returns a picture from the users webcam"
    },
    {
      "function_name": "get_clipboard()",
      "arguments": "none",
      "description": "a function that returns a the contents of the users clipboard"
    },
    {
      "function_name": "set_clipboard()",
      "arguments": "str",
      "description": "a function that sets the contents of the users clipboard"
    },
    {
      "function_name": "save_note()",
      "arguments": "str,name of file",
      "description": "a function that save to passed string to a file with the given name, dont ask what the user whats the name to be just pick a appropriate name, and make sure to have .txt in the name"
    }
  ]
}


----------


import os
import mss
import mss.tools
import cv2
import pyperclip


def get_picture():
    try:
        cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        ret, frame = cam.read()
        cam.release()
        file_path = "captured_camera.png"
        cv2.imwrite(file_path, frame)  
        im = upload_to_gemini(file_path)  
        os.remove("captured_camera.png")
        return im
    except Exception as e:
        return f"Error capturing image: {e}"

def get_screenshot():
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            file_path = "captured_screen.png"
            mss.tools.to_png(screenshot.rgb, screenshot.size, output=file_path)
            im = upload_to_gemini(file_path)
            os.remove("captured_screen.png")
            return im
    except Exception as e:
        return f"Error capturing screen: {e}"

def get_clipboard():
    try:
        return f"""BEGINING OF CLIPBOARD CONTENTS:  {pyperclip.paste()}  :ENDING OF CLIPBOARD CONTENTS """
    except pyperclip.PyperclipException as e:
        return f"Error accessing clipboard: {e}"

def set_clipboard(text = ""):
    try:
        print(text)
        pyperclip.copy(f"{text}")
        return "Successfuly coped to clipboard"
    except pyperclip.PyperclipException as e:
        return f"Error accessing clipboard: {e}"


def save_note(content, filename):
    if not filename.endswith('.txt'):
        filename += '.txt'  # Ensure the filename has .txt extension
    dir_path = os.path.abspath("Notes")
    os.makedirs(dir_path, exist_ok=True)  # Create notes directory if it doesn't exist
    filepath = os.path.join(dir_path, filename)
    with open(filepath, 'w') as file:
        file.write(content)
    return "Successfully saved note"

