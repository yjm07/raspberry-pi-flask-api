import subprocess
from time import sleep


ssid_list = set()
wpa_supplicant = '/etc/wpa_supplicant/wpa_supplicant.conf'
user_directory = './temp.conf'
origin_user_directory = './temp_origin.conf'


def is_known_wifi(ssid):
    return ssid in ssid_list


def connect(ssid, psk, auto_reconnect):
    if is_known_wifi(ssid):
        id = id_wpa_cli(ssid)
        connect_wpa_cli(id)
    else:
        write_temp_wpa_supplicant(ssid, psk)
        reconnect_wpa_supplicant(user_directory)
        psk_right = is_psk_right()
        if psk_right == 'connected':
            ssid_list.add(ssid)
            write_wpa_supplicant(ssid, psk)
            print("connected!")
        else:
            print("wrong psw")
        flush(user_directory)
    print("done")
    return


def flush(dir):
    subprocess.call(['sudo', 'cp', origin_user_directory, dir])


def is_psk_right():
    subprocess.call('wpa_cli reconfigure > /dev/null', shell=True)
    proc = subprocess.Popen(['./wpa.sh'],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()

    if stderr != b'':
        print(stderr.decode())
    else:
        print('output')
        return stdout.decode().rstrip()


def connect_wpa_cli(id):
    subprocess.call(['wpa_cli', '-i', 'wlan0', 'select_network', id])


def remove_wpa_cli(id):
    subprocess.call(['wpa_cli', '-i', 'wlan0', 'remove_network', id])


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


def write_wpa_supplicant(ssid, psk):
    proc = subprocess.Popen(f"wpa_passphrase '{ssid}' {psk} | sudo tee -a {wpa_supplicant}", 
                            shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout,stderr = proc.communicate()
    print('write wpa end')


def write_temp_wpa_supplicant(ssid, psk):
    proc = subprocess.Popen(f"wpa_passphrase '{ssid}' {psk} | sudo tee -a {user_directory}", 
                            shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout,stderr = proc.communicate()
    print('write temp wpa end')




