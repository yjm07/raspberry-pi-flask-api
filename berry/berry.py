import berry.module.ble_scan as bl
import berry.module.modi_scan as md
from berry.module.wifi import WifiHandler


def ble_list():
    print("scanning ble")
    return bl.scan_ble()
    

def wifi_list():
    print("scanning wifi")
    wf = WifiHandler('~/smart-ai-api')
    return wf.scan()


def wifi_current():
    print("current wifi")
    wf = WifiHandler('~/smart-ai-api')
    print(type(wf.info()))
    return wf.info()


def wifi_connect(ssid, psw, auto_reconnect):
    print("connecting wifi")
    wf = WifiHandler('~/smart-ai-api')
    return wf.connect(ssid, psw, auto_reconnect)


def modi_list():
    print("scanning modi")
    return md.print_modi_list()
