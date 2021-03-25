import berry.script.ble_scan as bl
import berry.script.modi_scan as md
from berry.module.wifi import WifiHandler

def ble_list():
    print("scanning ble")
    return bl.scan_ble()
    

def wifi_list():
    print("scanning wifi")
    wf = WifiHandler('~/smart-ai-api')
    return wf.scan()


def wifi_connected():
    print("scanning current wifi")
    wf = WifiHandler('~/smart-ai-api')
    return wf.info()


def modi_list():
    print("scanning modi")
    return md.print_modi_list()
