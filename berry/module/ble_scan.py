import subprocess


def scan_ble():
    proc = subprocess.Popen("sudo timeout -s SIGINT 1s hcitool -i hci0 lescan | cut -d ' ' -f 2 | grep MODI", 
                            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    output = stdout.decode()

    # If error
    if stderr:
        print(stderr.decode())
        return stderr.decode()

    list_ = list(set(output.split()))
    return list_
