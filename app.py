from flask import Flask, render_template, request
import berry.script.template_updater
import berry.berry as berry
import json


app = Flask(__name__, static_url_path="")


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/wifi/list')
def get_wifi_list():
    """ Scan available wifi list.

    Usage: /wifi/list

    Returns: json
        [
            {
                "ssid": string,             // Wifi name
                "frequency": string,        // 2.4Ghz: 2, 5Ghz: 5
                "intensity": string,        // 0 ~ 70
                "psk-requirement": string   // public: off, private: on
            },
        ]
    """
    return json.dumps(berry.wifi_list(), indent=4, ensure_ascii=False)


@app.route('/wifi/info')
def get_wifi_current():
    """ SSID, intensity of connected wifi.

    Usage: /wifi/info

    Returns:
        connected: json {"ssid": string, "intensity": string}
        not connected: string "Not connected"
    """
    return json.dumps(berry.wifi_current())


@app.route('/wifi/is-known/<ssid>')
def is_wifi_known(ssid):
    """ Check if ssid is known.

    Usage: /wifi/known/wifi_name

    Returns: json: boolean
    """
    return json.dumps(berry.wifi_is_known(ssid))


@app.route('/wifi/connect/known', methods=['POST'])
def wifi_connect_known():
    """ Connect to ssid via psw with auto reconnect option.

    Usage: /wifi/connect/known
            body:
            {
                "ssid": "wifi name",
                "opt": true/false
            }

    Returns: json
        {
            "status": boolean,     // connected: true,         failed: false
            "ssid": string,        // connected: Wifi name,    failed: null
            "ip-address": string   // connected: 172.xx.xx.xx, failed: null
        }
    """
    input_data = request.get_json()
    ssid = input_data["ssid"]
    auto_reconnect = input_data["opt"]
    return json.dumps(berry.wifi_connect(True, ssid, None, auto_reconnect), indent=4, ensure_ascii=False)


@app.route('/wifi/connect/unknown', methods=['POST'])
def wifi_connect_unknown():
    """ Connect to ssid via psw with auto reconnect option.

    Usage: /wifi/connect/unknown
            body:
            {
                "ssid": "wifi name",
                "psw": "password",
                "opt": true/false
            }

    Returns: json
        {
            "status": boolean,     // connected: true,         failed: false
            "ssid": string,        // connected: Wifi name,    failed: null
            "ip-address": string   // connected: 172.xx.xx.xx, failed: null
        }
    """
    input_data = request.get_json()
    ssid = input_data["ssid"]
    psw = input_data["psw"]
    auto_reconnect = input_data["opt"]
    
    return json.dumps(berry.wifi_connect(False, ssid, psw, auto_reconnect), indent=4, ensure_ascii=False)


@app.route('/ble')
def get_ble_list():
    """ Scan available Modi ble uuid.

    Usage: /ble

    Returns: json
        ['MODI_uuid': string, ]     // MODI_403D8B7C
    """
    return json.dumps(berry.ble_list())


@app.route('/modi/list')
def get_modi_list():
    """ Scan connected Modi list.

    Usage: /modi/list

    Returns:
        disconnected: string "No Modi"
        connected: json
        [
            {
                "Module": string,           // "network"
                "Uuid": int,                // 2813171425
                "Id": int,                  // 1761
                "Is-up-to-date": boolean    // false
            },
        ]
    """
    return json.dumps(berry.modi_list(), indent=4)


@app.route('/modi/update')
def run_modi_update():
    """ Check and run update Modi modules if needed.

    Usage: /modi/update

    Returns:
        disconnected: string "No Modi"
        connected: json
        [
            {
                "Module": string,           // "network"
                "Id": int,                  // 1761
            },
        ]
    """
    return json.dumps(berry.modi_update(), indent=4)


@app.route('/power-off')
def power_off():
    """ Shutdown the machine.

    Usage: /power-off

    Returns: None
    """
    return berry.power_off()


@app.route('/power-reboot')
def power_reboot():
    """ Reboot the machine.

    Usage: /power-reboot

    Returns: None
    """
    return berry.power_reboot()


def run():
    app.run(debug=True, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    run()
