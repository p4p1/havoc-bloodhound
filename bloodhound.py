#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Made by papi
# Created on: Tue 02 Jan 2024 01:27:42 PM CET
# bloodhound.py
# Description:
#  a havocui script to link bloodhound CE with havoc
# Functionality of this script
#  1. Settings for bloodhound API -> done
#  2. Settings for SharpHound command -> done
#  3. Tree view for domain information.
#  4. Function to run collector -> done
#  5. Function to downlaod and upload data. -> done

import havoc, havocui
import hmac, hashlib, datetime, requests, base64
import zipfile
import os, json

bloodhound_current_dir = os.getcwd()
bloodhound_install_path = "/data/extensions/havoc-bloodhound/"

while not os.path.exists(bloodhound_current_dir + bloodhound_install_path):
    # not installed through havoc-store so prompt for the path
    bloodhound_install_path = ""
    havocui.inputdialog("Install path", "Please enter your install path here for the module to work correctly:")

# Global variables
search_dialog = havocui.Dialog("Search", True, 600, 150)
bloodhound_settings_pane = havocui.Widget("BloodHound Settings", True)
sharphound_settings_pane = havocui.Widget("SharpHound Settings", True)
bloodhound_log_panel = havocui.Logger("BloodHound Logs")
bh_conf_path = bloodhound_current_dir + bloodhound_install_path + "settings.json"
search_value = ""
settings_bloodhound = {
    "server_url": "http://localhost:8080",
    "api-key": "Enter key here",
    "api-id": "Enter id here",
    "sharphound_path": os.path.join(bloodhound_current_dir, bloodhound_install_path, "SharpHound.exe"),
    "sharphound": {
        "args": False,
        "domain": "template.domain",
        "search_forest": False,
    }
}

# Thank you stack overflow
def is_website_online(url):
    try:
        response = requests.head(url)
    except Exception as e:
        return False
    else:
        return True
    return False

def unzip_folder(zip_file_path, extract_to):
    extracted_paths = []
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        for member in zip_ref.namelist():
            zip_ref.extract(member, extract_to)
            extracted_paths.append(os.path.join(extract_to, member))
    return extracted_paths

# Manipulate the API through this function
def call_api(method, uri, body=None):
    # Function taken from:
    # https://support.bloodhoundenterprise.io/hc/en-us/articles/11311053342619-Working-with-the-BloodHound-API
    digester = hmac.new(settings_bloodhound["api-key"].encode(), None, hashlib.sha256)
    digester.update(f"{method}{uri}".encode())
    digester = hmac.new(digester.digest(), None, hashlib.sha256)
    datetime_formatted = datetime.datetime.now().astimezone().isoformat("T")
    digester.update(datetime_formatted[:13].encode())
    digester = hmac.new(digester.digest(), None, hashlib.sha256)
    if body is not None:
        digester.update(body.encode())
    return requests.request(
        method=method,
        url=settings_bloodhound["server_url"]+uri,
        headers={
            "User-Agent": "bh-havoc-client",
            "Authorization": "bhesignature %s" % settings_bloodhound["api-id"],
            "RequestDate": datetime_formatted,
            "Signature": base64.b64encode(digester.digest()),
            "Content-Type": "application/json",
        },
        data=body,
    )

# Function to build the sharphound command
def build_sharphound_command():
    global settings_bloodhound
    cmd = "dotnet inline-execute " + settings_bloodhound["sharphound_path"]
    if settings_bloodhound["sharphound"]["args"]:
        if settings_bloodhound["sharphound"]["domain"] != "template.domain":
            cmd += "--domain %s " % settings_bloodhound["sharphound"]["domain"]
        if settings_bloodhound["sharphound"]["search_forest"] == True:
            cmd += "--searchforest "
    return cmd

# save the settings
def save_settings():
    global settings_bloodhound
    global bh_conf_path
    with open(bh_conf_path, "w") as fp:
        # save the config
        json.dump(settings_bloodhound, fp)

# Capture the data for the bloodhound settings panel
def get_server_url(text):
    global settings_bloodhound
    settings_bloodhound["server_url"] = text
def get_api_key(text):
    global settings_bloodhound
    settings_bloodhound["api-key"] = text
def get_api_id(text):
    global settings_bloodhound
    settings_bloodhound["api-id"] = text
# the actual bloodhound settings panel
def open_bloodhound_settings():
    global settings_bloodhound
    bloodhound_settings_pane.clear()
    bloodhound_settings_pane.addLabel("<h3 style='color:#bd93f9'>BloodHound Status:</h3>")
    if is_website_online(settings_bloodhound["server_url"]):
        bloodhound_settings_pane.addLabel("status: <span style='color:#00ff00'>online</span>")
    else:
        bloodhound_settings_pane.addLabel("status: <span style='color:#ff6347'>offline</span>")
    bloodhound_settings_pane.addLabel("<h3 style='color:#bd93f9'>BloodHound Settings:</h3>")
    bloodhound_settings_pane.addLabel("<span style='color:#71e0cb'>BloodHound URL:</span>")
    bloodhound_settings_pane.addLineedit(settings_bloodhound["server_url"], get_server_url)
    bloodhound_settings_pane.addLabel("<span style='color:#71e0cb'>API key:</span>")
    bloodhound_settings_pane.addLineedit(settings_bloodhound["api-key"], get_api_key)
    bloodhound_settings_pane.addLabel("<span style='color:#71e0cb'>API id:</span>")
    bloodhound_settings_pane.addLineedit(settings_bloodhound["api-id"], get_api_id)
    bloodhound_settings_pane.addButton("Save", save_settings)
    bloodhound_settings_pane.setSmallTab()

# Capture the sharphound arguments data
def get_arguments():
    global settings_bloodhound
    settings_bloodhound["sharphound"]["args"] = not settings_bloodhound["sharphound"]["args"]
def get_domain_sh(text):
    global settings_bloodhound
    settings_bloodhound["sharphound"]["domain"] = text
def get_search_forest():
    global settings_bloodhound
    settings_bloodhound["sharphound"]["search_forest"] = not settings_bloodhound["sharphound"]["search_forest"]
def change_sharphound_path():
    global settings_bloodhound
    new_path = havocui.openfiledialog("select file").decode('ascii')
    old_path = ""
    if os.path.exists(settings_bloodhound["sharphound_path"]):
        old_path = "<span style='color:#00ff00'>%s</span>" % settings_bloodhound["sharphound_path"]
    else:
        old_path = "<span style='color:#ff6347'>%s</span>" % settings_bloodhound["sharphound_path"]
    sharphound_settings_pane.replaceLabel(old_path, "<span style='color:#ffa07a'>%s</span>" % new_path)
    settings_bloodhound["sharphound_path"] = new_path
# the actual sharphound settings panel
def open_sharphound_settings():
    global settings_bloodhound
    sharphound_settings_pane.clear()
    sharphound_settings_pane.addLabel("<h3 style='color:#bd93f9'>Sharphound path:</h3>")
    if os.path.exists(settings_bloodhound["sharphound_path"]):
        sharphound_settings_pane.addLabel("<span style='color:#00ff00'>%s</span>" % settings_bloodhound["sharphound_path"])
    else:
        sharphound_settings_pane.addLabel("<span style='color:#ff6347'>%s</span>" % settings_bloodhound["sharphound_path"])
    sharphound_settings_pane.addButton("Change", change_sharphound_path)
    sharphound_settings_pane.addLabel("<h3 style='color:#bd93f9'>Sharphound settings:</h3>")
    sharphound_settings_pane.addCheckbox("Activate optional arguments", get_arguments, settings_bloodhound["sharphound"]["args"])
    sharphound_settings_pane.addLineedit(settings_bloodhound["sharphound"]["domain"], get_domain_sh)
    sharphound_settings_pane.addCheckbox("Search Forests", get_search_forest, settings_bloodhound["sharphound"]["search_forest"])
    sharphound_settings_pane.addButton("Save", save_settings)
    sharphound_settings_pane.setSmallTab()

# The function for the log pannel
def open_logs():
    data = call_api("GET", "/api/v2/audit")
    if data.status_code == 200:
        bloodhound_log_panel.clear()
        parsed_data = data.json()
        for entry in parsed_data["data"]["logs"]:
            bloodhound_log_panel.addText("[<span style='color:#71e0cb'>%s</span>] by <span style='color:#ff6347'>%s</span> -> %s" % (entry["created_at"], entry["actor_name"], entry["action"]))
        bloodhound_log_panel.setBottomTab()

search_result_values = {}
def search_handler(selected):
    return selected
search_result = havocui.Tree("Search Result", search_handler)
def get_search_value(text):
    global search_value
    search_value = text
def run_search():
    search_dialog.close()
    global search_value
    global search_result_values
    unique_types = []
    data = call_api("GET", "/api/v2/search?q=%s" % search_value)
    if data.status_code == 200:
        search_result.addRow("------Results for %s-----" % search_value)
        data = data.json()
        unique_types = list({item["type"] for item in data["data"]})
        for value in unique_types:
            matching_elements = [item["name"] for item in data['data'] if item['type'] == value]
            search_result_values[value] = matching_elements
            search_result.addRow(value, *matching_elements)
        search_result.setBottomTab()
# The widget for opening search
def open_search():
    search_dialog.clear()
    search_dialog.addLabel("<h2 style='color:#bd93f9'>Search for an element:</h2>")
    search_dialog.addLineedit("Type in the name of an element..", get_search_value)
    search_dialog.addButton("Search", run_search)
    search_dialog.exec()

# A function that will display information about comupters, users and gpos to be coded in the future
def open_inspect():
    data = call_api("GET", "/api/v2/available-domains")
    print(data)
    print(data.json())
    data = call_api("GET", "/api/v2/domains/%s" % data.json()['data'][0]['id'])
    print(data)
    print(data.json())
    print("why...")

# The two command line functions
def run_collector(demonID, *param):
    if not os.path.exists(settings_bloodhound["sharphound_path"]):
        havocui.errormessage("the provided path for sharphound is wrong please navigate to the sharphound settings and select the appropriate binary...")
        return None
    demon = havoc.Demon(demonID)
    TaskID = demon.ConsoleWrite(demon.CONSOLE_TASK, "Executing collector...")
    demon.Command(TaskID, build_sharphound_command())
    return TaskID

def upload_collected(demonID, *param):
    demon = havoc.Demon(demonID)
    path_to_zip = bloodhound_current_dir + "/" + param[0] + "/Download/" + param[1].replace("\\", "/")
    if not os.path.exists(bloodhound_current_dir + "/" + param[0] + "/Download/" + param[1].replace("\\", "/")):
        TaskID = demon.ConsoleWrite(demon.CONSOLE_ERROR, "Could not find provided file")
        return TaskID
    demon.ConsoleWrite(demon.CONSOLE_INFO, "unzipping: %s" % path_to_zip)
    files = unzip_folder(path_to_zip, "/tmp/bloodhound-havoc/")
    for file in files:
        demon.ConsoleWrite(demon.CONSOLE_INFO, "uploading: %s" % file)
        reqres = call_api("POST", "/api/v2/file-upload/start")
        if reqres.status_code != 201:
            demon.ConsoleWrite(demon.CONSOLE_ERROR, "Error during task creation on the api-end!")
            return None
        data = reqres.json()
        with open(file, "r") as fp:
            content = fp.read()
            a = call_api("POST", "/api/v2/file-upload/%s" % data['data']['id'], content)
        if a.status_code != 202:
            demon.ConsoleWrite(demon.CONSOLE_ERROR, "Error during upload!")
            return None
        a = call_api("POST", "/api/v2/file-upload/%s/end" % data['data']['id'])
    demon.ConsoleWrite(demon.CONSOLE_INFO, "Completed the script correctly")
    return None

# Handle the settings of the tool load / save
if os.path.exists(bh_conf_path):
    # find the settings path
    with open(bh_conf_path, "r") as fp:
        # load the settings
        settings_bloodhound = json.load(fp)
else:
    save_settings()

havoc.RegisterModule("bloodhound","A command to manage bloodhound related things","","","","")
havoc.RegisterCommand( run_collector, "bloodhound", "collect", "Run the Bloodhound collector on the target machine (aka: SharpHound)", 0, "", "" )
havoc.RegisterCommand( upload_collected, "bloodhound", "upload", "Upload the zip file to the api", 0, "[local_download_path] [remote_zip_file_path]", "/data/ c:\\file\\number_BloodHound.zip" )
havocui.createtab("Bloodhound", "Search", open_search, "SharpHound", open_sharphound_settings, "Logs", open_logs, "Settings", open_bloodhound_settings)
