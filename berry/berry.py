import berry.module.ble_scan as bl
from berry.module.modi import ModiHandler
from berry.module.wifi import WifiHandler


def ble_list():
    print("scanning ble")
    return bl.scan_ble()
    

def wifi_list():
    print("scanning wifi")
    wf = WifiHandler()
    return wf.scan()


def wifi_current():
    print("current wifi")
    wf = WifiHandler()
    return wf.info()


def wifi_connect(ssid, psw=None, auto_reconnect=True):
    print("connecting wifi")
    wf = WifiHandler()
    return wf.connect(ssid, psw, auto_reconnect)


def modi_list():
    print("scanning modi")
    md = ModiHandler()
    return md.print_modi_list()


def modi_update():
    print("checking modi update")
    md = ModiHandler()
    return md.update_modi()
