from berry.module.modi import ModiHandler
from berry.module.wifi import WifiHandler
import berry.module.ble_scan as bl
import berry.module.power as pw


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


def wifi_is_known(ssid):
    print(f"checking wifi...{ssid}")
    wf = WifiHandler()
    return wf.is_known(ssid)


def wifi_connect(is_known, ssid, psw=None, auto_reconnect=True):
    print(f"connecting wifi...known: {is_known} ssid:'{ssid}' psw:{psw} opt: {auto_reconnect}")
    wf = WifiHandler()
    return wf.connect(is_known, ssid, psw, auto_reconnect)


def modi_list():
    print("scanning modi")
    md = ModiHandler()
    return md.print_modi_list()


def modi_update():
    print("checking modi update")
    md = ModiHandler()
    return md.update_modi()


def power_off():
    print("power off")
    return pw.off()


def power_reboot():
    print("power reboot")
    return pw.reboot()
