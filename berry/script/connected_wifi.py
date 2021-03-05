import subprocess


def connected_wifi():

    proc = subprocess.Popen("iw wlan0 link | grep SSID | cut -d ' ' -f 2", 
                            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    output = stdout.decode()

    # if error
    if stderr != b'':
        return stderr.decode()

    if len(output) == 0:
        return "Not connected"
        
    return output.rstrip("\n")
