import subprocess
import json


def print_modi_list():
    num = num_modi_in_usb()

    if not num:
        return "no modi"
    
    import modi

    bundle_list = list()
    for i in range(num):
        bundle = modi.MODI()
        bundles = bundle.modules
        for m in bundles:
            if m.is_connected:
                bundle_list.append((m.module_type, m.uuid, m.id, m.is_up_to_date))
    bundle.close()

    for m in bundle_list:
        if not m[3]:
            if m[0] == 'network':
                pass
                # modi.update_network_firmware()
            else:
                modi.update_module_firmware(target_ids=(m[2],))

    return json.dumps(bundle_list, indent=4)


def num_modi_in_usb():
    proc = subprocess.Popen("lsusb | grep 2fde:0002",
                            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    output = stdout.decode()

    # If error
    if stderr:
        print(stderr.decode())
        return stderr.decode()

    if not len(output):
        return 0

    list_ = output.rstrip('\n').split('\n')
    return len(list_)
