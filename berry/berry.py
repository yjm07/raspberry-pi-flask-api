import berry.script.ble_scan as bl
import berry.script.wifi_scan as wf
import berry.script.modi_scan as md
import berry.script.connected_wifi as c_wf


def ble_list():
    print("scanning ble")
    return bl.scan_ble()
    

def wifi_list():
    print("scanning wifi")
    return wf.scan_wifi()


def wifi_connected():
    print("scanning current wifi")
    return c_wf.connected_wifi()


def modi_list():
    print("scanning modi")
    return md.print_modi_list()
