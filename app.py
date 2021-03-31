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
    return berry.wifi_list()


@app.route('/wifi/info')
def get_wifi_current():
    return berry.wifi_current()


@app.route('/wifi/connect/<string:ssid><string:psw><string:auto_reconnect>')
def get_wifi_connect(ssid, psw, auto_reconnect):
    return berry.wifi_connect(ssid, psw, auto_reconnect)


@app.route('/ble')
def get_ble_list():
    return berry.ble_list()


@app.route('/modi')
def get_modi_list():
    return berry.modi_list()


def run():
    app.run(debug=True, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    run()
