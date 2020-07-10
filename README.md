Role cloud_kvm
==============

Cloud KVM role help you to deploy a CloudInit image domain in Linux KVM.

version: 0.1.0

Requirements
------------

Minimum Ansible 2.8, VMware vSphere ESXi + vCenter, PowerCLI + Powershell 


Role Variables
--------------

Those variables define class, cidata, image and iso file used to deploy domain for each Linux target.

**TARGET OS - ubuntu, rhel, centos**

    # debian, ubuntu, rhel, fedora, centos
    cloud_os: rhel
    class_os: "{{ CLOUDINIT[cloud_os].class }}"

**Cloud-Init images default dict**

    CLOUDINIT:
      debian:
        class: DEBIAN
        cidata: [ meta-data, user-data ]
        template: ""
        iso: DEBIAN/debian-10.4.0-amd64-netinst.iso
        ova: ""
      ubuntu:
        class: DEBIAN
        cidata: [ meta-data, user-data ]
        template: ""
        iso: UBUNTU/ubuntu-20.04-live-server-amd64.iso
        ova: ""
      centos:
        class: REDHAT
        cidata: [ meta-data, user-data ]
        template: ""
        iso: CENTOS/CentOS-8.1.1911-x86_64-dvd1.iso
        ova: ""    
      rhel:
        class: REDHAT
        cidata: [ meta-data, user-data ]
        template: rhel82
        guest_id: rhel8_64Guest
        iso: REDHAT/rhel-8.2-x86_64-dvd.iso
        ova: /mnt/depot/iso/CLOUD/rhel82.ova
      windows:
        class: WINDOWS


Example Playbook
----------------

    - name: CloudInit domain example
      hosts: all
      gather_facts: no
      roles:
        - cloud_vmw

License
-------

Apache 2.0

