#! /usr/bin/env python

from core.logger import Logger
from logging import FileHandler, Formatter, DEBUG, INFO
from requests.exceptions import ConnectionError, ConnectTimeout, ReadTimeout

import argparse
import json
import os
import re
import requests
import sys
import time
import warnings
import yaml

warnings.filterwarnings("ignore")

BOOT_SOURCES_URI = "/redfish/v1/Systems/System.Embedded.1/BootSources/Settings"
BIOS_URI = "/redfish/v1/Systems/System.Embedded.1/Bios/Settings"
RETRIES = 15


class Badfish:
    def __init__(self, _host, _username, _password, _retries=RETRIES, log=None, _log_level=INFO):
        self.host = _host
        self.username = _username
        self.password = _password
        self.retries = _retries
        self.log = log
        self.logger = Logger()
        self.logger.start(level=_log_level)

        if self.log:
            file_handler = FileHandler(self.log)
            file_handler.setFormatter(Formatter(self.logger.LOGFMT))
            file_handler.setLevel(DEBUG)
            self.logger.addHandler(file_handler)

    @staticmethod
    def progress_bar(value, end_value, state, bar_length=20):
        percent = float(value) / end_value
        arrow = '-' * int(round(percent * bar_length) - 1) + '>'
        spaces = ' ' * (bar_length - len(arrow))

        if state.lower() == "on":
            state = "On  "
        sys.stdout.write(
            "\r  Polling: [{0}] {1}% - Host state: {2}\n".format(arrow + spaces, int(round(percent * 100)), state)
        )
        sys.stdout.flush()

    def error_handler(self, _response):
        try:
            data = _response.json()
        except ValueError:
            self.logger.error("Error reading response from host.")
            sys.exit(1)

        if "error" in data:
            detail_message = str(data["error"]["@Message.ExtendedInfo"][0]["Message"])
            self.logger.warning(detail_message)

        sys.exit(1)

    def get_boot_seq(self):
        bios_boot_mode = self.get_bios_boot_mode()
        if bios_boot_mode == "Uefi":
            return "UefiBootSeq"
        else:
            return "BootSeq"

    def get_bios_boot_mode(self):
        self.logger.debug("Getting bios boot mode.")
        try:
            _response = requests.get(
                "https://%s/redfish/v1/Systems/System.Embedded.1/Bios" % self.host,
                verify=False,
                auth=(self.username, self.password),
            )
        except (ConnectionError, ConnectTimeout, ReadTimeout) as ex:
            self.logger.debug(ex)
            self.logger.error("Failed to communicate with server. Host appears to be down.")
            sys.exit(1)

        try:
            data = _response.json()
        except ValueError:
            self.logger.error("Could not retrieve Bios Boot mode.")
            sys.exit(1)

        try:
            bios_boot_mode = data[u"Attributes"]["BootMode"]
            return bios_boot_mode
        except KeyError:
            self.logger.warning("Could not retrieve Bios Attributes. Assuming Bios.")
            return "Bios"

    def get_boot_devices(self):
        _boot_seq = self.get_boot_seq()
        try:
            _response = requests.get(
                "https://%s/redfish/v1/Systems/System.Embedded.1/BootSources" % self.host,
                verify=False,
                auth=(self.username, self.password),
            )
        except (ConnectionError, ConnectTimeout, ReadTimeout) as ex:
            self.logger.debug(ex)
            self.logger.error("Failed to communicate with server.")
            sys.exit(1)
        data = _response.json()
        return data[u"Attributes"][_boot_seq]

    def get_job_queue(self):
        self.logger.debug("Getting job queue.")
        _url = "https://%s/redfish/v1/Managers/iDRAC.Embedded.1/Jobs" % self.host
        try:
            _response = requests.get(_url, auth=(self.username, self.password), verify=False)
        except (ConnectionError, ConnectTimeout, ReadTimeout) as ex:
            self.logger.debug(ex)
            self.logger.error("Failed to communicate with server. Host appears to be down.")
            sys.exit(1)
        data = _response.json()
        data = str(data)
        job_queue = re.findall("JID_.+?'", data)
        jobs = [job.strip("}").strip("\"").strip("'") for job in job_queue]
        return jobs

    def get_job_status(self, _job_id):
        self.logger.debug("Getting job status.")

        for _ in range(self.retries):
            try:
                _response = requests.get(
                    "https://%s/redfish/v1/Managers/iDRAC.Embedded.1/Jobs/%s" % (self.host, _job_id),
                    verify=False,
                    auth=(self.username, self.password),
                )
            except (ConnectionError, ConnectTimeout, ReadTimeout) as ex:
                self.logger.debug(ex)
                self.logger.error("Failed to communicate with server.")
                continue

            status_code = _response.status_code
            if status_code == 200:
                self.logger.info("Command passed to check job status, code 200 returned.")
                time.sleep(10)
            else:
                self.logger.error("Command failed to check job status, return code is %s." % status_code)

                self.error_handler(_response)

            data = _response.json()
            if data[u"Message"] == "Task successfully scheduled.":
                self.logger.info("Job id %s successfully scheduled." % _job_id)
                return
            else:
                self.logger.warning("JobStatus not scheduled, current status is: %s." % data[u"Message"])

        self.logger.error("Not able to successfully schedule the job.")
        sys.exit(1)

    def get_host_type(self, _interfaces_path):
        boot_devices = self.get_boot_devices()

        if _interfaces_path:
            with open(_interfaces_path, "r") as f:
                try:
                    definitions = yaml.safe_load(f)
                except yaml.YAMLError as ex:
                    self.logger.error("Couldn't read file: %s" % _interfaces_path)
                    self.logger.debug(ex)
                    sys.exit(1)

            host_model = self.host.split(".")[0].split("-")[-1]
            interfaces = {}
            for _host in ["foreman", "director"]:
                match = True
                interfaces[_host] = definitions["%s_%s_interfaces" % (_host, host_model)].split(",")
                for device in sorted(boot_devices[: len(interfaces)], key=lambda x: x[u"Index"]):
                    if device[u"Name"] == interfaces[_host][device[u"Index"]]:
                        continue
                    else:
                        match = False
                        break
                if match:
                    return _host

        return None

    def get_power_state(self):
        _url = 'https://%s/redfish/v1/Systems/System.Embedded.1/' % self.host
        self.logger.debug("url: %s" % _url)
        try:
            response = requests.get(_url, verify=False, auth=(self.username, self.password), timeout=20)
        except (ConnectionError, ConnectTimeout, ReadTimeout) as ex:
            self.logger.debug(ex)
            self.logger.debug("Can't communicate with host.")
            return "Down"
        if response.ok:
            data = response.json()
        else:
            self.logger.debug("Couldn't get power state. Retrying.")
            return "Down"
        self.logger.debug("Current server power state is: %s." % data[u'PowerState'])

        return data[u'PowerState']

    def change_boot_order(self, _interfaces_path, _host_type):
        with open(_interfaces_path, "r") as f:
            try:
                definitions = yaml.safe_load(f)
            except yaml.YAMLError as ex:
                self.logger.error(ex)
                sys.exit(1)

        host_model = self.host.split(".")[0].split("-")[-1]
        interfaces = definitions["%s_%s_interfaces" % (_host_type, host_model)].split(",")

        boot_devices = self.get_boot_devices()
        change = False
        for i in range(len(interfaces)):
            for device in boot_devices:
                if interfaces[i] == device[u"Name"]:
                    if device[u"Index"] != i:
                        device[u"Index"] = i
                        change = True
                    break

        if change:
            self.patch_boot_seq(boot_devices)

        else:
            self.logger.warning("No changes were made since the boot order already matches the requested.")
            sys.exit()

    def patch_boot_seq(self, boot_devices):
        _boot_seq = self.get_boot_seq()
        url = "https://%s%s" % (self.host, BOOT_SOURCES_URI)
        payload = {"Attributes": {_boot_seq: boot_devices}}
        headers = {"content-type": "application/json"}
        response = None
        _status_code = 400
        count = 0
        while _status_code != 200 and count < self.retries:
            try:
                count += 1
                response = requests.patch(
                    url, data=json.dumps(payload), headers=headers, verify=False,
                    auth=(self.username, self.password)
                )
            except (ConnectionError, ConnectTimeout, ReadTimeout) as ex:
                self.logger.debug(ex)
                self.logger.error("Failed to communicate with server.")
                continue
            _status_code = response.status_code
        if _status_code == 200:
            self.logger.info("PATCH command passed to update boot order.")
        else:
            self.logger.error("There was something wrong with your request.")

            if response:
                self.error_handler(response)

    def set_next_boot_pxe(self):
        _url = "https://%s/redfish/v1/Systems/System.Embedded.1" % self.host
        _payload = {"Boot": {"BootSourceOverrideTarget": "Pxe"}}
        _headers = {"content-type": "application/json"}
        try:
            _response = requests.patch(
                _url, data=json.dumps(_payload), headers=_headers, verify=False, auth=(self.username, self.password)
            )
        except (ConnectionError, ConnectTimeout, ReadTimeout) as ex:
            self.logger.debug(ex)
            self.logger.error("Failed to communicate with server.")
            sys.exit(1)

        time.sleep(5)

        if _response.status_code == 200:
            self.logger.info('PATCH command passed to set next boot onetime boot device to: "%s".' % "Pxe")
        else:
            self.logger.error("Command failed, error code is %s." % _response.status_code)

            self.error_handler(_response)

    def clear_job_queue(self):
        _job_queue = self.get_job_queue()
        if _job_queue:
            _url = "https://%s/redfish/v1/Managers/iDRAC.Embedded.1/Jobs" % self.host
            _headers = {"content-type": "application/json"}
            self.logger.warning("Clearing job queue for job IDs: %s." % _job_queue)
            for _job in _job_queue:
                job = _job.strip("'")
                url = "%s/%s" % (_url, job)
                try:
                    requests.delete(url, headers=_headers, verify=False, auth=(self.username, self.password))
                except (ConnectionError, ConnectTimeout, ReadTimeout) as ex:
                    self.logger.debug(ex)
                    self.logger.error("Failed to communicate with server.")
                    sys.exit(1)

            job_queue = self.get_job_queue()
            if not job_queue:
                self.logger.info("Job queue for iDRAC %s successfully cleared." % self.host)
            else:
                self.logger.error("Job queue not cleared, current job queue contains jobs: %s." % job_queue)
                sys.exit(1)
        else:
            self.logger.warning(
                "Job queue already cleared for iDRAC %s, DELETE command will not execute." % self.host
            )

    def create_job(self, _url, _payload, _headers, expected=200):
        try:
            _response = requests.post(
                _url, data=json.dumps(_payload), headers=_headers, verify=False, auth=(self.username, self.password)
            )
        except (ConnectionError, ConnectTimeout, ReadTimeout) as ex:
            self.logger.debug(ex)
            self.logger.error("Failed to communicate with server.")
            sys.exit(1)

        status_code = _response.status_code

        if status_code == expected:
            self.logger.info("POST command passed to create target config job.")
        else:
            self.logger.error("POST command failed to create BIOS config job, status code is %s." % status_code)

            self.error_handler(_response)

        convert_to_string = str(_response.__dict__)
        job_id_search = re.search("JID_.+?,", convert_to_string).group()
        _job_id = re.sub("[,']", "", job_id_search).strip("}").strip("\"").strip("'")
        self.logger.info("%s job ID successfully created." % _job_id)
        return _job_id

    def create_bios_config_job(self, uri):
        _url = "https://%s/redfish/v1/Managers/iDRAC.Embedded.1/Jobs" % self.host
        _payload = {"TargetSettingsURI": uri}
        _headers = {"content-type": "application/json"}
        return self.create_job(_url, _payload, _headers)

    def send_reset(self, reset_type):
        _url = "https://%s/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset" % self.host
        _payload = {"ResetType": reset_type}
        _headers = {"content-type": "application/json"}
        try:
            _response = requests.post(
                _url, data=json.dumps(_payload), headers=_headers, verify=False, auth=(self.username, self.password)
            )
        except (ConnectionError, ConnectTimeout, ReadTimeout) as ex:
            self.logger.debug(ex)
            self.logger.error("Failed to communicate with server.")
            sys.exit(1)
        status_code = _response.status_code
        if status_code == 204:
            self.logger.info(
                "Command passed to %s server, code return is %s." % (reset_type, status_code)
            )
            time.sleep(10)
        else:
            self.logger.error(
                "Command failed to %s server, status code is: %s." % (reset_type, status_code)
            )

            self.error_handler(_response)

    def reboot_server(self):
        self.logger.debug("Rebooting server: %s." % self.host)
        power_state = self.get_power_state()
        if power_state.lower() == "on":
            self.send_reset("GracefulRestart")

            host_down = self.polling_host_state("Off")

            if not host_down:
                self.logger.warning(
                    "Unable to graceful shutdown the server, will perform forced shutdown now."
                )
                self.send_reset("ForceOff")

            host_not_down = self.polling_host_state("Down", False)

            if host_not_down:
                self.send_reset("On")

        elif power_state.lower() == "off":
            self.send_reset("On")
        return True

    def reset_idrac(self):
        self.logger.debug("Running reset iDRAC.")
        _url = "https://%s/redfish/v1/Managers/iDRAC.Embedded.1/Actions/Manager.Reset/" % self.host
        _payload = {"ResetType": "GracefulRestart"}
        _headers = {'content-type': 'application/json'}
        self.logger.debug("url: %s" % _url)
        self.logger.debug("payload: %s" % _payload)
        self.logger.debug("headers: %s" % _headers)
        try:
            _response = requests.post(
                _url, data=json.dumps(_payload), headers=_headers, verify=False, auth=(self.username, self.password)
            )
        except (ConnectionError, ConnectTimeout, ReadTimeout) as ex:
            self.logger.debug(ex)
            self.logger.error("There was something wrong with your request.")
            sys.exit(1)
        status_code = _response.status_code
        if status_code == 204:
            self.logger.info("Status code %s returned for POST command to reset iDRAC." % status_code)
        else:
            data = _response.json()
            self.logger.error("Status code %s returned, error is: \n%s." % (status_code, data))
            sys.exit(1)
        time.sleep(15)

        self.logger.info("iDRAC will now reset and be back online within a few minutes.")
        return True

    def boot_to(self, device):
        if self.check_device(device):
            self.clear_job_queue()
            self.reset_idrac()
            host_up = self.polling_host_state("On")
            time.sleep(5)
            if host_up:
                self.send_one_time_boot(device)
                job_id = self.create_bios_config_job(BIOS_URI)
                if job_id:
                    self.get_job_status(job_id)
                self.reboot_server()
            else:
                self.logger.error("Couldn't communicate with host after %s attempts." % self.retries)
                sys.exit(1)
        else:
            sys.exit(1)
        return True

    def send_one_time_boot(self, device):
        _url = "https://%s%s" % (self.host, BIOS_URI)
        _payload = {"Attributes": {"OneTimeBootMode": "OneTimeBootSeq", "OneTimeBootSeqDev": device}}
        _headers = {"content-type": "application/json"}
        try:
            _response = requests.patch(
                _url, data=json.dumps(_payload), headers=_headers, verify=False, auth=(self.username, self.password)
            )
        except (ConnectionError, ConnectTimeout, ReadTimeout) as ex:
            self.logger.debug(ex)
            self.logger.error("Failed to communicate with server.")
            sys.exit(1)
        status_code = _response.status_code
        if status_code == 200:
            self.logger.info("Command passed to set BIOS attribute pending values.")
        else:
            self.logger.error("Command failed, error code is: %s." % status_code)
            self.error_handler(_response)

    def check_boot(self, _interfaces_path):
        if _interfaces_path:

            _host_type = self.get_host_type(_interfaces_path)

            if _host_type:
                self.logger.warning("Current boot order is set to: %s." % _host_type)
            else:
                boot_devices = self.get_boot_devices()

                self.logger.warning("Current boot order does not match any of the given.")
                self.logger.info("Current boot order:")
                for device in sorted(boot_devices, key=lambda x: x[u"Index"]):
                    self.logger.info("%s: %s" % (int(device[u"Index"]) + 1, device[u"Name"]))

        else:
            boot_devices = self.get_boot_devices()
            self.logger.info("Current boot order:")
            for device in sorted(boot_devices, key=lambda x: x[u"Index"]):
                self.logger.info("%s: %s" % (int(device[u"Index"]) + 1, device[u"Name"]))
        return True

    def check_device(self, device):
        self.logger.debug("Checking device %s." % device)
        devices = self.get_boot_devices()
        self.logger.debug(devices)
        boot_devices = [device["Name"].lower() for device in devices]
        if device.lower() in boot_devices:
            return True
        else:
            self.logger.error("Device %s does not match any of the existing for host %s" % (device, self.host))
            return False

    def polling_host_state(self, state, equals=True):
        state_str = "Not %s" % state if not equals else state
        self.logger.info("Polling for host state: %s" % state_str)
        desired_state = False
        count = 0
        while not desired_state and count < self.retries:
            count += 1
            current_state = self.get_power_state()
            self.progress_bar(count, self.retries, current_state)
            if equals:
                desired_state = current_state.lower() == state.lower()
            else:
                desired_state = current_state.lower() != state.lower()
            time.sleep(5)

        return desired_state

    def change_boot(self, host_type, interfaces_path, pxe=False):

        if interfaces_path:
            if not os.path.exists(interfaces_path):
                self.logger.error("No such file or directory: %s." % interfaces_path)
                sys.exit(1)
        else:
            self.logger.error(
                "You must provide a path to the interfaces yaml via `-i` optional argument."
            )
            sys.exit(1)

        _type = self.get_host_type(interfaces_path)
        if _type and _type.lower() != host_type.lower():
            self.clear_job_queue()
            self.reset_idrac()
            self.logger.warning("Waiting for host to be up.")
            host_up = self.polling_host_state("On")
            if host_up:
                if host_type:
                    if host_type.lower() not in ("foreman", "director"):
                        raise argparse.ArgumentTypeError('Expected values for -t argument are "foreman" or "director"')

                    self.change_boot_order(interfaces_path, host_type)

                if pxe:
                    self.set_next_boot_pxe()

                job_id = self.create_bios_config_job(BIOS_URI)
                if job_id:
                    self.get_job_status(job_id)

                self.reboot_server()
            else:
                self.logger.error("Couldn't communicate with host after %s attempts." % self.retries)
                sys.exit(1)
        else:
            self.logger.warning(
                "No changes were made since the boot order already matches the requested."
            )
        return True

    def get_firmware_inventory(self):
        self.logger.debug("Getting firmware inventory for all devices supported by iDRAC.")

        _url = 'https://%s/redfish/v1/UpdateService/FirmwareInventory/' % self.host
        try:
            _response = requests.get(_url, auth=(self.username, self.password), verify=False)
        except (ConnectionError, ConnectTimeout, ReadTimeout) as ex:
            self.logger.debug(ex)
            self.logger.error("Failed to communicate with server.")
            sys.exit(1)

        data = _response.json()
        installed_devices = []
        for device in data[u'Members']:
            a = device[u'@odata.id']
            a = a.replace("/redfish/v1/UpdateService/FirmwareInventory/", "")
            if "Installed" in a:
                installed_devices.append(a)

        for device in installed_devices:
            self.logger.debug("Getting device info for %s" % device)
            _url = 'https://%s/redfish/v1/UpdateService/FirmwareInventory/%s' % (self.host, device)
            try:
                _response = requests.get(_url, auth=(self.username, self.password), verify=False)
            except (ConnectionError, ConnectTimeout, ReadTimeout) as ex:
                self.logger.debug(ex)
                self.logger.error("Failed to get data for %s." % device)
                continue

            data = _response.json()
            for info in data.items():
                if "odata" not in info[0] and "Description" not in info[0]:
                    self.logger.info("%s: %s" % (info[0], info[1]))

            self.logger.info("*" * 48)

    def export_configuration(self):
        _url = 'https://%s/redfish/v1/Managers/iDRAC.Embedded.1/Actions/Oem/EID_674_Manager.ExportSystemConfiguration' % self.host
        _payload = {"ExportFormat": "XML", "ShareParameters": {"Target": "ALL"},
                    "IncludeInExport": "IncludeReadOnly,IncludePasswordHashValues"}
        _headers = {'content-type': 'application/json'}
        job_id = self.create_job(_url, _payload, _headers, 202)

        for _ in range(RETRIES):
            try:
                _response = requests.get('https://%s/redfish/v1/TaskService/Tasks/%s' % (self.host, job_id),
                                         auth=(self.username, self.password), verify=False)
            except (ConnectionError, ConnectTimeout, ReadTimeout) as ex:
                self.logger.debug(ex)
                self.logger.error("Failed to communicate with server.")
                continue

            data = _response.__dict__
            if "<SystemConfiguration Model" in str(data):
                self.logger.info("Export job ID %s successfully completed." % job_id)

                filename = "%s_export.xml" % self.host

                with open(filename, "w") as _file:
                    _content = data["_content"]
                    _file.writelines(["%s\n" % line.decode("utf-8") for line in _content.split(b"\n")])

                self.logger.info("Exported attributes saved in file: %s" % filename)

                return
            else:
                pass

            status_code = _response.status_code
            data = _response.json()

            if status_code == 202 or status_code == 200:
                self.logger.info("JobStatus not completed, current status: \"%s\", percent complete: \"%s\"" % (
                    data[u'Oem'][u'Dell'][u'Message'], data[u'Oem'][u'Dell'][u'PercentComplete']))
                time.sleep(1)
            else:
                self.logger.error("Execute job ID command failed, error code is: %s" % status_code)
                sys.exit(1)

        self.logger.error("Could not export settings after %s attempts." % RETRIES)


def execute_badfish(_host, _args):
    username = _args["u"]
    password = _args["p"]
    host_type = _args["t"]
    log = _args["log"]
    interfaces_path = _args["i"]
    pxe = _args["pxe"]
    device = _args["boot_to"]
    reboot_only = _args["reboot_only"]
    racreset = _args["racreset"]
    check_boot = _args["check_boot"]
    firmware_inventory = _args["firmware_inventory"]
    export_configuration = _args["export_configuration"]
    clear_jobs = _args["clear_jobs"]
    verbose = _args["verbose"]
    retries = _args["retries"]

    log_level = DEBUG if verbose else INFO

    badfish = Badfish(_host, username, password, retries, log, log_level)

    if reboot_only:
        badfish.reboot_server()
    elif racreset:
        badfish.reset_idrac()
    elif device:
        badfish.boot_to(device)
    elif check_boot:
        badfish.check_boot(interfaces_path)
    elif firmware_inventory:
        badfish.get_firmware_inventory()
    elif export_configuration:
        badfish.export_configuration()
    elif clear_jobs:
        badfish.clear_job_queue()
    else:
        badfish.change_boot(host_type, interfaces_path, pxe)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Client tool for changing boot order via Redfish API.")
    parser.add_argument("-H", help="iDRAC host address")
    parser.add_argument("-u", help="iDRAC username", required=True)
    parser.add_argument("-p", help="iDRAC password", required=True)
    parser.add_argument("-i", help="Path to iDRAC interfaces yaml", default=None)
    parser.add_argument("-t", help="Type of host. Accepts: foreman, director")
    parser.add_argument("-l", "--log", help="Optional argument for logging results to a file")
    parser.add_argument("--host-list", help="Path to a plain text file with a list of hosts.", default=None)
    parser.add_argument("--pxe", help="Set next boot to one-shot boot PXE", action="store_true")
    parser.add_argument("--boot-to", help="Set next boot to one-shot boot to a specific device")
    parser.add_argument("--reboot-only", help="Flag for only rebooting the host", action="store_true")
    parser.add_argument("--racreset", help="Flag for iDRAC reset", action="store_true")
    parser.add_argument("--check-boot", help="Flag for checking the host boot order", action="store_true")
    parser.add_argument("--firmware-inventory", help="Get firmware inventory", action="store_true")
    parser.add_argument("--export-configuration", help="Export system configuration to XML", action="store_true")
    parser.add_argument("--clear-jobs", help="Clear any schedule jobs from the queue", action="store_true")
    parser.add_argument("-v", "--verbose", help="Verbose output", action="store_true")
    parser.add_argument("-r", "--retries", help="Number of retries for executing actions.", default=RETRIES)
    args = vars(parser.parse_args(argv))

    host_list = args["host_list"]
    host = args["H"]

    if host_list:
        with open(host_list, "r") as _file:
            for _host in _file.readlines():
                execute_badfish(_host, args)
    elif not host:
        raise argparse.ArgumentError("You must specify at least either a host (-H) or a host list (--host-list).")
    else:
        execute_badfish(host)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nBadfish terminated.")
