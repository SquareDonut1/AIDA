{
  "functions": [
    {
      "function_name": "get_current_time()",
      "arguments": "none",
      "description": "a function that returns the current time"
    }
  ]
}


----------


import datetime

# Define functions
def get_current_time():
    return datetime.datetime.now().strftime("%H:%M")


