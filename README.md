![badfish](/image/badfish-original-licensed.small.png)

[![Copr build status](https://copr.fedorainfracloud.org/coprs/quadsdev/python3-badfish/package/python3-badfish/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/quadsdev/python3-badfish/package/python3-badfish/)
[![Build Status](https://travis-ci.com/redhat-performance/badfish.svg?branch=master)](https://travis-ci.com/redhat-performance/badfish)
[![codecov](https://codecov.io/gh/redhat-performance/badfish/branch/master/graph/badge.svg?token=CNJN0CD6GN)](https://codecov.io/gh/redhat-performance/badfish)
[![Docker Repository on Quay](https://quay.io/repository/quads/badfish/status "Docker Repository on Quay")](https://quay.io/repository/quads/badfish)

   * [About Badfish](#badfish)
      * [Scope](#scope)
      * [Features](#features)
      * [Requirements](#requirements)
      * [Setup](#setup)
         * [Badfish RPM package](#badfish-rpm-package)
         * [Badfish Standalone CLI](#badfish-standalone-cli)
         * [Badfish Standalone Script](#badfish-standalone-script)
         * [Badfish Standalone within a virtualenv](#badfish-standalone-within-a-virtualenv)
      * [Usage](#usage)
        * [As Python Library](#as-python-library)
        * [Via Podman](#via-podman)
      * [Common Operations](#common-operations)
         * [Enforcing an OpenStack Director-style interface order](#enforcing-an-openstack-director-style-interface-order)
         * [Enforcing a Foreman-style interface order](#enforcing-a-foreman-style-interface-order)
         * [Enforcing a Custom interface order](#enforcing-a-custom-interface-order)
         * [Forcing a one time boot to a specific device](#forcing-a-one-time-boot-to-a-specific-device)
         * [Forcing a one time boot to a specific mac address](#forcing-a-one-time-boot-to-a-specific-mac-address)
         * [Forcing a one time boot to a specific type](#forcing-a-one-time-boot-to-a-specific-type)
         * [Forcing a one-time boot to PXE](#forcing-a-one-time-boot-to-pxe)
         * [Rebooting a System](#rebooting-a-system)
         * [Power Cycling a System](#power-cycling-a-system)
         * [Power State Control](#power-state-control)
         * [Check Power State](#check-power-state)
         * [Resetting iDRAC](#resetting-idrac)
         * [BIOS factory reset](#bios-factory-reset)
         * [Check current boot order](#check-current-boot-order)
         * [Toggle boot device](#toggle-boot-device)
         * [Variable number of retries](#variable-number-of-retries)
         * [Firmware inventory](#firmware-inventory)
         * [Clear Job Queue](#clear-job-queue)
         * [List Job Queue](#list-job-queue)
         * [Check Job Status](#check-job-status)
         * [Set Bios Password](#set-bios-password)
         * [Remove Bios Password](#remove-bios-password)
         * [List Network Interfaces](#list-network-interfaces)
         * [List Memory](#list-memory)
         * [List Processors](#list-processors)
         * [Check Virtual Media](#check-virtual-media)
         * [Unmount Virtual Media](#unmount-virtual-media)
         * [Get SRIOV mode](#get-sriov-mode)
         * [Set SRIOV mode](#set-sriov-mode)
         * [Get BIOS attributes](#get-bios-attributes)
         * [Get specific BIOS attribute](#get-specific-bios-attribute)
         * [Set BIOS attribute](#set-bios-attribute)
         * [Get server screenshot](#get-server-screenshot)
         * [Bulk actions via text file with list of hosts](#bulk-actions-via-text-file-with-list-of-hosts)
         * [Verbose Output](#verbose-output)
         * [Log to File](#log-to-file)
      * [iDRAC and Data Format](#idrac-and-data-format)
         * [Dell Foreman and PXE Interface](#dell-foreman-and-pxe-interface)
         * [Host type overrides](#host-type-overrides)
      * [Contributing](#contributing)
      * [Contact](#contact)

# Badfish
Badfish is a Redfish-based API tool for managing bare-metal systems via the [Redfish API](https://www.dmtf.org/standards/redfish)

You can read more [about badfish](https://quads.dev/about-badfish/) at the [QUADS](https://quads.dev/) website.

## Scope
Right now Badfish is focused on managing Dell, SuperMicro and HPE systems, but can potentially work with any system that supports the Redfish API.  Functionality may vary depending on the vendor Redfish implementation.

We're mostly concentrated on programmatically enforcing interface/device boot order to accommodate [TripleO](https://docs.openstack.org/tripleo-docs/latest/) based [OpenStack](https://www.openstack.org/) and [OpenShift](https://www.openshift.com/) deployments while simultaneously allowing easy management and provisioning of those same systems via [The Foreman](https://theforeman.org/).  Badfish can be useful as a general standalone, unified vendor IPMI/OOB tool however as support for more vendors is added.

## Features
* Toggle and save a persistent interface/device boot order on remote systems
* Perform one-time boot to a specific interface, mac address or device listed for PXE booting
* Enforce a custom interface boot order
* Check current boot order
* Reboot host
* Reset iDRAC
* Clear iDRAC job queue
* Revert to factory settings
* Check/set SRIOV
* Get firmware inventory of installed devices supported by iDRAC
* Check/ummount virtual media en-masse across a set of systems
* Obtain limited hardware information (CPU, Memory, Interfaces)
* Bulk actions via plain text file with list of hosts for parallel execution
* Logging to a specific path
* Containerized Badfish image

## Requirements
* (Dell) iDRAC7,8,9 or newer
* (Dell) Firmware version ```2.60.60.60``` or higher
* iDRAC administrative account
* Python >= ```3.6``` or [podman](https://podman.io/getting-started/installation) as a container.
* python3-devel >= ```3.6``` (If using standalone below).

## Setup
### Badfish RPM package
```bash
dnf copr enable quadsdev/python3-badfish  -y
dnf install python3-badfish -y
```

Active releases:
- Centos-stream 8
- EPEL for CentOS 7
- EPEL for CentOS 8
- Fedora 33
- Fedora 34
- Fedora 35

* Note: For EL7 you'll need a working Python 3.6+ and dependencies _(python3-pyyaml, python3-setuptools)_ so setting up [Software Collections/SCL](https://www.softwarecollections.org/en/scls/rhscl/rh-python36/) will be required before installing and using Badfish as an RPM package.

### Badfish Standalone CLI
```bash
git clone https://github.com/redhat-performance/badfish && cd badfish
python setup.py build
python setup.py install --prefix ~/.local
```
NOTE:

* This will allow Badfish to be called from the terminal via the `badfish` command
* This requires `python3-devel` if you see errors about missing `Python.h`.
* This is **ideal** for a non-root user, otherwise you'll get badfish in `/root/.local/bin/badfish` for example.
* If you have problems running as root you will need to add whatever you set in `--prefix=` to your `$PATH` by adding something like the following to the end of your `~/.bashrc` file.

```bash
if [ -d "$HOME/.local/bin" ] ; then
  PATH="$PATH:$HOME/.local/bin"
fi
```

### Badfish Standalone Script
```bash
git clone https://github.com/redhat-performance/badfish && cd badfish
pip install -r requirements.txt
```
NOTE:
* This will allow the badfish script execution via `./src/badfish/badfish.py`

### Badfish Standalone within a virtualenv
```bash
git clone https://github.com/redhat-performance/badfish && cd badfish
virtualenv .badfish_venv
source .badfish_venv/bin/activate
```
NOTE:
* Both setup methods above can be used within a virtualenv
* After using badfish, the virtual environment can be deactivated running the ```deactivate``` command

## Usage
Badfish can be consumed in 2 forms after successful installation. Either via the standalone cli tool or as a python library.
For an extensive use of the cli tool check the [Common Operations](#common-operations) section of this file.

NOTE: Badfish operates against a YAML configuration file to toggle between key:value pair sets of boot interface/device strings.  You just need to create your own interface config that matches your needs to easily swap/save interface/device boot ordering or select one-time boot devices.

### As Python Library
If Badfish has been properly installed in the system (RPM package install, setuptools), then the library should be available under your python path therefore it can be imported as a python library to your python project.
```python
from badfish.badfish import badfish_factory

badfish = await badfish_factory(
    _host=_oob_mgmt,
    _username=_username,
    _password=_password,
)
boot_devices = await badfish.get_boot_devices()
success = await badfish.boot_to(boot_devices[0])
if success:
    print("Change boot device success")
result = await badfish.reboot_server()
if not result:
    print("Failed to reboot system")
```
NOTE: Badfish relies heavily on asyncio for executing multiple tasks. If you will be using badfish from outside an async function you will have to provide an async event loop and run via `run_until_complete`

### Via Podman
Badfish happily runs in a container image using podman, for this you need to first pull the Badfish image via:
```bash
podman pull quay.io/quads/badfish
```
You can then run badfish from inside the container:
```bash
podman run -it --rm --dns $DNS_IP quay.io/quads/badfish -H $HOST -u $USER -p $PASS --reboot-only
```
NOTE:
* If you are running quads against a host inside a VPN you must specify your VPN DNS server ip address with `--dns`
* If you would like to use a different file for `config/idrac_interfaces.yml` you can map a volume to your modified config with `-v idrac_interfaces.yml:config/idrac_interfaces.yml`

## Common Operations

### Enforcing an OpenStack Director-style interface order
In our performance/scale R&D environments TripleO-based OpenStack deployments require a specific 10/25/40GbE NIC to be the primary boot device for PXE, followed by disk, and then followed by the rest of the interfaces.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass -i config/idrac_interfaces.yml -t director
```

### Enforcing a Foreman-style interface order
Foreman and Red Hat Satellite (as of 6.x based on Foreman) require managed systems to first always PXE from the interface that is Foreman-managed (DHCP/PXE).  If the system is not set to build it will simply boot to local disk.  In our setup we utilize a specific NIC for this interface based on system type.

```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass -i config/idrac_interfaces.yml -t foreman
```

### Enforcing a Custom interface order
Badfish allows you to supply your own interface order type in addition to `director` and `foreman` modes as defined in `idrac_interfaces.yml`

* Supply your own distinct string in the first part of the key value (split by `_`)
* Refer to it via the string name
* Consequently [host type overrides](#host-type-overrides) can also be leveraged

We will use the custom interface order called **ocp5beta** as an example.

_Example_ any system you want to boot with a certain custom interface order.

```
ocp5beta_fc640_interfaces: NIC.Slot.2-4,NIC.Slot.2-1,NIC.Slot.2-2,NIC.Slot.2-3
```

_Example_ a rack of systems you want to boot with a certain custom interface order.


```
ocp5beta_f21_fc640_interfaces: NIC.Slot.2-4,NIC.Slot.2-1,NIC.Slot.2-2,NIC.Slot.2-3
```

_Example_ a specific system you want to boot with a certain custom interface order

```
ocp5beta_f21_h23_fc640_interfaces: NIC.Slot.2-4,NIC.Slot.2-1,NIC.Slot.2-2,NIC.Slot.2-3
```

Now you can run Badfish against the custom interface order type you have defined, refer to the [custom overrides](#host-type-overrides) on further usage examples.

```bash
src/badfish/badfish.py --host-list /tmp/hosts -u root -p password -i config/idrac_interfaces.yml -t ocp5beta
```


### Forcing a one time boot to a specific device
To force systems to perform a one-time boot to a specific device you can use the ```--boot-to``` option and pass as an argument the device you want the one-time boot to be set to. This will change the one time boot BIOS attributes OneTimeBootMode and OneTimeBootSeqDev and on the next reboot it will attempt to PXE boot or boot from that interface string.  You can obtain the device list via the `--check-boot` directive below.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass --boot-to NIC.Integrated.1-3-1
```

### Forcing a one time boot to a specific mac address
To force systems to perform a one-time boot to a specific mac address you can use the ```--boot-to-mac``` option and pass as an argument the device mac address for a specific NIC that you want the one-time boot to be set to. This will change the one time boot BIOS attributes OneTimeBootMode and OneTimeBootSeqDev and on the next reboot it will attempt to PXE boot or boot from that interface.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass --boot-to-mac A9:BB:4B:50:CA:54
```

### Forcing a one time boot to a specific type
To force systems to perform a one-time boot to a specific type you can use the ```--boot-to-type``` option and pass as an argument the device type, as defined on the iDRAC interfaces yaml, that you want the one-time boot to be set to. For this action you must also include the path to your interfaces yaml. This will change the one time boot BIOS attributes OneTimeBootMode and OneTimeBootSeqDev and on the next reboot it will attempt to PXE boot or boot from the first interface defined for that host type on the interfaces yaml file.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass -i config/idrac_interfaces.yml --boot-to-type foreman
```

### Forcing a one-time boot to PXE
To force systems to perform a one-time boot to PXE, simply pass the ```--pxe``` flag to any of the commands above, by default it will pxe off the first available device for PXE booting.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass -i config/idrac_interfaces.yml -t foreman --pxe
```

### Rebooting a system
In certain cases you might need to only reboot the host, for this case we included the ```--reboot-only``` flag which will force a GracefulRestart on the target host. Note that this option is not to be used with any other option.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass --reboot-only
```

### Power cycling a system
For a hard reset you can use ```--power-cycle``` flag which will run a ForceOff instruction on the target host. Note that this option is not to be used with any other option.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass --power-cycle
```

### Power State Control
You can also turn a server on or off by using options `--power-on` and `--power-off` respectively.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass --power-on
```

### Check Power State
For checking the current power state of a server you can run badfish with the `--power-state` option.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass --power-state
```
Partial Output:
```
- INFO     - Power state for mgmt-your-server.example.com: On
```

### Resetting iDRAC
For the replacement of `racadm racreset`, the optional argument `--racreset` was added. When this argument is passed to ```badfish```, a graceful restart is triggered on the iDRAC itself.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass --racreset
```

### BIOS factory reset
You can restore BIOS default settings by calling Badfish with the option `--factory-reset`.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass --factory-reset
```
NOTE:
* WARNING: Use this carefully, vendor defaults differ and may be disruptive. Do not use this in the Scale Lab or ALIAS.

### Check current boot order
To check the current boot order of a specific host you can use the ```--check-boot``` option which will return an ordered list of boot devices. Additionally you can pass the ```-i``` option which will in turn print on screen what type of host does the current boot order match as those defined on the iDRAC interfaces yaml.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass -i config/idrac_interfaces.yml --check-boot
```

### Toggle boot device
If you would like to enable or disable a boot device you can use ```--toggle-boot-device``` argument which takes the device name as input and will toggle the `Enabled` state from True to False and vice versa.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass --toggle-boot-device NIC.Integrated.1-3-1```
```

### Variable number of retries
At certain points during the execution of ```badfish``` the program might come across a non responsive resources and will automatically retry to establish connection. We have included a default value of 15 retries after failed attempts but this can be customized via the ```--retries``` optional argument which takes as input an integer with the number of desired retries.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass -i config/idrac_interfaces.yml -t foreman --retries 20
```

### Firmware inventory
If you would like to get a detailed list of all the devices supported by iDRAC you can run ```badfish``` with the ```--firware-inventory``` option which will return a list of devices with additional device info.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass --firmware-inventory
```

### Clear Job Queue
If you would like to clear all the jobs that are queued on the remote iDRAC you can run ```badfish``` with the ```--clear-jobs``` option which query for all active jobs in the iDRAC queue and will post a request to clear the queue.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass --clear-jobs
```

You can also force the clearing of Dell iDRAC job queues by passing the `--force` option.

```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass --clear-jobs --force
```

### List Job Queue
If you would like to list all active jobs that are queued on the remote iDRAC you can run ```badfish``` with the ```--ls-jobs``` option which query for all active jobs in the iDRAC queue and will return a list with all active items.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass --ls-jobs
```

### Check Job Status
If you would like to the status of an existing LifeCycle controller job you can run ```badfish``` with the ```--check-job``` option and passing the job id which can be obtained via ```--ls-jobs```. This will return a detail of the specific job with status and percentage of completion.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass --check-job JID_340568202796
```

### Set Bios Password
If you would like to set the bios password you can run ```badfish``` with the ```--set-bios-password``` option and passing the new password with ```--new-password```. If a password is already set you must pass this with ```--old-password``` otherwise optional.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass --set-bios-password --new-password new_pass --old-password old_pass
```

### Remove Bios Password
If you would like to remove the bios password you can run ```badfish``` with the ```--remove-bios-password``` option and passing the existing password with ```--old-password```.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass --remove-bios-password --old-password old_pass
```

### List Network Interfaces
For getting a list of network interfaces with individual metadata for each you can run ```badfish``` with the ```--ls-interfaces``` option.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass --ls-interfaces
```

### List Memory
For getting a detailed list of memory devices you can run ```badfish``` with the ```--ls-memory``` option.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass --ls-memory
```

### List Processors
For getting a detailed list of processors you can run ```badfish``` with the ```--ls-processors``` option.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass --ls-processors
```

### Check Virtual Media
If you would like to check for any active virtual media you can run ```badfish``` with the ```--check-virtual-media``` option which query for all active virtual devices.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass --check-virtual-media
```

### Unmount Virtual Media
If you would like to unmount all active virtual media you can run ```badfish``` with the ```--unmount-virtual-media``` option which post a request for unmounting all active virtual devices.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass --unmount-virtual-media
```
NOTE:
* This functionality is only available for SuperMicro devices.

### Get SRIOV mode
For checking if the global SRIOV mode is enabled you can use ```--get-sriov```
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass --get-sriov
```
NOTE:
  * This is only supported on DELL devices.

### Set SRIOV mode
For changing the mode of the SRIOV glabal BIOS attribute, we have included 2 new arguments.
In case the setting is in disabled mode, you can enable it by passing ```--enable-sriov```
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass --enable-sriov
```
On the contrary, if you would like to disable the SRIOV mode, you can now pass ```--disable-sriov```
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass --disable-sriov
```
NOTE:
  * This is only supported on DELL devices.

### Get BIOS attributes
To get a list of all BIOS attributes we can potentially modify (some might be set as read-only), you can run badfish with ```--get-bios-attribute``` alone and this will return a list off all BIOS attributes with their current value set.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass --get-bios-attribute
```

### Get specific BIOS attribute
In case you would like to get a more detailed view on the parameters for a BIOS attribute you can run ```--get-bios-attribute``` including the specific name of the attribute via ```--attribute```.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass --get-bios-attribute --attribute ProcC1E
```

### Set BIOS attribute
To change the value of a bios attribute you can use ```--set-bios-attribute``` passing both ```--attribute``` and ```--value```.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass --set-bios-attribute --attribute ProcC1E --value Enabled
```
NOTE:
* You can get the list of allowed values you can pass for that attribute by looking at the attribute details via ```--get-bios-attribute``` for that specific one.

### Get server screenshot
If you would like to get a screenshot with the current state of the server you can now run badfish with ```--screenshot``` which will capture this and store it in the current directory in png format.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass --screenshot
```

### Bulk actions via text file with list of hosts
In the case you would like to execute a common badfish action on a list of hosts, you can pass the optional argument ```--host-list``` in place of ```-H``` with the path to a text file with the hosts you would like to action upon and any addtional arguments defining a common action for all these hosts.
```bash
badfish --host-list /tmp/bad-hosts -u root -p yourpass --clear-jobs
```

### Verbose output
If you would like to see a more detailed output on console you can use the ```--verbose``` option and get a additional debug logs. Note: this is the default log level for the ```--log``` argument.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass -i config/idrac_interfaces.yml -t foreman --verbose
```

### Log to file
If you would like to log the output of ```badfish``` you can use the ```--log``` option and pass the path to where you want ```badfish``` to log it's output to.
```bash
badfish -H mgmt-your-server.example.com -u root -p yourpass -i config/idrac_interfaces.yml -t foreman --log /tmp/bad.log
```

## iDRAC and Data Format

### Dell Foreman and PXE Interface
Your usage may vary, this is what our configuration looks like via ```config/idrac_interfaces.yml```

| Machine Type | Network Interface      |
| ------------ | ----------------------:|
| Dell fc640   |  NIC.Integrated.1-1-1  |
| Dell r620	   |  NIC.Integrated.1-3-1  |
| Dell r630    |  NIC.Slot.2-1-1        |
| Dell r930    |  NIC.Integrated.1-3-1  |
| Dell r720xd  |  NIC.Integrated.1-3-1  |
| Dell r730xd  |  NIC.Integrated.1-3-1  |
| Dell r740xd  |  NIC.Integrated.1-3-1  |
| Dell r640    |  NIC.Integrated.1-1-1  |

### Host type overrides
Every other method that requires passing the `-i` argument, is going to parse the key strings from this and look for the most adequate candidate for the given FQDN.
We format the key strings with the following criteria:
```
{host_type}_[{rack}_[{ULocation}_[{blade}_]]]{model}_interfaces
```
With rack, ULocation and blade being optional in a hierarchical fashion otherwise mandatory, ergo you can't define blade without ULocation and so forth. host_type and model values are always mandatory.

#### Example for director type overrides:

| Keys defined on interfaces yaml | FQDN | Use boot order |
| :------------------------------ |:----:| --------------:|
| director_r620_interfaces         | mgmt-f21-h17-000-r620.domain.com | NO             |
| director_f21_r620_interfaces     | mgmt-f21-h17-000-r620.domain.com | NO             |
| director_f21_h17_r620_interfaces | mgmt-f21-h17-000-r620.domain.com | YES            |

| Keys defined on interfaces yaml | FQDN | Use boot order |
| :------------------------------ |:----:| --------------:|
| director_r620_interfaces         | mgmt-f21-h18-000-r620.domain.com | NO             |
| director_f21_r620_interfaces     | mgmt-f21-h18-000-r620.domain.com | YES            |
| director_f21_h17_r620_interfaces | mgmt-f21-h18-000-r620.domain.com | NO             |

| Keys defined on interfaces yaml | FQDN | Use boot order |
| :------------------------------ |:----:| --------------:|
| director_r620_interfaces         | mgmt-f22-h17-000-r620.domain.com | YES            |
| director_f21_r620_interfaces     | mgmt-f22-h17-000-r620.domain.com | NO             |
| director_f21_h17_r620_interfaces | mgmt-f22-h17-000-r620.domain.com | NO             |

## Contributing
We love pull requests and welcome contributions from everyone!  Please use the `development` branch to send pull requests.  Here are the general steps you'd want to follow.

1) Fork the Badfish Github repository
2) Clone the forked repository
3) Push your changes to your forked clone
4) Open a pull request against our `development` branch.

* Here is some useful documentation
  - [Creating a pull request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request)
  - [Keeping a cloned fork up to date](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/syncing-a-fork)

## Contact

* You can find us on IRC in `#badfish` (or `#quads`) on `irc.libera.chat` if you have questions or need help.  [Click here](https://https://web.libera.chat/?channels=#quads) to join in your browser.

