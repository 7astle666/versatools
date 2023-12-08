import os
import sys
# pylint: disable=unused-import
from tools import ProxyChecker,CookieGenerator,CookieRefresher,CookieChecker,CookieVerifier,TShirtGenerator,MessageBot,FriendRequestBot,StatusChanger,FollowBot,GameVote,FavoriteBot,DisplayNameChanger,SolverBalanceChecker,GroupJoinBot,AssetsDownloader,CommentBot,Gen2018Acc,ModelSales,AssetsUploader,ModelVote,AdsScraper,ProxyScraper,GameVisits,DiscordRpc,ItemBuyer,ReportBot,UP2UPC
from Tool import Tool
from utils import Utils
import json
from data.config import config
from data.version import version
import eel
import time
from watchdog.observers import Observer
from threading import Thread
from FilesChangeHandler import FilesChangeHandler
import traceback
import httpx
import subprocess

@eel.expose
def get_tools_info():
    """
    Returns info about tools
    """
    app = App()
    tools = [{"name": tool.name, "color": tool.color, "description": tool.description} for tool in app.tools]
    sorted_tools = sorted(tools, key=lambda x: x["name"])

    return sorted_tools

@eel.expose
def show_menu():
    """
    Show menu in terminal
    """
    eel.clear_terminal()
    eel.write_terminal("\x1B[1;32mWelcome to Versatools\x1B[0;0m")
    eel.write_terminal("Best FREE opensource Roblox botting tools written in Python\n")
    eel.write_terminal("\x1B[1;31mOur tools:\x1B[0;0m")

    tools = get_tools_info()

    for i, tool in enumerate(tools):
        eel.write_terminal(f"\x1B[1;3{tool['color']}m   {str(i + 1)}. {tool['name']}\x1B[0;0m")
        eel.write_terminal(f"\x1B[1;3{tool['color']}m      {tool['description']}\x1B[0;0m")

class App():
    def __init__(self):
        self.cache_directory = os.path.join(os.path.dirname(__file__), "../.versacache")
        self.files_directory = os.path.join(os.path.dirname(__file__), "../files")
        self.proxies_file_path = os.path.join(self.files_directory, "proxies.txt")
        self.cookies_file_path = os.path.join(self.files_directory, "cookies.txt")
        self.config_file_path = os.path.join(self.files_directory, "config.json")

        self.current_tool = None
        self.selected_tool = None
        self.proxies_loaded = None
        self.cookies_loaded = None

        Utils.ensure_directories_exist([self.cache_directory, self.files_directory])
        Utils.ensure_files_exist([self.proxies_file_path, self.cookies_file_path])

        self.ensure_config_file()
        self.tools = [t(self) for t in Tool.__subclasses__()]

        self.start_watching_files() # used for syncing config changes with UI

    @staticmethod
    def check_update():
        """
        Checks if update is available
        """
        res = httpx.get("https://garry.lol/versatools/uploads/version.txt")

        if res.status_code != 200:
            return False

        return res.text != version

    def update_versatools(self):
        try:
            download_url = 'https://garry.lol/versatools/uploads/versatools-setup.exe'
            installable_path = os.path.join(self.cache_directory, "./versatools-setup.exe")

            response = httpx.get(download_url, follow_redirects=True)
            open(installable_path, "wb").write(response.content)

            subprocess.run([installable_path, '/verysilent'], check=True)
        except Exception as err:
            return str(err)

        return True

    def restart_versatools(self):
        try:
            os.execl(sys.executable, sys.executable, *sys.argv)
        except Exception as err:
            return str(err)

    def launch_tool(self, tool_name):
        """
        Launches a tool from its name
        """
        tool = self.get_tool_from_name(tool_name)
        if tool is None:
            raise Exception("Tool not found")

        self.current_tool = tool
        tool.exit_flag = False

        try:
            tool.run()
        except KeyboardInterrupt:
            return
        except Exception as err:
            traceback_str = traceback.format_exc()
            eel.write_terminal(traceback_str)
            eel.write_terminal(f"\x1B[1;31m{str(err)}\x1B[0;0m")

        eel.tool_finished()

    def get_tool_from_name(self, tool_name):
        """
        Returns the tool from its name
        """
        tool = next((t for t in self.tools if t.name == tool_name), None)

        if tool is None:
            raise Exception("Tool not found")

        return tool

    def get_tool_config(self, tool_name):
        """
        Returns the config of a tool from name
        """
        tool = self.get_tool_from_name(tool_name)
        self.selected_tool = tool

        return tool.config

    def ensure_config_file(self):
        """
        Ensure config file exists and is valid
        """
        config_file_path = os.path.join(self.files_directory, "config.json")
        # make sure config file exists
        if not os.path.exists(config_file_path):
            with open(config_file_path, "w") as json_file:
                ordered_config = dict(sorted(config.items(), key=lambda x: x[0]))
                json.dump(ordered_config, json_file, indent=4)
        else:
            # make sure config file contains all keys
            with open(config_file_path, "r+") as json_file:
                file_config = json.load(json_file)
                for key in config:
                    if key not in file_config:
                        file_config[key] = config[key]
                    else:
                        for subkey in config[key]:
                            if subkey not in file_config[key]:
                                file_config[key][subkey] = config[key][subkey]

                            # make sure subkeys starting with // are not overwritten
                            if subkey.startswith("//"):
                                file_config[key][subkey] = config[key][subkey]
                ordered_config = dict(sorted(file_config.items(), key=lambda x: x[0]))
                json_file.seek(0)
                json_file.truncate()
                json.dump(ordered_config, json_file, indent=4)

    def set_tool_config(self, tool_name, tool_config):
        """
        Changes the config of a tool in config.json and in its instance
        """
        tool = self.get_tool_from_name(tool_name)

        # update config
        tool.config = tool_config

        # update config file
        with open(self.config_file_path, "r+") as json_file:
            file_config = json.load(json_file)
            file_config[tool.name.replace(" ", "")] = tool.config
            ordered_config = dict(sorted(file_config.items(), key=lambda x: x[0]))
            json_file.seek(0)
            json_file.truncate()
            json.dump(ordered_config, json_file, indent=4)

    def set_tool_config_ui(self):
        if self.selected_tool is None:
            return

        old_config = str(self.selected_tool.config)
        try:
            new_config = self.selected_tool.load_config()
            if old_config != str(new_config):
                eel.set_ui_tool_config(new_config)()
        except ValueError:
            pass

    def set_proxies_loaded(self):
        try:
            f = open(self.proxies_file_path, 'r')
        except FileNotFoundError:
            amount = 0

        proxies_list = f.readlines()
        proxies_list = [*set(proxies_list)] # remove duplicates
        amount = len(proxies_list)

        if amount == self.proxies_loaded:
            return

        self.proxies_loaded = amount
        eel.set_proxies_loaded(amount)

    def set_cookies_loaded(self):
        amount = len(self.tools[0].get_cookies(ignore_zero_cookie=True))

        if amount == self.cookies_loaded:
            return

        self.cookies_loaded = amount
        eel.set_cookies_loaded(amount)

    def start_watching_files(self):
        thread = Thread(target = self.watch_files_changes)
        thread.daemon = True
        thread.start()

    def watch_files_changes(self):
        path = self.files_directory
        event_handler = FilesChangeHandler(self)

        observer = Observer()
        observer.schedule(event_handler, path, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        finally:
            observer.stop()
            observer.join()

    def __str__(self) -> str:
        return "Versatools main class"
