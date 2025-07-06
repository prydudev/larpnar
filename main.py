import os, json, random, string, datetime, requests
from colorama import init, Fore, Style
init(autoreset=True)

SUCCESS, ERROR, WHITE, INFO, RESET = '\033[38;2;0;255;100m', '\033[38;2;255;50;50m', '\033[38;2;255;255;255m', '\033[38;2;80;180;255m', Style.RESET_ALL

def get_accounts_path():
    return os.path.join(os.path.expanduser('~'), '.lunarclient', 'settings', 'game', 'accounts.json')

def load_accounts():
    with open(get_accounts_path(), 'r', encoding='utf-8') as f: return json.load(f)

def save_accounts(data):
    with open(get_accounts_path(), 'w', encoding='utf-8') as f: json.dump(data, f, indent=2)
    
def random_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))

def get_minecraft_profile(username):
    r = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{username}')
    return r.json() if r.status_code == 200 else None

def list_accounts(data):
    return [(i+1, k, v.get('username', 'Unknown'), 'refreshToken' in v) for i, (k, v) in enumerate(data.get('accounts', {}).items())]

def delete_account(data, local_id):
    accs = data.get('accounts', {})
    if local_id in accs:
        del accs[local_id]
        if data.get('activeAccountLocalId') == local_id:
            data['activeAccountLocalId'] = next(iter(accs), '')
    return data

def create_account(data, username):
    p = get_minecraft_profile(username)
    if not p: return False
    local_id = random_id()
    expires = (datetime.datetime.utcnow() + datetime.timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    acc = {"accessToken": local_id, "accessTokenExpiresAt": expires, "eligibleForMigration": False, "hasMultipleProfiles": False, "legacy": False, "persistent": True, "localId": local_id, "minecraftProfile": {"id": p['id'], "name": username}, "remoteId": username, "type": "Xbox", "username": username}
    data['accounts'][local_id] = acc
    return True

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    while True:
        data = load_accounts(); accs = list_accounts(data); clear_screen()
        [print(f'{WHITE}[{INFO}{i}{WHITE}] {name}') for i, k, name, is_real in accs]
        add_num, del_num = len(accs)+1, len(accs)+2
        print(f'{WHITE}[{INFO}{add_num}{WHITE}] {SUCCESS}Add new account')
        print(f'{WHITE}[{INFO}{del_num}{WHITE}] {ERROR}Remove an account')
        try:
            choice = int(input(f'\n{WHITE}→ '))
            if choice == add_num:
                username = input(f'{INFO}> Enter the new Minecraft name: ')
                print(f'{SUCCESS}Account created.' if create_account(data, username) and not save_accounts(data) else f'{ERROR}Failed to fetch Minecraft profile.')
                input(f'{INFO}Press Enter to continue...')
            elif choice == del_num:
                try:
                    num = int(input(f'{INFO}> Enter account number to remove: '))
                    if 1 <= num <= len(accs):
                        local_id, username, is_real = accs[num-1][1], accs[num-1][2], accs[num-1][3]
                        if is_real and input(f'{ERROR}Are you sure you want to delete {username}? {WHITE}(y/n): ').lower() != 'y':
                            print(f'{ERROR}Deletion cancelled.'); input(f'{WHITE}Press Enter to continue...'); continue
                        delete_account(data, local_id); save_accounts(data); print(f'{SUCCESS}Account deleted.')
                    else: print(f'{ERROR}Invalid number.')
                except: print(f'{ERROR}Invalid input.')
                input(f'{INFO}Press Enter to continue...')
            elif 1 <= choice <= len(accs): pass
            else:
                print(f'{ERROR}Invalid option.'); input(f'{INFO}Press Enter to continue...')
        except: print(f'{ERROR}Invalid input.'); input(f'{INFO}Press Enter to continue...')

if __name__ == '__main__': main()
