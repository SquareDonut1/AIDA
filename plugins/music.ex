{
  "functions": [
    {
      "function_name": "play_song()",
      "arguments": "str(songname)",
      "description": "a function that plays the specified song. songname is a sring as sould always be in ''"
    },
      {
      "function_name": "stop_song()",
      "arguments": "none",
      "description": "a function that stops the current song"
    }
  ]
}

----------


import yt_dlp
import os
import pygame
import threading
import time

# Shared variable for playback control
stop_flag = threading.Event()

def play_song(song_name):
    # Create a thread to run the play_song_async function
    thread = threading.Thread(target=play_song_async, args=(song_name,))
    thread.start()
    return f"Successfuly started playing {song_name}"




def stop_song():
    try:
        stop_flag.set()
        return "Successfuly stoped song"
    except Exception as e:
        print(f"""Failed to stop song: {str(e)}""")
        return f"Failed to stop song: {str(e)}"




def play_song_async(song_name):
    # Set the path to ffmpeg in the current directory
    ffmpeg_path = os.path.dirname(os.path.abspath("Extras/ffmpeg"))
    
    # Update yt-dlp options to use ffmpeg
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'default_search': 'ytsearch1:',
        'noplaylist': True,
        'ffmpeg_location': ffmpeg_path,
        'outtmpl': 'music.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Search and download the audio file
            ydl.extract_info(song_name, download=True)
        
        # Check if 'music.mp3' exists
        music_file = 'music.mp3'
        if os.path.exists(music_file):
            # Initialize pygame mixer
            pygame.mixer.init()
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.play()

            # Wait for playback to finish or be stopped
            while pygame.mixer.music.get_busy() and not stop_flag.is_set():
                time.sleep(0.1)
            
            # Stop playback if flag is set
            pygame.mixer.music.stop()
            
            # Add a delay before removing the file
            time.sleep(2)
        else:
            print("Error: music.mp3 not found.")

        


    except Exception as e:
        print(f"An error occurred: {str(e)}")
