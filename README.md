![badfish](/image/badfish-original-licensed.small.png)

[![Build Status](https://travis-ci.com/redhat-performance/badfish.svg?branch=master)](https://travis-ci.com/redhat-performance/badfish)
[![Build Status](https://img.shields.io/docker/cloud/build/quads/badfish.svg)](https://cloud.docker.com/repository/registry-1.docker.io/quads/badfish/builds)

# Badfish
Badfish is a Redfish-based API tool for managing bare-metal systems via the Redfish API

## Scope
Right now Badfish is focused on managing Dell systems, but can potentially work
with any system that supports the Redfish API.  

We're mostly concentrated on programmatically enforcing interface/device boot order to accommodate [TripleO](https://docs.openstack.org/tripleo-docs/latest/) based [OpenStack](https://www.openstack.org/) deployments while simultaneously allowing easy management and provisioning of those same systems via [The Foreman](https://theforeman.org/).

## Features
* Toggle and save a persistent interface/device boot order on remote systems
* Optionally one-time boot to a specific interface or to first device listed for PXE booting
* Check current boot order
* Reboot host
* Reset iDRAC
* Export iDRAC system configuration to  XML
* Clear iDRAC job queue
* Get firmware inventory of installed devices supported by iDRAC
* Bulk actions via plain text file with list of hosts
* Logging to a specific path
* Containerized Badfish image

## Requirements
* iDRAC7,8 or newer
* Firmware version ```2.60.60.60```
* iDRAC administrative account

## Usage
Badfish operates against a YAML configuration file to toggle between key:value pair sets of boot interface/device strings.  You just need to create your own interface config that matches your needs to easily swap/save interface/device boot ordering or select one-time boot devices.

## Usage via docker
Badfish can now be run via a docker-image. For this you need to first pull the Badfish image via:
```
docker pull quads/badfish
```
You can then run badfish from inside the container:
```
docker run -it --rm --dns $DNS_IP quads/badfish -H $HOST -u $USER -p $PASS --reboot-only
```
NOTE:
* If you are running quads against a host inside a VPN you must specify your VPN DNS server ip address with --dns
* If you would like to use a different file for config/idrac_interfaces.yml you can map a volume to your modified config with `-v idrac_interfaces.yml:config/idrac_interfaces.yml`

### Enforcing an OpenStack Director-style interface order
In our performance/scale R&D environments TripleO-based OpenStack deployments require a specific 10/25/40GbE NIC to be the primary boot device for PXE, followed by disk, and then followed by the rest of the interfaces.
```
./badfish.py -H mgmt-your-server.example.com -u root -p yourpass -i config/idrac_interfaces.yml -t director
```

### Enforcing a Foreman-style interface order
Foreman and Red Hat Satellite (as of 6.x based on Foreman) require managed systems to first always PXE from the interface that is Foreman-managed (DHCP/PXE).  If the system is not set to build it will simply boot to local disk.  In our setup we utilize a specific NIC for this interface based on system type.

```
./badfish.py -H mgmt-your-server.example.com -u root -p yourpass -i config/idrac_interfaces.yml -t foreman
```

### Forcing a one time boot to a specific device
To force systems to perform a one-time boot to a specific device you can use the ```--boot-to``` option and pass as an argument the device you want the one-time boot to be set to. This will change the one time boot BIOS attributes OneTimeBootMode and OneTimeBootSeqDev and automatically reboot the host after changes are applied. 
```
./badfish.py -H mgmt-your-server.example.com -u root -p yourpass --boot-to NIC.Integrated.1-3-1
```

### Forcing a one-time boot to PXE
To force systems to perform a one-time boot to PXE, simply pass the ```--pxe``` flag to any of the commands above, by default it will pxe off the first available device for PXE booting.
```
./badfish.py -H mgmt-your-server.example.com -u root -p yourpass -i config/idrac_interfaces.yml -t foreman --pxe
```

### Reboot only option
In certain cases you might need to only reboot the host, for this case we included the ```--reboot-only``` flag which will force a GracefulRestart on the target host. Note that this option is not to be used with any other option.
```
./badfish.py -H mgmt-your-server.example.com -u root -p yourpass --reboot-only
```

### Resetting iDRAC
For the replacement of `racadm racreset`, the optional argument `--racreset` was added. When this argument is passed to ```badfish```, a graceful restart is triggered on the iDRAC itself.
```
./badfish.py -H mgmt-your-server.example.com -u root -p yourpass --racreset
```

### Check current boot order
To check the current boot order of a specific host you can use the ```--check-boot``` option which will return an ordered list of boot devices. Additionally you can pass the ```-i``` option which will in turn print on screen what type of host does the current boot order match (Foreman or Director).
```
./badfish.py -H mgmt-your-server.example.com -u root -p yourpass -i config/idrac_interfaces.yml --check-boot
```

### Variable number of retries
At certain points during the execution of ```badfish``` the program might come across a non responsive resources and will automatically retry to establish connection. We have included a default value of 15 retries after failed attempts but this can be customized via the ```--retries``` optional argument which takes as input an integer with the number of desired retries.
```
./badfish.py -H mgmt-your-server.example.com -u root -p yourpass -i config/idrac_interfaces.yml -t foreman --retries 20
```

### Export system configuration
If you would like export the current iDRAC system settings to an xml you can run ```badfish``` with the ```--export-configuration``` option which create a job request for system configuration export and will create an xml file with the exported attributes on the current directory.
```
./badfish.py -H mgmt-your-server.example.com -u root -p yourpass --export-configuration
```

### Firmware inventory
If you would like to get a detailed list of all the devices supported by iDRAC you can run ```badfish``` with the ```--firware-inventory``` option which will return a list of devices with additional device info.
```
./badfish.py -H mgmt-your-server.example.com -u root -p yourpass --firmware-inventory
```

### Clear Job Queue
If you would like to clear all the jobs that are queued on the remote iDRAC you can run ```badfish``` with the ```--clear-jobs``` option which query for all active jobs in the iDRAC queue and will post a request to clear the queue.
```
./badfish.py -H mgmt-your-server.example.com -u root -p yourpass --clear-jobs
```

### Bulk actions via text file with list of hosts
In the case you would like to execute a common badfish action on a list of hosts, you can pass the optional argument ```--host-list``` in place of ```-H``` with the path to a text file with the hosts you would like to action upon and any addtional arguments defining a common action for all these hosts.
```
./badfish.py --host-list /tmp/bad-hosts -u root -p yourpass --clear-jobs
```

### Verbose output
If you would like to see a more detailed output on console you can use the ```--verbose``` option and get a additional debug logs. Note: this is the default log level for the ```--log``` argument.
```
./badfish.py -H mgmt-your-server.example.com -u root -p yourpass -i config/idrac_interfaces.yml -t foreman --verbose
```

### Log to file
If you would like to log the output of ```badfish``` you can use the ```--log``` option and pass the path to where you want ```badfish``` to log it's output to.
```
./badfish.py -H mgmt-your-server.example.com -u root -p yourpass -i config/idrac_interfaces.yml -t foreman --log /tmp/bad.log
```

#### Dell Foreman / PXE Interface
Your usage may vary, this is what our configuration looks like via ```config/idrac_interfaces.yml```

| Machine Type | Network Interface      |
| ------------ | ----------------------:|
| Dell r620	   |  NIC.Integrated.1-3-1  |
| Dell r630    |  NIC.Slot.2-1-1        |
| Dell r930    |  NIC.Integrated.1-3-1  |
| Dell r720xd  |  NIC.Integrated.1-3-1  |
| Dell r730xd  |  NIC.Integrated.1-3-1  |
