from subprocess import Popen, PIPE
from time import sleep
import re
import json
import logging


class WifiHandler:
    """ A module for Raspberry Pi wifi(interface: wlan0).

    Usage:
        connect(ssid, psw, auto_reconnect_option)
        scan()
        info()
    """
    def __init__(self, user_dir:str):
        self.user_directory = user_dir
        self.ssid_list = set()
        self.logger = self.__init_logger()
        # TODO: path fix
        self.wpa_supplicant_conf = '/etc/wpa_supplicant/wpa_supplicant.conf'
        self.temp_conf = '../script/temp.conf'
        self.temp_orign_conf = '../script/temp_origin.conf'

    @staticmethod
    def __init_logger():
        logger = logging.getLogger('Dashboard Wifi Logger')
        logger.setLevel(logging.INFO)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        logger.addHandler(stream_handler)

        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # file_handler = logging.FileHandler('/var/log/wifi.log')
        # file_handler.setLevel(logging.INFO)
        # file_handler.setFormatter(formatter)
        # logger.addHandler(file_handler)
        return logger

    def connect(self, ssid, psw, auto_reconnect):
        """ Connect to ssid via psw. Auto_reconnect option needed.

        :param: {'ssid': string, 'password': string, 'auto_reconnect': boolean}
        :return: json
        {
            "status": boolean,     // connected: true,         failed: false
            "ssid": string,        // connected: Wifi name,    failed: null
            "ip address": string   // connected: 172.xx.xx.xx, failed: null
        }
        """
        output = dict()

        # If already known, use wpa_cli
        if self._is_known_wifi(ssid):
            self.logger.info("Known ssid")
            id = self._id_wpa_cli(ssid)
            self._connect_wpa_cli(id)
        # Write to temp_wpa_supplicant.conf and check if psw is right
        else:
            self.logger.info("New ssid")
            self._write_wpa_supplicant(ssid, psw, self.temp_conf)
            self._reconnect_wpa_supplicant(self.temp_conf)

            # If psw is right, add ssid to list and write to wpa_supplicant.conf
            if self._is_psk_right() == 'connected':
                self.ssid_list.add(ssid)
                self._write_wpa_supplicant(ssid, psw, self.wpa_supplicant_conf)
                self._reconnect_wpa_supplicant(self.wpa_supplicant_conf)

                # Set priority of newly added ssid
                id = self._id_wpa_cli(ssid)
                self._set_priority(id, id)
                self.logger.info("Connected")

                output['status'] = True
                output['ssid'] = ssid
                output['ip_address'] = self._ip_wpa_cli()
            # If psw is wrong, just reconnect to wpa_supplicant.conf
            else:
                self._reconnect_wpa_supplicant(self.wpa_supplicant_conf)
                self.logger.info("Wrong psw")
                output['status'] = False
                output['ssid'] = None
                output['ip_address'] = None

            # Return temp.conf to initial state
            self._erase_conf(self.temp_conf)
        
        # Auto_reconnect option
        id = self._id_wpa_cli(ssid)
        self.logger.info(f"Auto connect option: {auto_reconnect}, Id: {id}")
        if not auto_reconnect:
            self._disable_wpa_cli(id)
        else:
            self._enable_wpa_cli(id)

        return json.dumps(output, indent=4, ensure_ascii=False)

    # Check if ssid is known
    def _is_known_wifi(self, ssid):
        return ssid in self.ssid_list

    # Flush temp_wpa_supplicant.conf back to the state before
    def _erase_conf(self, dir):
        proc = Popen(['sudo', 'cp', self.temp_orign_conf, dir])
        proc.wait()

    # Reconfigure wpa_cli to update wpa_supplicant.conf and check psk
    def _is_psk_right(self):
        proc = Popen('sudo wpa_cli -iwlan0 reconfigure > /dev/null', shell=True)
        proc.wait()
        sleep(1)
        proc = Popen(['../script/wpa.sh'], stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()

        if stderr:
            self.logger.info(stderr.decode())
            return
        return stdout.decode().rstrip()

    # Connect to network of the id with wpa_cli
    def _connect_wpa_cli(self, id):
        proc = Popen(['sudo', 'wpa_cli', '-i', 'wlan0', 'select_network', id])
        proc.wait()

    # Remove id from wpa_cli list
    def _remove_wpa_cli(self, id):
        proc = Popen(['sudo', 'wpa_cli', '-i', 'wlan0', 'remove_network', id])
        proc.wait()

    # Get id of the ssid from wpa_cli list
    def _id_wpa_cli(self, ssid):
        proc = Popen(f'sudo wpa_cli -iwlan0 list_networks | grep {ssid}',
                    shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()
        output = stdout.decode()

        if stderr:
            self.logger.info(stderr.decode())
            return
        if not len(stdout):
            self.logger.info(f"Unknown ssid '{ssid}'")
            return -1
        return output.split()[0]
    
    # Get ip address of connected wifi
    def _ip_wpa_cli(self):
        while True:
            sleep(1)
            proc = Popen(f'sudo wpa_cli -iwlan0 status | fgrep -A 1 wpa_state | cut -d "=" -f 2',
                        shell=True, stdout=PIPE, stderr=PIPE)
            stdout, stderr = proc.communicate()
            output = stdout.decode()

            if stderr:
                self.logger.info(stderr.decode())
                return

            list_ = output.split()

            # Wifi not connected
            if list_[0] != 'COMPLETED' and list_[0] != 'ASSOCIATING':
                self.logger.info("Wifi is not connected")
                return -1
            
            # Ip address is not shown yet
            if list_[1].find('.') != -1:
                return list_[1]
            self.logger.info("Checking ip address")

    # Disable network in wpa_cli list
    def _disable_wpa_cli(self, id):
        proc1 = Popen(f'sudo wpa_cli -iwlan0 disable {id} > /dev/null', shell=True)
        proc1.wait()
        proc2 = Popen('sudo wpa_cli -iwlan0 save_config > /dev/null', shell=True)
        proc2.wait()
        self.logger.info(f"Disabled wpa cli id {id}")

    # Enable network in wpa_cli list
    def _enable_wpa_cli(self, id):
        proc1 = Popen(f'sudo wpa_cli -iwlan0 enable {id} > /dev/null', shell=True)
        proc1.wait()
        proc2 = Popen('sudo wpa_cli -iwlan0 save_config > /dev/null', shell=True)
        proc2.wait()
        self.logger.info(f"Enabled wpa cli id {id}")

    # Kill and reconnect wpa_supplicant
    def _reconnect_wpa_supplicant(self, dir):
        MyOut1 = Popen(['sudo', 'killall', 'wpa_supplicant'])
        MyOut1.wait()
        sleep(1)

        MyOut2 = Popen(['sudo', 'wpa_supplicant','-B', '-iwlan0', '-c', dir, '-f/var/log/wpa_supplicant.log'])
        MyOut2.wait()
        sleep(1)
        self.logger.info(f"Wpa supplicant connected: {dir}")

    # Connect dhclient
    def _dhclient_connect(self):
        MyOut = Popen(['sudo', 'dhclient',  'wlan0'])
        MyOut.wait()
        sleep(1)
        self.logger.info("Dhclient connected")

    # Write ssid and password to wpa_supplicant.conf of the directory
    def _write_wpa_supplicant(self, ssid, psw, dir):
        proc = Popen(f"sudo wpa_passphrase '{ssid}' {psw} | sudo tee -a {dir} > /dev/null", shell=True)
        proc.wait()
        self.logger.info("Wpa supplicant write done")

    # Set the priority of the id in wpa_cli list
    def _set_priority(self, id, priority):
        proc = Popen(f'sudo wpa_cli -iwlan0 set_network {id} priority {priority} > /dev/null', shell=True)
        proc.wait()
        sleep(1)
        proc = Popen('sudo wpa_cli -iwlan0 save_config > /dev/null', shell=True)
        proc.wait()
        sleep(1)
        self.logger.info("Set priority done")

    def scan(self):
        """ Scan available wifi list.

        :param: None
        :return: json
        {
            {   
                "ssid": string,             // Wifi name
                "frequency": string,        // 2.4Ghz: 2, 5Ghz: 5
                "intensity": string,        // 0 ~ 70
                "psk requirement": string   // public: off, private: on
            },
        }
        """
        proc = Popen("sudo iwlist wlan0 scan | fgrep -B 3 ESSID | cut -d ':' -f 2 | awk '{print$1}'",
                    shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()
        output = stdout.decode()

        list_ = list()

        if stderr:
            self.logger.info(stderr.decode())
            return

        for text in output.split('--'):
            line = text.split('\"')
            info = line[0].split()
            ssid = line[1]

            # If no ssid
            if not ssid:
                continue
            
            # If same ssid
            repeat = False
            for i in list_:
                if ssid in i.values():
                    repeat = True
            if repeat:
                continue

            # If character has unicode(UTF-8)
            numbers = re.findall('\\\\x[0-9a-fA-F][0-9a-fA-F]', ssid)
            if len(numbers):
                ssid = self._utf8_to_str(ssid, numbers)
                self.logger.info("Unicode encoding done")

            # Frequency & Intensity parsing
            info[0] = info[0].split('.')[0]
            info[1] = info[1].split('=')[1].split('/')[0]

            # Type change 'ssid' & 'info' to dictionary
            info.insert(0, ssid)
            temp_list = ['ssid', 'frequecy', 'intensity', 'psk requirement']
            dict_info = dict(zip(temp_list, info))

            list_.append(dict_info)

        # Sorting by quality
        list_ = sorted(list_, key=lambda x: x['intensity'], reverse=True)
        # List to json
        json_list = json.dumps(list_, indent=4, ensure_ascii=False)

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
        """ SSID, intensity of connected wifi.

        :param: None
        :return: connected: json {"ssid": string, "intensity": string}
                 not connected: string "Not connected"
        """
        proc = Popen("sudo iw wlan0 link | egrep 'SSID|signal' | cut -d ' ' -f 2",
                    shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()
        output = stdout.decode()

        # If error
        if stderr:
            self.logger.info(stderr.decode())
            return

        if not output:
            return "Not connected"

        # Intensity unit change(Max 70)
        list_ = output.split()
        list_[1] = str(int(list_[1]) + 110)

        # Type change list to dictionary
        temp_list = ['ssid', 'intensity']
        output_dict = dict(zip(temp_list, list_))

        return json.dumps(output_dict, ensure_ascii=False)
