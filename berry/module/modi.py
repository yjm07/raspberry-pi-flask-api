import subprocess


class ModiHandler:
    """ A module for Modi.

    Usage:
        print_modi_list()
        update_modi()
    """
    def __init__(self):
        self.bundle_list = list()
        num = self._num_modi_in_usb()

        if not num:
            return "No Modi"
        
        import modi

        for _ in range(num):
            bundle = modi.MODI()
            bundles = bundle.modules
            for m in bundles:
                if m.is_connected:
                    self.bundle_list.append((m.module_type, m.uuid, m.id, m.is_up_to_date))
        bundle.close()

    # Return list of connected Modi info list.
    def print_modi_list(self):
        temp_list = ['Module', 'Uuid', 'Id', 'Is up to date']
        _bundle_list = list(dict(zip(temp_list, m)) for m in self.bundle_list)

        return _bundle_list
    
    # If update needed, run upadate.
    def update_modi(self):
        list_ = list()

        for m in self.bundle_list:
            if not m[3]:
                print("Update start")
                if m[0] == 'network':
                    # TODO: Network module update 
                    # modi.update_network_firmware()
                    pass
                else:
                    modi.update_module_firmware(target_ids=(m[2],))
                # Module name and Id
                list_.append((m[0], m[2]))
        # All modules are already up to date
        if not len(list_):
            return "Update not needed"
        # List to dict list
        print("Update done")
        tmp_list = ['Module', 'Id']
        updated_list = list(dict(zip(tmp_list, m)) for m in list_)
        return updated_list

    # Number of Modi connected to usb.
    def _num_modi_in_usb(self):
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
