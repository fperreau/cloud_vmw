#!/bin/env /snap/bin/pwsh
##
# CDDrive.ps1 -server vcenter -user administrator@vsphere.local -passwd secret -vm node1 -iso "[DS01] cloudinit/node1.iso"
##

param($server,$user,$passwd,$vm,$iso)
Import-Module VMware.VimAutomation.Core
$WarningPreference = "SilentlyContinue"
$ProgressPreference = "SilentlyContinue"

#$pwd=/opt/custom/java -cp /opt/custom TripleDES d $passwd
Connect-VIServer -Server $server -User $user -Password $passwd
$count=36  # 3 minutes
try {
    while ($count) {
        sleep 5
        $count--
        $vm_id = Get-VM $vm
        if ($vm_id.PowerState -eq 'PoweredOn'){
            if ($count -eq 35){
                Write-Host "Waiting VM '$($vm)' shutdown."
            }
            if ($count -eq 12){  # 1 minutes
                Write-Host "Shutdown VM '$($vm)' now."
                Shutdown-VMGuest $vm_id -Confirm:$false
            }
        }
        if ($vm_id.PowerState -eq 'PoweredOff'){
            Write-Host "Change CDROM '$($iso)' on VM '$($vm)'."
            Get-CDDrive $vm_id|Set-CDDrive -IsoPath $iso -StartConnect $true -Confirm:$false
            Write-Host "Power ON VM '$($vm)' now."
            Start-VM $vm_id -Confirm:$false
            break
        }
    }
    if ($count -eq 0){
        Write-Host "ERROR: Timeout power state VM '$($vm)' !"
    }
}
catch {
    Write-Host "ERROR: VM '$($vm)' not found !"
}
Disconnect-VIServer -Confirm:$false -Server $server
