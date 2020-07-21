#!/usr/bin/env python3
##
#
# Author: F.PERREAU
##

import atexit
import requests
from tools import cli
from pyVmomi import vim
from pyVim.connect import SmartConnectNoSSL, Disconnect
from tools import tasks
from time import sleep

def get_args():
    parser = cli.build_arg_parser()
    parser.add_argument('-n', '--vm', required=True, help="Name of the VirtualMachine you want to change.")
    parser.add_argument('-m', '--unit', required=True, help='CD/DVD unit number.', type=int)
    parser.add_argument('-i', '--iso', required=False, help='Full path to iso. i.e. "[ds1] folder/Ubuntu.iso"'
                                                            ' If not provided, backend will'
                                                            ' set to RemotePassThrough')
    my_args = parser.parse_args()
    return cli.prompt_for_password(my_args)

def get_obj(content, vim_type, name):
    obj = None
    container = content.viewManager.CreateContainerView(content.rootFolder, vim_type, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj

def ChangeCDDrive(si, vm_obj, cdrom_number, full_path_to_iso=None):
    cdrom_label = 'CD/DVD drive ' + str(cdrom_number)
    cdrom_device = None
    for dev in vm_obj.config.hardware.device:
        if isinstance(dev, vim.vm.device.VirtualCdrom) and dev.deviceInfo.label == cdrom_label:
            cdrom_device = dev

    if not cdrom_device:
        raise RuntimeError("ERROR: {} could not be found.".format(cdrom_label))

    cdrom_spec = vim.vm.device.VirtualDeviceSpec()
    cdrom_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
    cdrom_spec.device = vim.vm.device.VirtualCdrom()
    cdrom_spec.device.controllerKey = cdrom_device.controllerKey
    cdrom_spec.device.key = cdrom_device.key
    cdrom_spec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()

    # if full_path_to_iso is provided it will mount the iso
    if full_path_to_iso:
        cdrom_spec.device.backing = vim.vm.device.VirtualCdrom.IsoBackingInfo()
        cdrom_spec.device.backing.fileName = full_path_to_iso
        cdrom_spec.device.connectable.connected = True
        cdrom_spec.device.connectable.startConnected = True
    else:
        cdrom_spec.device.backing = vim.vm.device.VirtualCdrom.RemotePassthroughBackingInfo()

    # Allowing guest control
    cdrom_spec.device.connectable.allowGuestControl = True

    dev_changes = []
    dev_changes.append(cdrom_spec)
    spec = vim.vm.ConfigSpec()
    spec.deviceChange = dev_changes
    task = vm_obj.ReconfigVM_Task(spec=spec)
    tasks.wait_for_tasks(si, [task])
    return True

def main():
    args = get_args()
    si = SmartConnectNoSSL(host=args.host, user=args.user, pwd=args.password, port=args.port)
    atexit.register(Disconnect, si)

    content = si.RetrieveContent()
    vm = get_obj(content, [vim.VirtualMachine], args.vm)

    if vm:
        count = 36
        while count:
            sleep(5)
            count -= 1
            if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
                if count == 35:
                    print("Waiting VM '{}' shutdown.".format(vm.name))
                if count == 12:
                    print("Shutdown VM '{}' now.".format(vm.name))
                    vm.ShutdownGuest()
            if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOff:
                ChangeCDDrive(si, vm, args.unit, args.iso)
                device_change = args.iso if args.iso else 'Client Device'
                print("Change CDROM {} to '{}' on VM '{}'.".format(args.unit, device_change, vm.name))
                vm.PowerOn()
                print("Power ON VM '{}' now.".format(vm.name))
                break
        if count == 0:
            print("ERROR: Timeout power state VM '{}' !".format(vm.name))
    else:
        print("ERROR: VM '{}' not found !".format(args.name))

# start
if __name__ == "__main__":
    main()
