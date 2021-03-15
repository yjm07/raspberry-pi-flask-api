import subprocess
from time import sleep


ssid_list = set()   # ssid list that have been connected once
wpa_supplicant = '/etc/wpa_supplicant/wpa_supplicant.conf'
user_directory = './temp.conf'
origin_user_directory = './temp_origin.conf'


def connect(ssid, psw, auto_reconnect):
    """
    Main method for connecting wifi.
    Input: {'ssid': string, 'password': string, 'auto_reconnect': boolean}
    """
    # If already known, use wpa_cli
    if is_known_wifi(ssid):
        id = id_wpa_cli(ssid)
        connect_wpa_cli(id)
    # Write to temp_wpa_supplicant.conf and check if psw is right
    else:
        write_wpa_supplicant(ssid, psw, user_directory)
        reconnect_wpa_supplicant(user_directory)

        psw_right = is_psk_right()
        # If psw is right, add ssid to list and write to wpa_supplicant.conf
        if psw_right == 'connected':
            ssid_list.add(ssid)
            write_wpa_supplicant(ssid, psw, wpa_supplicant)
            reconnect_wpa_supplicant(wpa_supplicant)
            # Set priority of newly added ssid
            id = id_wpa_cli(ssid)
            set_priority(id, id)
            print("connected")
        # If psw is wrong, just reconnect to wpa_supplicant.conf
        else:
            print("wrong psw")
            reconnect_wpa_supplicant(wpa_supplicant)
        flush(user_directory)

    print("done")
    return


    # if auto_reconnect:
        # ssid_list.remove(ssid)
        # remove_wpa_cli(id)
    # else:

# Check ssid list if already known
def is_known_wifi(ssid):
    return ssid in ssid_list

# Flush temp_wpa_supplicant.conf back to the state before
def flush(dir):
    subprocess.call(['sudo', 'cp', origin_user_directory, dir])

# Reconfigure wpa_cli to update wpa_supplicant.conf and check psk
def is_psk_right():
    subprocess.call('wpa_cli reconfigure > /dev/null', shell=True)
    sleep(1)
    proc = subprocess.Popen(['./wpa.sh'],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()

    if stderr != b'':
        print(stderr.decode())
    else:
        print('output')
        return stdout.decode().rstrip()

# Connect to network of the id with wpa_cli
def connect_wpa_cli(id):
    subprocess.call(['wpa_cli', '-i', 'wlan0', 'select_network', id])

# Remove id from wpa_cli list
def remove_wpa_cli(id):
    subprocess.call(['wpa_cli', '-i', 'wlan0', 'remove_network', id])

# Return id of the ssid from wpa_cli list
def id_wpa_cli(ssid):
    proc = subprocess.Popen(f'wpa_cli -i wlan0 list_networks | grep {ssid}',
                            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    output = stdout.decode()

    if stderr != b'':
        print(stderr.decode())
    if len(stdout) == 0:
        return -1
    return output.split()[0]

# Kill and reconnect wpa_supplicant
def reconnect_wpa_supplicant(dir):
    MyOut1 = subprocess.Popen(['sudo', 'killall', 'wpa_supplicant'])
    MyOut1.wait()
    sleep(1)
    print('kill all wpa_supplicant end')

    MyOut2 = subprocess.Popen(['sudo', 'wpa_supplicant','-B', '-iwlan0', '-c', dir, '-f/var/log/wpa_supplicant.log'])
    MyOut2.wait()
    sleep(1)
    print('wpa_supplicant setup end')

    print('reconnect end')

# Write ssid and password to wpa_supplicant.conf of the directory
def write_wpa_supplicant(ssid, psw, dir):
    proc = subprocess.Popen(f"wpa_passphrase '{ssid}' {psw} | sudo tee -a {dir}", 
                            shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout,stderr = proc.communicate()
    print('write wpa end')

# Set the priority of the id in wpa_cli list
def set_priority(id, priority):
    subprocess.call(['wpa_cli', '-i', 'wlan0', 'set_network', id, 'priority', priority])
    sleep(1)
    subprocess.call(['wpa_cli', '-i', 'wlan0', 'save_config'])
    sleep(1)


