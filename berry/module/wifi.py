import subprocess
import re
import json
from time import sleep


class Wifi:
    """
    A module for Raspberry Pi wifi(interface: wlan0).
    Usage:
        connect(ssid, psw, auto_reconnect_option)
        scan()
        info()
    """
    def __init__(self, user_dir:str):
        self.user_directory = user_dir
        self.ssid_list = set()
        # TODO: path fix
        self.wpa_supplicant_conf = '/etc/wpa_supplicant/wpa_supplicant.conf'
        self.temp_conf = '../script/temp.conf'
        self.temp_orign_conf = '../script/temp_origin.conf'


    def connect(self, ssid, psw, auto_reconnect):
        """
        Connect to ssid via psw. Auto_reconnect option needed.
        Input: {'ssid': string, 'password': string, 'auto_reconnect': boolean}
        Output: json
        {
            "status": boolean,     // connected: true,         failed: false
            "ssid": string,        // connected: Wifi name,    failed: null
            "ip_address": string   // connected: 172.xx.xx.xx, failed: null
        }
        """
        output = dict([('status', None), ('ssid', None), ('ip_address', None)])

        # If already known, use wpa_cli
        if self._is_known_wifi(ssid):
            id = self._id_wpa_cli(ssid)
            self._connect_wpa_cli(id)
        # Write to temp_wpa_supplicant.conf and check if psw is right
        else:
            self._write_wpa_supplicant(ssid, psw, self.temp_conf)
            self._reconnect_wpa_supplicant(self.temp_conf)

            psw_right = self._is_psk_right()

            # If psw is right, add ssid to list and write to wpa_supplicant.conf
            if psw_right == 'connected':
                self.ssid_list.add(ssid)
                self._write_wpa_supplicant(ssid, psw, self.wpa_supplicant_conf)
                self._reconnect_wpa_supplicant(self.wpa_supplicant_conf)

                # Set priority of newly added ssid
                id = self._id_wpa_cli(ssid)
                self._set_priority(id, id)
                print("connected")

                output['status'] = True
                output['ssid'] = ssid
                output['ip_address'] = self._ip_wpa_cli()
            # If psw is wrong, just reconnect to wpa_supplicant.conf
            else:
                self._reconnect_wpa_supplicant(self.wpa_supplicant_conf)
                print("wrong psw")
                output['status'] = False

            self._flush(self.temp_conf)
        
        return json.dumps(output, indent=4, ensure_ascii=False)

        # TODO: auto_reconnect option
        # if auto_reconnect:
        #     ssid_list.remove(ssid)
        #     _remove_wpa_cli(id)
        # else:

    # Check ssid list if already known
    def _is_known_wifi(self, ssid):
        return ssid in self.ssid_list

    # Flush temp_wpa_supplicant.conf back to the state before
    def _flush(self, dir):
        subprocess.call(['sudo', 'cp', self.temp_orign_conf, dir])

    # Reconfigure wpa_cli to update wpa_supplicant.conf and check psk
    def _is_psk_right(self):
        subprocess.call('wpa_cli -iwlan0 reconfigure > /dev/null', shell=True)
        sleep(1)
        proc = subprocess.Popen(['../script/wpa.sh'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        proc.wait()

        if stderr != b'':
            print(stderr.decode())
        else:
            return stdout.decode().rstrip()

    # Connect to network of the id with wpa_cli
    def _connect_wpa_cli(self, id):
        subprocess.call(['wpa_cli', '-i', 'wlan0', 'select_network', id])

    # Remove id from wpa_cli list
    def _remove_wpa_cli(self, id):
        subprocess.call(['wpa_cli', '-i', 'wlan0', 'remove_network', id])

    # Get id of the ssid from wpa_cli list
    def _id_wpa_cli(self, ssid):
        proc = subprocess.Popen(f'wpa_cli -iwlan0 list_networks | grep {ssid}',
                                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        output = stdout.decode()
        proc.wait()

        if stderr != b'':
            print(stderr.decode())
        if not len(stdout):
            return -1
        return output.split()[0]
    
    # Get ip of connected wifi
    def _ip_wpa_cli(self):
        while True:
            sleep(1)
            proc = subprocess.Popen(f'wpa_cli -iwlan0 status | fgrep -A 1 wpa_state | cut -d "=" -f 2',
                                    shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            output = stdout.decode()
            proc.wait()

            if stderr != b'':
                print(stderr.decode())

            list_ = output.split()

            # Wifi not connected
            if list_[0] != 'COMPLETED' and list_[0] != 'ASSOCIATING':
                return -1
            
            if list_[1].find('.') != -1:
                return list_[1]

    # Kill and reconnect wpa_supplicant
    def _reconnect_wpa_supplicant(self, dir):
        MyOut1 = subprocess.Popen(['sudo', 'killall', 'wpa_supplicant'])
        MyOut1.wait()
        sleep(1)

        MyOut2 = subprocess.Popen(['sudo', 'wpa_supplicant','-B', '-iwlan0', '-c', dir, '-f/var/log/wpa_supplicant.log'])
        MyOut2.wait()
        sleep(1)
        print(f'{dir} connected')

    # Run dhclient
    def _dhclient_connect(self):
        MyOut = subprocess.Popen(['sudo', 'dhclient',  'wlan0'])
        MyOut.wait()
        sleep(1)
        print('dhclient connected')

    # Write ssid and password to wpa_supplicant.conf of the directory
    def _write_wpa_supplicant(self, ssid, psw, dir):
        proc = subprocess.Popen(f"wpa_passphrase '{ssid}' {psw} | sudo tee -a {dir}", 
                                shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = proc.communicate()
        proc.wait()
        print('write wpa end')

    # Set the priority of the id in wpa_cli list
    def _set_priority(self, id, priority):
        subprocess.call(['wpa_cli', '-i', 'wlan0', 'set_network', id, 'priority', priority])
        sleep(1)
        subprocess.call(['wpa_cli', '-i', 'wlan0', 'save_config'])
        sleep(1)


    def scan(self):
        """
        Scan available wifi list.
        Input: None
        Ouput: json
        {
            "SSID": {                       // Wifi name
                "frequency": string,        // 2.4Ghz: 2, 5Ghz: 5
                "intensity": string,        // 0 ~ 70
                "psk requirement": string   // public: off, private: on
            } 
        }
        """
        proc = subprocess.Popen("sudo iwlist wlan0 scan | fgrep -B 3 ESSID | cut -d ':' -f 2 | awk '{print$1}'", 
                                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        output = stdout.decode()

        dict_ = dict()

        if stderr != b'':
            dict_['error'] = stderr.decode()
            return dict_

        for text in output.split('--'):
            line = text.split('\"')
            info = line[0].split()
            ssid = line[1]

            # If no ssid
            if not ssid: continue

            # If character has unicode(UTF-8)
            numbers = re.findall('\\\\x[0-9a-fA-F][0-9a-fA-F]', ssid)
            if len(numbers):
                ssid = self._utf8_to_str(ssid, numbers)

            # Frequency & Intensity parsing
            info[0] = info[0].split('.')[0]
            info[1] = info[1].split('=')[1].split('/')[0]
            
            # Type change 'info' to dictionary
            temp_list = ['frequecy', 'intensity', 'psk requirement']
            dict_info = dict(zip(temp_list, info))
            
            dict_[ssid] = dict_info

        # Sorting by quality
        dict_ = dict(sorted(dict_.items(), key=lambda x: x[1]['intensity'], reverse=True))
        # Dictionary to json
        json_list = json.dumps(dict_, indent=4, ensure_ascii=False)

        print(json_list)
        return json_list

    # Encode Utf-8 to string
    def _utf8_to_str(self, ssid, numbers):
        byte_string = b''
        for n in numbers:
            sp = ssid.split(n, 1)
            if sp[0] != '':
                byte_string += sp[0].encode('utf-8')
            ssid = sp[1]
            # encoding word by word
            byte_string += self._string_to_hex(n).to_bytes(1, byteorder='big')
        byte_string += ssid.encode('utf-8')
        ssid = byte_string.decode()
        return ssid

    # Change string to hex number
    def _string_to_hex(self, s):
        if len(s) != 4:
            return s
        elif s[:2] != '\\x':
            return s
        else:
            f = self._char_to_hex(s[2])
            s = self._char_to_hex(s[3])
            if f is not None and s is not None:
                return f*16+s
            else:
                return s

    # Change character to hex number
    def _char_to_hex(self, ch):
        if re.match('[0-9]',ch):
            return int(ch)
        elif re.match('[a-f]',ch):
            return ord(ch)-87
        elif re.match('[A-F]',ch):
            return ord(ch)-55
        elif True:
            return None


    def info(self):
        """
        SSID, intensity of connected wifi.
        Input: None
        Ouput: json {"SSID": string, "intensity": string}
        """
        proc = subprocess.Popen("iw wlan0 link | egrep 'SSID|signal' | cut -d ' ' -f 2",
                                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        output = stdout.decode()

        # If error
        if stderr != b'':
            return stderr.decode()

        if len(output) == 0:
            return "Not connected."

        # Intensity unit change(Max 70)
        list_ = output.split()
        list_[1] = str(int(list_[1]) + 110)

        # Type change list to dictionary
        temp_list = ['SSID', 'intensity']
        output_list = dict(zip(temp_list, list_))
            
        return json.dumps(output_list, ensure_ascii=False)

    # result = wf._ip_wpa_cli()
    # result = wf.info()
    # result = wf.scan()
    # print(result)