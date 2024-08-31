# AIDA a WIP LLM powered assistant

Hey! im Ethan the developer of AIDA. Believe it or not this is my first big python project, Sooo please keep that in mind while looking at the code.

Im looking for work so if your in need of a Dev, please contact me at: ethan.a.williams7@gmail.com

## **Sections**

- [About](#description)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Making Plugins](#making-plugins)

## **Features**:

- Can take screenshots
- Tell the time
- Play music
- Read and wright to the clipboard
- Do math
- Take notes
- Plugin support

## **About AIDA**

AIDA is a assistant that is powered by [Googles Gemini API](https://ai.google.dev/gemini-api), or really any llm with a small amout of motification.
The TTS and STT are ran localy

### Whats the point of this project?

In short its a better version (in my opinan) of Siri/Google assistant, but now for pc, also partly inspaired by how useless the copilot preview is.

I just wanted to make a actully usefull voice assistant that is faster then opening a web browser and typing in your question

### Plans for the future?

I hope to add more things to the config like for hotkeys. I also plan to add a step to the setup to run everything completly localy. And i would love to have Mac and Linux support, but i dont have much experience with anything but Windows so i dont really know what im doing.
Other then that fill free to leave feature requests.

## **Installation**

you MUST have python installed for this to run if you dont have it then:

1. Download the latest version of Python from the official website: [Python Downloads](https://www.python.org/downloads/).
2. Run the installer and make sure to check the box that says "Add Python to PATH" before clicking "Install Now."
3. Verify the installation by opening a command prompt and typing:
   ```bash
   python --version
   ```

now that you have python time to install AIDA

**First way is if you have git installed**

1. - **Clone the repository**:

   ```bash
   git clone https://github.com/SquareDonut1/AIDA
   ```

2. - **Change to the directory**:

   ```bash
   cd AIDA
   ```

3. - **Run the setup file**:

   ```bash
   python setup.py
   ```

4. - **Go Through The Setup And Your Done!**

**The second way is for everyone else**

1. **Download**:

   [Click here](https://github.com/SquareDonut1/AIDA/archive/refs/heads/main.zip), or at the top of the page click Code > Download ZIP

2. **Extract**:

   Right click on the downloaded file and select Extract All...

3. **Run Set Up**

   Navigate to the extracted folder and double click setup.py
   run through setup and your done!

## **Usage**

- The hot key to use it is win-ctrl-r i plan to make this configurable in the future

## **Making Plugins**

I would recommend using math.ex as an example, but heres mroe to help you out

- **About the ex**:

  my .ex file a really just a pyton script with a json in the first half. i just wanted a single file per plugin soo this is what you get

- **Example Script**

  ```python
   {
   "functions": [
     {
       "function_name": "example()",
       "arguments": "none",
       "description": "a function that returns a string"
     }
   ]
   }

   ----------

   def example():
     return "Example"

  ```

- **So How Dose It Work**

  Every time the program runs it loads all the functions from all the plugins and gives them to the LLM in the system prompt. The LLM has been instructed to call any function it thinks it needs to respond the best it can

- **Testing The Script**

  If you put the test script in a file and name it with the extantion .ex and run main.py it should show that it loaded in the command line. To test it simply ask the assistant to run the "name of the funtion" funtion (the actual function name MUST be the same as the function_name).
  The LLM should respond and tell you that it returned "Example"

- **IMPORTAINT**

  Becose its loading python files that can have any amout of code please make sure that you read the source code for any plugin be for you run it

  If runing the function you get "Failed to execute the function." make sure that your returning somthing, becouse it progamed that if it gets nothing back from the function it assumes that it dident work

<sup>
ps if you hate the name dont blame me i had the LLM name 
itself and that was the best it could come up with</sup>
