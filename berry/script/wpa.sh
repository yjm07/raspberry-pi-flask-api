#!/bin/bash

function poke {
    while true
    do
        printf '\n'
        sleep 1
    done
}

function watch {
    (poke) | sudo wpa_cli | while read line
    do
        case "$line" in
            *'CTRL-EVENT-ASSOC-REJECT'* | *'auth_failures'*)
                echo "incorrect key"
                return
            ;;
            *'CTRL-EVENT-NETWORK-NOT-FOUND'*)
                echo "network not found"
                return
            ;;
            *'CTRL-EVENT-CONNECTED'*)
                echo "connected"
                return
        esac
    done
}

sudo wpa_cli disable_network 0 > /dev/null
sudo wpa_cli enable_network 0 > /dev/null

watch