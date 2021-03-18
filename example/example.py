from berry import wifi, ble, rpi_modi


if __name__ == "__main__":

    # scan wifi
    wifi_scan_result = wifi.scan()
    print(wifi_scan_result)
    """json
    {
        "DREAMPLUS_GUEST" : {
            "frequency" : 2,    // 2.4 Ghz : 2, 5 Ghz : 5
            "intensity" : 50,   // 0 ~ 70 max(70)
            "psk_requirement" : on  // public : off, private : on
        } 
    }
    """

    # connect wifi
    wifi_connection_result = wifi.connect(
                                          ssid="DREAMPLUS_GUEST",
                                          psk="password",
                                          auto_reconnect=True
                                         )
    print(wifi_connection_result)
    """json
    {
        "status" : "True"    // boolean
        "ssid" : "DREAMPLUS_GUEST",
        "ip_addr" : "172.xx.xx.xx"
    }
    """
    
    # scan ble
    modi_ble_scan = ble.scan()
    print(modi_ble_scan) 
    """json
    {
        "MODI_uuid" : "MODI_59D256F7"
    }
    """

    # display connected modi module
    modi_list = rpi_modi.scan(conn_type="can")    # can, ble, ser
    print(modi_list)
    """json
        {
            "bundle" :  {
                "Gyro",
                "Button",
                "IR"
            }
        }
    """

