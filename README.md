# badfish
badfish is a Redfish-based API tool for managing bare-metal systems via the Redfish API

## Scope
Right now badfish is focused on managing Dell systems, but can potentially work
with any system that supports the Redfish API.  

We're mostly concentrated on programmatically enforcing interface/device boot order to accommodate [TripleO](https://docs.openstack.org/tripleo-docs/latest/) based [OpenStack](https://www.openstack.org/) deployments while simultaneously allowing easy management and provisioning of those same systems via [The Foreman](https://theforeman.org/).

## Features
* Toggle and save a persistent interface/device boot order on remote systems
* Optionally one-time boot to a specific interface or to first device listed for PXE booting
* Check current boot order
* Reboot host
* Logging to a specific path

## Requirements
* iDRAC7,8 or newer
* Firmware version ```2.60.60.60```
* iDRAC administrative account

## Usage
badfish operates against a YAML configuration file to toggle between key:value pair sets of boot interface/device strings.  You just need to create your own interface config that matches your needs to easily swap/save interface/device boot ordering or select one-time boot devices.

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

### Check current boot order
To check the current boot order of a specific host you can use the ```--check-boot``` option which will return an ordered list of boot devices. Additionally you can pass the ```-i``` option which will in turn print on screen what type of host does the current boot order match (Foreman or Director).
```
./badfish.py -H mgmt-your-server.example.com -u root -p yourpass -i config/idrac_interfaces.yml --check-boot
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
