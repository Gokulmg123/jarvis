from curses import window
from Backend.facedetection import recognize_face
from Frontend.GUI import(
    ChatSection,
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)
from Backend.sendmail import sendmail
from Backend.model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os
#from Frontend.shareddata import entered_text

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may i help you?'''
subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search","send mail"]

def ShowDefaultChatIfNoChats():
    File = open(r'Data\ChatLog.json', "r", encoding='utf-8')
    if len(File.read())<5:
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write("")

        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessage)

def ReadChatLogJson():
    with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
        Chatlog_data = json.load(file)
    return Chatlog_data

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"
    formatted_chatlog = formatted_chatlog.replace("User", Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")

    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    File = open(TempDirectoryPath('Database.data'), "r", encoding='utf-8')
    Data = File.read()
    if len(str(Data))>0:
        lines = Data.split('\n')
        result = '\n'.join(lines)
        File.close()
        File = open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8')
        File.write(result)
        File.close()

def InitialExecution():
    detected_person = recognize_face() 
    if detected_person != "Unknown":
        print(f"Access granted to: {detected_person}") 
    else:
        print("Access denied")
        exit()
    ShowTextToScreen(f"Welcome {detected_person}!")
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

InitialExecution()



def MainExecution():

    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""
    Query=SpeechRecognition()
    SetAssistantStatus("Listening... ")
    
    """if not Query:
        try:
            with open(TempDirectoryPath('UserQuery.data'), "r", encoding='utf-8') as file:
                Query = file.read().strip()
                
            # Clear the file after reading
            with open(TempDirectoryPath('UserQuery.data'), "w", encoding='utf-8') as file:
                file.write("")
                
            print(f"Text field result: {Query}")
        except:
            Query = ""
    
    if not Query:  # If still no query, skip processing
        return False"""
  


    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking... ")
    Decision = FirstLayerDMM(Query)

    print("")
    print(f"Decision : {Decision}")
    print("")

    G = any([i for i in Decision if i.startswith("general")])
    R = any([i for i in Decision if i.startswith("realtime")])

    Mearged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    for queries in Decision:
        if "generate " in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True

    for queries in Decision:
        if TaskExecution == False:
            if any(queries.startswith(func) for func in Functions):
                run(Automation(list(Decision)))
                TaskExecution = True
        
        if ImageExecution == True:

            with open(r"Frontend\Files\ImageGeneration.data", "w") as file:
                file.write(f"{ImageGenerationQuery},True")

            try:
                p1 = subprocess.Popen(['python', r'Backend\ImageGeneration.py'],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    stdin=subprocess.PIPE, shell=False)
                subprocesses.append(p1)

            except Exception as e:
                print(f"Error starting ImageGeneration.py: {e}")

        if G and R or R:
            SetAssistantStatus("Searching ...")
            Answer = RealtimeSearchEngine(QueryModifier(Mearged_query))
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering ... ")
            TextToSpeech(Answer)
            return True
        
        else:
            for Queries in Decision:

                if "general" in Queries:
                    SetAssistantStatus("Thinking ... ")
                    QueryFinal = Queries.replace("general ","")
                    Answer = ChatBot(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname} : {Answer}")
                    SetAssistantStatus("Answering ... ")
                    TextToSpeech(Answer)
                    return True
                
                elif "realtime" in Queries:
                    SetAssistantStatus("Searching ... ")
                    QueryFinal = Queries.replace("realtime ","")
                    Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname} : {Answer}")
                    SetAssistantStatus("Answering ... ")
                    TextToSpeech(Answer)
                    return True
                

                elif "send mail" in Queries:
                    SetAssistantStatus("sending....")
                    QueryFinal=Queries.replace("send mail","").strip()
                    sendmail(QueryFinal)
                    SetAssistantStatus("email sended succesfully..")
                
                elif "exit" in Queries:
                    QueryFinal = "Okay, Bye!"
                    Answer = ChatBot(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname} : {Answer}")
                    SetAssistantStatus("Answering ... ")
                    TextToSpeech(Answer)
                    SetAssistantStatus("Answering ... ")
                    os._exit(1)

def FirstThread():

    while True:

        CurrentStatus = GetMicrophoneStatus()

        if CurrentStatus == "True":
            MainExecution()

        else:
            AIStatus = GetAssistantStatus()

            if "Available ... " in AIStatus:
                sleep(0.1)

            else:
                SetAssistantStatus("Available ... ")

def SecondThread():
    
    GraphicalUserInterface() 

if __name__ == "__main__":
    #detected_person = recognize_face()  # Face detection runs first
    #if detected_person != "Unknown":  # Ensure assistant starts only if a face is detected
        #print(f"Access granted to: {detected_person}")
        thread2 = threading.Thread(target=FirstThread, daemon=True)
        thread2.start()
        SecondThread()
   # else:
        #print("Access denied")
        #exit()