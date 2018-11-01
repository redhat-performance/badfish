
=======
badfish
=======

badfish is a Redfish-based API tool for managing bare-metal systems via the Redfish API


Minimum Requirements
====================

- Python 3.4


Optional Requirements
=====================

.. _pytest: http://pytest.org
.. _Sphinx: http://sphinx-doc.org

- `pytest`_ (for running the test suite)
- `Sphinx`_ (for generating documentation)


Basic Setup
===========

Install for the current user:

.. code-block:: console

    $ python setup.py install --user


Run the application:

.. code-block:: console

    $ python -m badfish --help


Run the test suite:

.. code-block:: console
   
    $ pytest test/


Build documentation:

.. code-block:: console

    $ sphinx-build -b html doc doc/_build/html


Scope
=====

.. _TripleO: https://docs.openstack.org/tripleo-docs/latest/
.. _OpenStack: https://openstack.org/
.. _Foreman: https://theforeman.org/

Right now badfish is focused on managing Dell systems, but can potentially work
with any system that supports the Redfish API.

We're mostly concentrated on programatically enforcing interface/device boot order to accomodate `TripleO`_ based `OpenStack`_ deployments while simultaneously allowing easy management and provisioning of those same systems via `Foreman`_.


Features
========
* Toggle and save a persistent interface/device boot order on remote systems
* Optionally one-time boot to a specific interface


Requirements
============
* iDRAC7,8 or newer
* Firmware version ```2.60.60.60```
* iDRAC administrative account


Usage
=====
badfish operates against a YAML configuration file to toggle between keyvalue:pair sets of boot interface/device strings.  You just need to create your own interface config that matches your needs to easily swap/save interface/device boot ordering or select one-time boot devices.


Enforcing an OpenStack Director-style interface order
=====================================================
In our performance/scale R&D environments TripleO-based OpenStack deployments require a specific 10/25/40GbE NIC to be the primary boot device for PXE, followed by disk, and then followed by the rest of the interfaces.

```
./badfish.py -H mgmt-your-server.example.com -u root -p yourpass -i config/idrac_interfaces.yml -t director
```

Enforcing a Foreman-style interface order
=========================================
Foreman and Red Hat Satellite (as of 6.x based on Foreman) require managed systems to first always PXE from the interface that is Foreman-managed (DHCP/PXE).  If the system is not set to build it will simply boot to local disk.  In our setup we utilize a specific NIC for this interface based on system type.

```
./badfish.py -H mgmt-your-server.example.com -u root -p yourpass -i config/idrac_interfaces.yml -t foreman
```

Forcing a one-time boot to Foreman
==================================
To force systems to perform a one-time boot off a specific interface simply pass the ```--pxe``` flag to any of the commands above, by default it will pxe off the Foreman interface listed in your ```config/idrac_interfaces.yml``` or equivalent resource.


Reboot only option
==================
In certain cases you might need to only reboot the host, for this case we included the ```--reboot``` flag which will force a GracefulRestart on the target host. Note that this option is not to be used with any other option.


Dell Foreman / PXE Interface
============================
Your usage may vary, this is what our configuration looks like via ```config/idrac_interfaces.yml```

| Machine Type | Network Interface      |
| ------------ | ----------------------:|
| Dell r620	   |  NIC.Integrated.1-3-1  |
| Dell r630    |  NIC.Slot.2-1-1        |
| Dell r930    |  NIC.Integrated.1-3-1  |
| Dell r720xd  |  NIC.Integrated.1-3-1  |
| Dell r730xd  |  NIC.Integrated.1-3-1  |
