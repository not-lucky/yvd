import poe
import logging
import sys
import json
import threading
import time
import datetime
"""
{
  "a2": "Claude-instant",
  "a2_100k": "Claude-instant-100k",
  "beaver": "GPT-4",
  "chinchilla": "ChatGPT",
  "a2_2": "Claude+",
  "capybara": "Sage",
  "acouchy": "Google-PaLM"
}
"""

#send multiple messages and get their responses
#note: this is not recommended anymore due to the risk of a ban

# token = sys.argv[1]
poe.logger.setLevel(logging.INFO)
client = poe.Client("zPCds1Urcxmhkf6-OOognw%3D%3D")

thread_count = 0

fl = open("poe_api.txt", "a", encoding="utf-8")


def message_thread(model, prompt, counter):
    global thread_count
    for chunk in client.send_message(model, prompt, with_chat_break=False):
        pass

#   print(""+prompt+"\n\n"+chunk["text"]+"\n"*3)
    print("\n\n" +
          f"Model: {model}\nTime: {str(datetime.datetime.now())}\n\n" +
          "USER:\n" + prompt + "\n\nAI:\n" + chunk["text"] + "\n" * 3,
          file=fl)

    thread_count -= 1


# m = '''As a cloud computing expert, answer the following questions in small but precise points. Write points in such a way that next is somewhat related to previous point (it helps to visualize). Write at least 4 unique points about each topic/subtopics and at most whatever you feel necessary. Also write pro and cons. Provide two examples for each question, if possible:
# '''

prompts = """
Based on the code that I provided, I want you write a project file subsection based on this program named "1st shit" which is under section "Output Design". Keep the language formal as it needs to be submitted to the university.
"""

m = [
     'Details of output', 'Expected Warnings/Errors'
]

for model in m:
    a = prompts
    # message_thread('beaver', prompts + model, 0)
    a = a.replace('1st shit', model)
    message_thread('a2_100k', a, 0)
