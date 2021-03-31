from flask import Flask, render_template
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

    Args: None

    Returns: json
        [
            {
                "ssid": string,             // Wifi name
                "frequency": string,        // 2.4Ghz: 2, 5Ghz: 5
                "intensity": string,        // 0 ~ 70
                "psk requirement": string   // public: off, private: on
            },
        ]
    """
    return json.dumps(berry.wifi_list(), indent=4, ensure_ascii=False)


@app.route('/wifi/info')
def get_wifi_current():
    """ SSID, intensity of connected wifi.

    Args: None

    Returns:
        connected: json {"ssid": string, "intensity": string}
        not connected: string "Not connected"
    """
    return json.dumps(berry.wifi_current())


@app.route('/wifi/connect/<string:ssid><string:psw><string:auto_reconnect>')
def get_wifi_connect(ssid, psw=None, auto_reconnect=False):
    """ Connect to ssid via psw with auto reconnect option.

    Args:
        {
            'ssid': string,
            'password': string,         // optional, default: None
            'auto_reconnect': boolean   // optional, default: False
        }

    Returns: json
        {
            "status": boolean,     // connected: true,         failed: false
            "ssid": string,        // connected: Wifi name,    failed: null
            "ip address": string   // connected: 172.xx.xx.xx, failed: null
        }
    """
    return json.dumps(berry.wifi_connect(ssid, psw, auto_reconnect), indent=4, ensure_ascii=False)


@app.route('/ble')
def get_ble_list():
    """ Scan available Modi ble uuid.

    Args: None

    Returns: json
        [
            'MODI_uuid': string,     // MODI_403D8B7C
        ]
    """
    return json.dumps(berry.ble_list())


@app.route('/modi/list')
def get_modi_list():
    """ Scan connected Modi list.

    Args: None

    Returns:
        disconnected: string "No Modi"
        connected: json
        [
            {
                "Module": string,           // "network"
                "Uuid": int,                // 2813171425
                "Id": int,                  // 1761
                "Is up to date": boolean    // false
            },
        ]
    """
    return json.dumps(berry.modi_list(), indent=4)


@app.route('/modi/update')
def run_modi_update():
    """ Check and run update Modi modules if needed.

    Args: None

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


def run():
    app.run(debug=True, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    run()
