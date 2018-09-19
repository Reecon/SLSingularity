#---------------------------
#   Import Libraries
#---------------------------
import os
import codecs
import sys
import json
import datetime
import time
import re
sys.path.append(os.path.join(os.path.dirname(__file__), "lib")) #point at lib folder for classes / references

import clr
clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")
clr.AddReference('System.Speech')
from System.Speech.Synthesis import SpeechSynthesizer

#---------------------------
#   [Required] Script Information
#---------------------------
ScriptName = "Singularity"
Website = "reecon820@gmail.com"
Description = "Lets people whisper the bot for TTS"
Creator = "Reecon820"
Version = "1.2.4.0"

#---------------------------
#   Settings Handling
#---------------------------
class SSettings:
    def __init__(self, settingsfile=None):
        try:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
                self.__dict__ = json.load(f, encoding="utf-8")
        except:
            self.Command = "!tts"
            self.Cooldown = 10
            self.Permission = "moderator"
            self.Info = ""
            self.Volume = 50
            self.Voice = "Microsoft David Desktop"
            self.UseSpeech2Go = False
            self.VoiceRate = 0
            self.ShoutoutPromo = False
            self.VCQuotes = False

    def Reload(self, jsondata):
        self.__dict__ = json.loads(jsondata, encoding="utf-8")

    def Save(self, settingsfile):
        try:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="w+") as f:
                json.dump(self.__dict__, f, encoding="utf-8", indent=4)
            with codecs.open(settingsfile.replace("json", "js"), encoding="utf-8-sig", mode="w+") as f:
                f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8')))
        except:
            Parent.Log(ScriptName, "Failed to save settings to file.")

#---------------------------
#   Define Global Variables
#---------------------------
global sSettingsFile
sSettingsFile = ""
global sScriptSettings
sScriptSettings = SSettings()
global sSpeak
sSpeak = SpeechSynthesizer()

global sLogHtmlPath
sLogHtmlPath = os.path.abspath(os.path.join(os.path.dirname(__file__), "MessageLog.html"))

global sLogFilePath
sLogFilePath = os.path.abspath(os.path.join(os.path.dirname(__file__), "MessageLog.txt"))

global sMessageLog
sMessageLog = []

#---------------------------
#   [Required] Initialize Data (Only called on load)
#---------------------------
def Init():

    #   Create Settings Directory
    directory = os.path.join(os.path.dirname(__file__), "Settings")
    if not os.path.exists(directory):
        os.makedirs(directory)

    #   Load settings
    global sSettingsFile
    sSettingsFile = os.path.join(os.path.dirname(__file__), "Settings\settings.json")

    global sScriptSettings
    sScriptSettings = SSettings(sSettingsFile)

    # querry installed voices and update ui file
    updateUi()

    LoadMessageLog()

    sSpeak.Volume = sScriptSettings.Volume
    sSpeak.SelectVoice(sScriptSettings.Voice)

    return

#---------------------------
#   [Required] Execute Data / Process messages
#---------------------------
def Execute(data):
    #   Check if the propper command is used, the command is not on cooldown and the user has permission to use the command
    if data.IsWhisper() and data.IsFromTwitch() and data.GetParam(0).lower() == sScriptSettings.Command and not Parent.IsOnCooldown(ScriptName, sScriptSettings.Command) and Parent.HasPermission(data.User, sScriptSettings.Permission, sScriptSettings.Info):
        
        # remove command from message
        cleanMessage = data.Message.split(' ', 1)[1]

        SayAndLog(cleanMessage, data.User)

        Parent.AddCooldown(ScriptName, sScriptSettings.Command, sScriptSettings.Cooldown)  # Put the command on cooldown

    elif data.IsFromTwitch() and data.IsRawData() and "USERNOTICE" in data.RawData and sScriptSettings.ShoutoutPromo:
        #@badges=subscriber/0,premium/1;color=#179B38;display-name=CrazyGirlWithAGun;emotes=;id=5a04b6bd-6835-4b76-91f8-ea9b833bf7d0;login=crazygirlwithagun;mod=0;msg-id=giftpaidupgrade;msg-param-promo-gift-total=220292;msg-param-promo-name=Subtember;msg-param-sender-login=previouslyungrokkable;msg-param-sender-name=previouslyungrokkable;room-id=62983472;subscriber=1;system-msg=CrazyGirlWithAGun\sis\scontinuing\sthe\sGift\sSub\sthey\sgot\sfrom\spreviouslyungrokkable!\sThey're\sone\sof\s220292\sgift\ssubs\sto\scontinue\sthis\sSubtember.;tmi-sent-ts=1537333390444;turbo=0;user-id=94921845;user-type= :tmi.twitch.tv USERNOTICE #kaypikefashion
        
        if ("msg-param-promo-name=Subtember;" in data.RawData):
            giftee = re.search("login=.*;", data.RawData).group(0).strip(";").split("=")[1]
            gifter = re.search("msg-param-sender-name=.*;", data.RawData).group(0).strip(";").split("=")[1]
            message = "{0} is continuing the Gift Sub they got from {1}!".format(giftee, gifter)
            SayAndLog(message, "Bot")
        
    elif data.IsFromTwitch() and data.IsChatMessage() and sScriptSettings.VCQuotes and data.GetParam(0).lower() == "!quote" and data.GetParam(1).lower() == "add" and data.User.lower() == "viciouscuddles":
        
        # remove command from quote
        cleanQuote = data.Message.split(' ', 2)[2]

        SayAndLog(cleanQuote, data.User)

#---------------------------
#   [Required] Tick method (Gets called during every iteration even when there is no incoming data)
#---------------------------
def Tick():
    return

#---------------------------
#   [Optional] Parse method (Allows you to create your own custom $parameters) 
#---------------------------
def Parse(parseString, userid, username, targetid, targetname, message):
    return parseString

#---------------------------
#   [Optional] Reload Settings (Called when a user clicks the Save Settings button in the Chatbot UI)
#---------------------------
def ReloadSettings(jsonData):
    # Execute json reloading here
    sScriptSettings.__dict__ = json.loads(jsonData)
    sScriptSettings.Save(sSettingsFile)
    # Don't forget to set the values to the things
    updateUi()
    sSpeak.Volume = sScriptSettings.Volume
    sSpeak.Rate = sScriptSettings.VoiceRate
    sSpeak.SelectVoice(sScriptSettings.Voice)

#---------------------------
#   [Optional] Unload (Called when a user reloads their scripts or closes the bot / cleanup stuff)
#---------------------------
def Unload():
    return

#---------------------------
#   [Optional] ScriptToggled (Notifies you when a user disables your script or enables it)
#---------------------------
def ScriptToggled(state):
    return

def SayAndLog(text, user):
    # send line to html
    time = "{}".format(datetime.datetime.now())
    jsonData = '{{"date": "{0}", "user": "{1}", "message": "{2}" }}'.format(time, user, text)
    
    Parent.BroadcastWsEvent("EVENT_TTS_MESSAGE", jsonData)

    if sScriptSettings.UseSpeech2Go:
        if os.path.exists("C:/Program Files (x86)/Speech2Go/"):
            os.system('"C:/Program Files (x86)/Speech2Go/Speech2Go.exe" -t "' + text + '"')
        else:
            Parent.Log(ScriptName, "Can not find Speech2Go at default path")
    else:
        sSpeak.Speak(text) # do the thing

    # save line to log file
    try:
        with codecs.open(sLogFilePath, encoding='utf-8', mode='a+') as f:
            line = "{0} -- {1}: {2}".format(datetime.datetime.now(), user, text)
            f.write(line + "\n")
    except Exception as err:
        Parent.Log(ScriptName, "Error saving log file: {}".format(err))

def OpenMessageLog():
    os.startfile(sLogHtmlPath)
    time.sleep(1) # give ws time to connect

    # send last 5 log messages to html
    jsonData = json.dumps(sMessageLog[-5:])
    Parent.BroadcastWsEvent("EVENT_TTS_LOG", jsonData)

def updateUi():
    # querry installed voices and update ui file
    voices = sSpeak.GetInstalledVoices()
    names = [voice.VoiceInfo.Name for voice in voices]

    ui = {}
    UiFilePath = os.path.join(os.path.dirname(__file__), "UI_Config.json")
    try:
        with codecs.open(UiFilePath, encoding="utf-8-sig", mode="r") as f:
            ui = json.load(f, encoding="utf-8")
    except Exception as err:
        Parent.Log(ScriptName, "Error loading UI file: {0}".format(err))

    if not ui['Voice']['value']:
        ui['Voice']['value'] = names[0]

    ui['Voice']['value'] = sScriptSettings.Voice
    ui['Voice']['items'] = names
    # update ui with loaded settings
    ui['Volume']['value'] = sScriptSettings.Volume
    ui['Command']['value'] = sScriptSettings.Command
    ui['Cooldown']['value'] = sScriptSettings.Cooldown
    ui['Permission']['value'] = sScriptSettings.Permission
    ui['Info']['value'] = sScriptSettings.Info
    ui['UseSpeech2Go']['value'] = sScriptSettings.UseSpeech2Go
    ui['ShoutoutPromo']['value'] = sScriptSettings.ShoutoutPromo
    ui['VCQuotes']['value'] = sScriptSettings.VCQuotes

    try:
        with codecs.open(UiFilePath, encoding="utf-8-sig", mode="w+") as f:
            json.dump(ui, f, encoding="utf-8", indent=4, sort_keys=True)
    except Exception as err:
        Parent.Log(ScriptName, "Error saving UI file: {0}".format(err))


def LoadMessageLog():
    # save line to log file
    try:
        with codecs.open(sLogFilePath, encoding='utf-8', mode='r') as f:
            for line in f:
                # 2018-07-20 16:21:45.674000 -- reecon820: test message
                tokens = line.split(" ")
                date = " ".join(tokens[:2])
                user = tokens[3][:-1] # remove :
                message = " ".join(tokens[4:]).strip()

                sMessageLog.append({'date': date, 'user': user, 'message': message})
    except Exception as err:
        Parent.Log(ScriptName, "Error loading log file: {}".format(err))