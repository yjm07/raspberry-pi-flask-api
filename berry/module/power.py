import subprocess


def off():
    proc = subprocess.Popen(['sudo', 'shutdown', '-h', 'now'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    if stderr:
        print(stderr.decode())
        return
    print(stdout.decode())


def reboot():
    proc = subprocess.Popen(['sudo', 'shutdown', '-r', 'now'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    if stderr:
        print(stderr.decode())
        return
    print(stdout.decode())
