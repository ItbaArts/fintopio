import random
import time
import sys
import re
import json
import requests
import os
import colorama
import base64
from colorama import Fore, Style
from urllib.parse import unquote, parse_qs
from datetime import datetime


api = "https://fintopio-tg.fintopio.com/api"

header = {
      "Accept": "application/json, text/plain, */*",
      "Accept-Encoding": "gzip, deflate, br",
      "Accept-Language": "en-US,en;q=0.9",
      "Referer": "https://fintopio-tg.fintopio.com/",
      "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128", "Microsoft Edge WebView2";v="128"',
      "Sec-Ch-Ua-Mobile": "?0",
      "Sec-Ch-Ua-Platform": "Windows",
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
    }

# Tambahkan konstanta warna di bagian atas file
COLORS = {
    'HEADER': '\033[95m',
    'BLUE': '\033[94m',
    'CYAN': '\033[96m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'RED': '\033[91m',
    'RESET': '\033[0m',
    'BOLD': '\033[1m'
}

def load_credentials():
    # Membaca token dari file dan mengembalikan daftar token
    try:
        with open('query.txt', 'r') as f:
            queries = [line.strip() for line in f.readlines()]
        # print("Token berhasil dimuat.")
        return queries
    except FileNotFoundError:
        print("File query.txt tidak ditemukan.")
        return 
    except Exception as e:
        print("Terjadi kesalahan saat memuat query:", str(e))
        return 

def print_(word):
    print(f"{COLORS['CYAN']}[⚔]{COLORS['RESET']} {word}")

def response_data(response):
        if response.status_code >= 500:
            print_(f"Error {response.status_code}")
            return None
        elif response.status_code >= 400:
            print_(f"Error {response.status_code}")
            return None
        elif response.status_code >= 200:
            return response.json()
        else:
            return None

def parse_query(query: str):
    try:
        parsed_query = parse_qs(query)
        parsed_query = {k: v[0] for k, v in parsed_query.items()}
        user_data = json.loads(unquote(parsed_query['user']))
        parsed_query['user'] = user_data
        return parsed_query
    except Exception as e:
        print_(f"Error {e}")

def get(id):
        tokens = json.loads(open("tokens.json").read())
        if str(id) not in tokens.keys():
            return None
        return tokens[str(id)]

def save(id, token):
        tokens = json.loads(open("tokens.json").read())
        tokens[str(id)] = token
        open("tokens.json", "w").write(json.dumps(tokens, indent=4))

def make_request(self, method, url, headers, json=None, data=None):
    retry_count = 0
    while True:
        time.sleep(2)
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, json=json)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=json, data=data)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=json, data=data)
        else:
            raise ValueError("Invalid method.")
        
        if response.status_code >= 500:
            if retry_count >= 4:
                self.print_(f"Status Code: {response.status_code} | {response.text}")
                return None
            retry_count += 1
            return None
        elif response.status_code >= 400:
            self.print_(f"Status Code: {response.status_code} | {response.text}")
            return None
        elif response.status_code >= 200:
            return response

def getdata(token):
    header['Authorization'] = f"Bearer {token}"
    response = requests.get(api+"/referrals/data", headers=header)
    data = response_data(response)
    return data

def checkin(token):
    try:
        url = api + "/daily-checkins"
        header['Authorization'] = f"Bearer {token}"
        header['Webapp'] = "true"
        response = requests.post(url, headers=header)
        data = response_data(response)
        return data
        
    except:
        print_('[checkin] failed, restarting')

def diamond(token):
    urldiamondstate = '/clicker/diamond/state'
    header['Authorization'] = f"Bearer {token}"
    header['Webapp'] = "true"
    try:
        response = requests.get(api+urldiamondstate, headers=header)
        data = response_data(response)
        return data
        

    except:
        print_('[asteroid] error restarting')
        time.sleep(5)
        main()

def start_task(token, id):
    header['Authorization'] = f"Bearer {token}"
    header['Webapp'] = "true"
    urlstart = f'/hold/tasks/{id}/start'
    response = requests.post(api+urlstart, headers=header)
    return response_data(response)

def claim_task(token, id):
    header['Authorization'] = f"Bearer {token}"
    header['Webapp'] = "true"
    urlclaim = f'/hold/tasks/{id}/claim'
    response = requests.post(api+urlclaim, headers=header)
    return response_data(response)

def printdelay(delay):
    now = datetime.now().isoformat(" ").split(".")[0]
    hours, remainder = divmod(delay, 3600)
    minutes, sec = divmod(remainder, 60)
    print(f"{COLORS['CYAN']}[{now}]{COLORS['RESET']} | {COLORS['YELLOW']}Waiting Time: {hours} hours, {minutes} minutes, and {round(sec)} seconds{COLORS['RESET']}")

def getlogin(query):
    url = api + "/auth/telegram?"
    header['Webapp'] = 'true'
    response = requests.get(url+query, headers=header)
    data = response_data(response)
    return data

def getname(queries):
    try:
        found = re.search('user=([^&]*)', queries).group(1)
        decoded = unquote(found)
        data = json.loads(decoded)
        return data
    except:
        print_('getname error')



def complete(token, id):
    url = api + "/clicker/diamond/complete"
    header['Authorization'] = f"Bearer {token}"
    payload = {"diamondNumber":id}
    response = requests.post(url, headers=header, json=payload)
    if response.status_code != 200:
        print_('asteroid failed to claim')
        return None
    else:
        return response.status_code


def getfarm(bearer):
    urlfarmstate = '/farming/state'
    try:
        response = requests.get(api+urlfarmstate, headers=header)
        data = response_data(response)
        state =  data['state']
        if state == 'idling':
            startfarm(bearer)
        elif state == 'farming':
            print_('farming not finished yet!')
        elif state == 'farmed':
            claimfarm(bearer)
        else:
            print_('[farming] error ')
    except:
        print_('[farming] error restarting')
        time.sleep(5)   

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def key_bot():
    api = base64.b64decode("aHR0cDovL2l0YmFhcnRzLmNvbS9hcGkuanNvbg==").decode('utf-8')
    try:
        response = requests.get(api)
        response.raise_for_status()
        try:
            data = response.json()
            header = data['header']
            print('\033[96m' + header + '\033[0m')
        except json.JSONDecodeError:
            print('\033[96m' + response.text + '\033[0m')
    except requests.RequestException as e:
        print('\033[96m' + f"Failed to load header: {e}" + '\033[0m')
def startfarm(token):
    try:
        url = api + "/farming/farm"
        header['Authorization'] = f"Bearer {token}"
        header['Webapp'] = "true"
        response = requests.post(url, headers=header)
        if response.status_code == 200:
            print_('farming started!')
    except:
        print_('[farming] failed to start')

def claimfarm(token):
    try:
        url = api + "/farming/claim"
        header['Authorization'] = f"Bearer {token}"
        header['Webapp'] = "true"
        response = requests.post(url, headers=header)
        if response.status_code == 200:
            print_('farming claimed!')
            time.sleep(2)
            startfarm(token)
    except:
        print_('[farming] failed to claim')

def play_game(token, score):
    try:
        url = api + '/hold/space-tappers/add-new-result'
        payload = {"score": score}
        header['Authorization'] = f"Bearer {token}"
        header['Webapp'] = "true"
        response = requests.post(url, headers=header, json=payload)
        if response.status_code == 201:
            jsons = response.json()
            actualReward = jsons.get('actualReward',0)
            print_(f"Play game done, reward : {actualReward*10}")
    except:
        print_('[farming] failed to playing game')

def gettask(token):
    try:
        urltasks = api + "/hold/tasks"
        header['Authorization'] = f"Bearer {token}"
        header['Webapp'] = "true"
        response = requests.get(urltasks, headers=header)
        data = response_data(response)
        return data
    except Exception as e:
        print_('[gettask] failed, restarting')

def init(token):
    url = 'https://fintopio-tg.fintopio.com/api/hold/fast/init'
    header['Authorization'] = f"Bearer {token}"
    header['Webapp'] = "true"
    response = requests.get(url, headers=header)
    data = response_data(response)
    return data

def main():
    print(f"\n{COLORS['BOLD']}{COLORS['HEADER']}╔══════════════════════════════════════╗{COLORS['RESET']}")
    print(f"{COLORS['BOLD']}{COLORS['HEADER']}║        FINTOPIO AUTO FARMING BOT     ║{COLORS['RESET']}")
    print(f"{COLORS['BOLD']}{COLORS['HEADER']}╚══════════════════════════════════════╝{COLORS['RESET']}\n")
    
    status_task = input(f"{COLORS['CYAN']}[?]{COLORS['RESET']} Clear task (y/n)? ").strip().lower()
    selector_game = input(f"{COLORS['CYAN']}[?]{COLORS['RESET']} Auto play game (y/n)? ").strip().lower()
    clear()
    key_bot()

    while True:
        delay = 1 * random.randint(3600, 3700)
        queries = load_credentials()
        start_time = time.time()
        total_point = 0
        sum = len(queries)
        for index, query in enumerate(queries, start=1):
            # Dapatkan data user terlebih dahulu
            user = parse_query(query).get('user')
            
            print(f"\n{COLORS['BOLD']}{COLORS['GREEN']}{'═' * 50}{COLORS['RESET']}")
            print(f"{COLORS['BOLD']}{COLORS['BLUE']}✦ Account {index} | {user.get('username')} ✦{COLORS['RESET']}")
            print(f"{COLORS['BOLD']}{COLORS['GREEN']}{'═' * 50}{COLORS['RESET']}\n")
            
            token = get(user.get('id'))
            print_(f"===== Account {index} | {user.get('username')} =====")
            if token == None:
                token = getlogin(query).get('token')
                save(user.get('id'), token)
                time.sleep(2)
            data = getdata(token)
            if data is not None:
                data_init = init(token)
                if data_init is not None:
                    referralData = data_init.get('referralData',{})
                    balance = referralData.get('balance','0')
                    print_(f"{COLORS['GREEN']}Balance : {balance} points{COLORS['RESET']}")
                    total_point += float(balance)
                isDailyRewardClaimed = data.get('isDailyRewardClaimed', True)
                if isDailyRewardClaimed:
                    print_(f"User {user.get('username')} has already claimed today's reward.")
                else:
                    data_checkin = checkin(token)
                    if data_checkin is not None:
                        print_('reward daily    : ' + str(data_checkin['dailyReward']))
                        print_('total login day :' + str(data_checkin['totalDays']))
                        print_('daily reward claimed!')
            time.sleep(2)
            getfarm(token)
            time.sleep(2)
            data_diamond = diamond(token)
            if data_diamond is not None:
                jsonsettings =  data_diamond['settings']
                jsonstate =  data_diamond['state']
                jsondiamondid =  data_diamond['diamondNumber']
                jsontotalreward =  jsonsettings['totalReward']
                if jsonstate == 'available':
                    time.sleep(2)
                    data_complete = complete(token, jsondiamondid)
                    if data_complete is not None:
                        print_('reward diamond   : ' + str(jsontotalreward))
                elif jsonstate == 'unavailable':
                    print_('asteroid unavailable yet!')
                else:
                    print_('asteroid crushed! waiting next round..')
            print_("--- TASK ---")
            if status_task == 'y':
                data_task = gettask(token)
                if data_task is not None:
                    task_list = data_task.get('tasks', [])
                    for item in task_list: 
                        if item['status'] == 'available':
                            id = item.get('id')
                            slug = item.get('slug')                          
                            print_(f'task {slug} started!')
                            data_task = start_task(token, id)
                            time.sleep(2)
                            if data_task is not None:
                                print_(f"task {slug} {data_task.get('status')}")
                        elif item['status'] == 'verified':
                            id = item.get('id')
                            slug = item.get('slug') 
                            rewardAmount = item.get('rewardAmount')
                            data_task = claim_task(token, id)
                            time.sleep(2)
                            if data_task is not None:
                                if data_task.get('status') == 'completed':
                                    print_(f"task {slug} done, reward {rewardAmount} points")
            if selector_game =='y':
                print_(f"\n{COLORS['YELLOW']}▶ Starting Game Session ◀{COLORS['RESET']}")
                loops = random.randint(5, 10)
                score = random.randint(900, 1000)

                for i in range(loops):
                    print_(f"{COLORS['CYAN']}➤ Playing Game {i+1}/{loops}{COLORS['RESET']}")
                    times = random.randint(30,35)
                    time.sleep(times)
                    play_game(token, score)

        print(f"\n{COLORS['BOLD']}{COLORS['HEADER']}╔══════════════════════════════════════╗{COLORS['RESET']}")
        print(f"{COLORS['BOLD']}{COLORS['HEADER']}║            SUMMARY REPORT            ║{COLORS['RESET']}")
        print(f"{COLORS['BOLD']}{COLORS['HEADER']}╚══════════════════════════════════════╝{COLORS['RESET']}")
        print_(f"{COLORS['GREEN']}Total Users : {sum} | Total Points : {round(total_point)}{COLORS['RESET']}")
        print(f"{COLORS['BOLD']}{COLORS['GREEN']}{'═' * 50}{COLORS['RESET']}\n")
        end_time = time.time()
        total_time = delay - (end_time-start_time)
        if total_time >= 0:
            printdelay(total_time)
            time.sleep(total_time)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()


