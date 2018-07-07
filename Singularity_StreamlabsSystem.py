#---------------------------
#   Import Libraries
#---------------------------
import os
import codecs
import sys
import json
sys.path.append(os.path.join(os.path.dirname(__file__), "lib")) #point at lib folder for classes / references

import clr
clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")
clr.AddReference('System.Speech')
from System.Speech.Synthesis import SpeechSynthesizer


#   Import your Settings class
from Settings_Module import MySettings
#---------------------------
#   [Required] Script Information
#---------------------------
ScriptName = "Singularity"
Website = "reecon820@gmail.com"
Description = "Lets people whisper the bot for TTS"
Creator = "Reecon820"
Version = "1.0.0.0"

#---------------------------
#   Define Global Variables
#---------------------------
global SettingsFile
SettingsFile = ""
global ScriptSettings
ScriptSettings = MySettings()
global speak
speak = SpeechSynthesizer()

#---------------------------
#   [Required] Initialize Data (Only called on load)
#---------------------------
def Init():

    #   Create Settings Directory
    directory = os.path.join(os.path.dirname(__file__), "Settings")
    if not os.path.exists(directory):
        os.makedirs(directory)

    #   Load settings
    global SettingsFile
    SettingsFile = os.path.join(os.path.dirname(__file__), "Settings\settings.json")

    global ScriptSettings
    ScriptSettings = MySettings(SettingsFile)

    speak.Volume = ScriptSettings.Volume
    speak.SelectVoice(ScriptSettings.Voice)

    # querry installed voices and update ui file
    voices = speak.GetInstalledVoices()
    names = [voice.VoiceInfo.Name for voice in voices]

    ui = {}
    UiFilePath = os.path.join(os.path.dirname(__file__), "UI_Config.json")
    try:
        with codecs.open(UiFilePath, encoding="utf-8-sig", mode="r") as f:
            ui = json.load(f, encoding="utf-8")
    except Exception as err:
        Parent.Log(ScriptName, "{0}".format(err))

    if not ui['Voice']['value']:
        ui['Voice']['value'] = names[0]

    ui['Voice']['value'] = ScriptSettings.Voice
    ui['Voice']['items'] = names
    # update ui with loaded settings
    ui['Volume']['value'] = ScriptSettings.Volume
    ui['Command']['value'] = ScriptSettings.Command
    ui['Cooldown']['value'] = ScriptSettings.Cooldown
    ui['Permission']['value'] = ScriptSettings.Permission
    ui['Info']['value'] = ScriptSettings.Info

    try:
        with codecs.open(UiFilePath, encoding="utf-8-sig", mode="w+") as f:
            json.dump(ui, f, encoding="utf-8", indent=4, sort_keys=True)
    except Exception as err:
        Parent.Log(ScriptName, "{0}".format(err))

    return

#---------------------------
#   [Required] Execute Data / Process messages
#---------------------------
def Execute(data):
    #   Check if the propper command is used, the command is not on cooldown and the user has permission to use the command
    if data.IsWhisper() and data.IsFromTwitch() and data.GetParam(0).lower() == ScriptSettings.Command and not Parent.IsOnCooldown(ScriptName, ScriptSettings.Command) and Parent.HasPermission(data.User, ScriptSettings.Permission, ScriptSettings.Info):
        #   remove command from message
        text = data.Message[len(ScriptSettings.Command):].strip()
        speak.Speak(text) # do the thing
        Parent.AddCooldown(ScriptName, ScriptSettings.Command, ScriptSettings.Cooldown)  # Put the command on cooldown

    return

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
    ScriptSettings.__dict__ = json.loads(jsonData)
    ScriptSettings.Save(SettingsFile)
    # Don't forget to set the values to the things
    speak.Volume = ScriptSettings.Volume
    speak.SelectVoice(ScriptSettings.Voice)
    return

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
