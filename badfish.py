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


class Badfish:
    def __init__(self, _host, _username, _password, _retries):
        self.host = _host
        self.username = _username
        self.password = _password
        self.retries = _retries
        self.logger = Logger()

    @staticmethod
    def get_boot_seq(bios_boot_mode):
        if bios_boot_mode == "Uefi":
            return "UefiBootSeq"
        else:
            return "BootSeq"

    @staticmethod
    def progress_bar(value, end_value, state, bar_length=20):
        percent = float(value) / end_value
        arrow = '-' * int(round(percent * bar_length) - 1) + '>'
        spaces = ' ' * (bar_length - len(arrow))

        if state.lower() == "on":
            state = "On  \n"
        sys.stdout.write(
            "\r  Retrying: [{0}] {1}% - Host state: {2}".format(arrow + spaces, int(round(percent * 100)), state)
        )
        sys.stdout.flush()

    def get_bios_boot_mode(self):
        try:
            _response = requests.get(
                "https://%s/redfish/v1/Systems/System.Embedded.1/Bios" % self.host,
                verify=False,
                auth=(self.username, self.password),
            )
        except ConnectionError:
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

    def get_boot_devices(self, _boot_seq):
        _response = requests.get(
            "https://%s/redfish/v1/Systems/System.Embedded.1/BootSources" % self.host,
            verify=False,
            auth=(self.username, self.password),
        )
        data = _response.json()
        return data[u"Attributes"][_boot_seq]

    def change_boot_order(self, _interfaces_path, _host_type):
        with open(_interfaces_path, "r") as f:
            try:
                definitions = yaml.safe_load(f)
            except yaml.YAMLError as ex:
                self.logger.error(ex)
                sys.exit(1)

        host_model = self.host.split(".")[0].split("-")[-1]
        interfaces = definitions["%s_%s_interfaces" % (_host_type, host_model)].split(",")

        bios_boot_mode = self.get_bios_boot_mode()
        boot_seq = self.get_boot_seq(bios_boot_mode)
        boot_devices = self.get_boot_devices(boot_seq)
        change = False
        for i in range(len(interfaces)):
            for device in boot_devices:
                if interfaces[i] == device[u"Name"]:
                    if device[u"Index"] != i:
                        device[u"Index"] = i
                        change = True
                    break

        if change:
            url = "https://%s%s" % (self.host, BOOT_SOURCES_URI)
            payload = {"Attributes": {boot_seq: boot_devices}}
            headers = {"content-type": "application/json"}
            _status_code = 400
            count = 0
            while _status_code != 200 and count < self.retries:
                try:
                    count += 1
                    response = requests.patch(
                        url, data=json.dumps(payload), headers=headers, verify=False, auth=(self.username, self.password)
                    )
                except ConnectionError:
                    self.logger.error("Failed to communicate with server.")
                    continue
                _status_code = response.status_code
            if _status_code == 200:
                self.logger.info("PATCH command passed to update boot order.")
            else:
                self.logger.error("There was something wrong with your request.")
                if response:
                    try:
                        data = response.json()
                    except ValueError:
                        return
                    if "error" in data:
                        detail_message = str(data["error"]["@Message.ExtendedInfo"][0]["Message"])
                        self.logger.error(detail_message)
        else:
            self.logger.warning("No changes were made since the boot order already matches the requested.")
            sys.exit()
        return

    def set_next_boot_pxe(self):
        _url = "https://%s/redfish/v1/Systems/System.Embedded.1" % self.host
        _payload = {"Boot": {"BootSourceOverrideTarget": "Pxe"}}
        _headers = {"content-type": "application/json"}
        _response = requests.patch(
            _url, data=json.dumps(_payload), headers=_headers, verify=False, auth=(self.username, self.password)
        )
        time.sleep(5)
        if _response.status_code == 200:
            self.logger.info('PATCH command passed to set next boot onetime boot device to: "%s".' % "Pxe")
        else:
            self.logger.error("Command failed, error code is %s." % _response.status_code)
            detail_message = str(_response.__dict__)
            self.logger.error(detail_message)
            sys.exit(1)
        return

    def clear_job_queue(self, _job_queue):
        _url = "https://%s/redfish/v1/Managers/iDRAC.Embedded.1/Jobs" % self.host
        _headers = {"content-type": "application/json"}
        if not _job_queue:
            self.logger.warning(
                "Job queue already cleared for iDRAC %s, DELETE command will not execute." % self.host
            )
            return
        self.logger.warning("Clearing job queue for job IDs: %s." % _job_queue)
        for _job in _job_queue:
            job = _job.strip("'")
            url = "%s/%s" % (_url, job)
            requests.delete(url, headers=_headers, verify=False, auth=(self.username, self.password))
        job_queue = self.get_job_queue()
        if not job_queue:
            self.logger.info("Job queue for iDRAC %s successfully cleared." % self.host)
        else:
            self.logger.error("Job queue not cleared, current job queue contains jobs: %s." % job_queue)
            sys.exit(1)
        return

    def get_job_queue(self):
        _url = "https://%s/redfish/v1/Managers/iDRAC.Embedded.1/Jobs" % self.host
        try:
            _response = requests.get(_url, auth=(self.username, self.password), verify=False)
        except ConnectionError:
            self.logger.error("Failed to communicate with server. Host appears to be down.")
            sys.exit(1)
        data = _response.json()
        data = str(data)
        job_queue = re.findall("JID_.+?'", data)
        jobs = [job.strip("'") for job in job_queue]
        return jobs

    def create_bios_config_job(self, uri):
        _url = "https://%s/redfish/v1/Managers/iDRAC.Embedded.1/Jobs" % self.host
        _payload = {"TargetSettingsURI": uri}
        _headers = {"content-type": "application/json"}
        _response = requests.post(
            _url, data=json.dumps(_payload), headers=_headers, verify=False, auth=(self.username, self.password)
        )
        status_code = _response.status_code

        if status_code == 200:
            self.logger.info("POST command passed to create target config job, status code 200 returned.")
        else:
            self.logger.error("POST command failed to create BIOS config job, status code is %s." % status_code)
            try:
                data = _response.json()
            except ValueError:
                return None
            if "error" in data:
                detail_message = str(data["error"]["@Message.ExtendedInfo"][0]["Message"])
                self.logger.error(detail_message)
            return None
        convert_to_string = str(_response.__dict__)
        job_id_search = re.search("JID_.+?,", convert_to_string).group()
        _job_id = re.sub("[,']", "", job_id_search)
        self.logger.info("%s job ID successfully created." % _job_id)
        return _job_id

    def get_job_status(self, _job_id):
        retries = 10
        for _ in range(retries):
            req = requests.get(
                "https://%s/redfish/v1/Managers/iDRAC.Embedded.1/Jobs/%s" % (self.host, _job_id),
                verify=False,
                auth=(self.username, self.password),
            )
            status_code = req.status_code
            if status_code == 200:
                self.logger.info("Command passed to check job status, code 200 returned.")
                time.sleep(10)
            else:
                self.logger.error("Command failed to check job status, return code is %s." % status_code)
                self.logger.error("Extended Info Message: {0}.".format(req.json()))
                sys.exit(1)
            data = req.json()
            if data[u"Message"] == "Task successfully scheduled.":
                self.logger.info("Job id %s successfully scheduled." % _job_id)
                return
            else:
                self.logger.warning("JobStatus not scheduled, current status is: %s." % data[u"Message"])
        self.logger.error("Not able to successfully schedule the job.")
        sys.exit(1)

    def reboot_server(self):
        _response = requests.get(
            "https://%s/redfish/v1/Systems/System.Embedded.1/" % self.host,
            verify=False,
            auth=(self.username, self.password),
        )

        data = _response.json()
        self.logger.warning("Current server power state is: %s." % data[u"PowerState"])
        if data[u"PowerState"] == "On":
            _url = "https://%s/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset" % self.host
            _payload = {"ResetType": "GracefulRestart"}
            _headers = {"content-type": "application/json"}
            _response = requests.post(
                _url, data=json.dumps(_payload), headers=_headers, verify=False, auth=(self.username, self.password)
            )
            status_code = _response.status_code
            if status_code == 204:
                self.logger.info(
                    "Command passed to gracefully restart server, code return is %s." % status_code
                )
                time.sleep(3)
            else:
                self.logger.error(
                    "Command failed to gracefully restart server, status code is: %s." % status_code
                )
                self.logger.error("Extended Info Message: {0}.".format(_response.json()))
                sys.exit(1)
            count = 0
            while True:
                _response = requests.get(
                    "https://%s/redfish/v1/Systems/System.Embedded.1/" % self.host,
                    verify=False,
                    auth=(self.username, self.password),
                )
                data = _response.json()
                if data[u"PowerState"] == "Off":
                    self.logger.info("GET command passed to verify server is in OFF state.")
                    break
                elif count == 10:
                    self.logger.warning(
                        "Unable to graceful shutdown the server, will perform forced shutdown now."
                    )
                    _url = "https://%s/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset" % self.host
                    _payload = {"ResetType": "ForceOff"}
                    _headers = {"content-type": "application/json"}
                    _response = requests.post(
                        _url,
                        data=json.dumps(_payload),
                        headers=_headers,
                        verify=False,
                        auth=(self.username, self.password),
                    )
                    status_code = _response.status_code
                    if status_code == 204:
                        self.logger.info(
                            "Command passed to forcefully power OFF server, code return is %s." % status_code
                        )
                        time.sleep(10)
                    else:
                        self.logger.error(
                            "Command failed to gracefully power OFF server, status code is: %s." % status_code
                        )
                        self.logger.error("Extended Info Message: {0}".format(_response.json()))
                        sys.exit(1)

                else:
                    time.sleep(1)
                    count += 1
                    continue

            _payload = {"ResetType": "On"}
            _headers = {"content-type": "application/json"}
            _response = requests.post(
                _url, data=json.dumps(_payload), headers=_headers, verify=False, auth=(self.username, self.password)
            )
            status_code = _response.status_code
            if status_code == 204:
                self.logger.info("Command passed to power ON server, code return is %s." % status_code)
            else:
                self.logger.error("Command failed to power ON server, status code is: %s." % status_code)

                try:
                    data = _response.json()
                except ValueError:
                    return None

                if "error" in data:
                    detail_message = str(data["error"]["@Message.ExtendedInfo"][0]["Message"])
                    self.logger.warning(detail_message)

                sys.exit(1)

        elif data[u"PowerState"] == "Off":
            _url = "https://%s/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset" % self.host
            _payload = {"ResetType": "On"}
            _headers = {"content-type": "application/json"}
            _response = requests.post(
                _url, data=json.dumps(_payload), headers=_headers, verify=False, auth=(self.username, self.password)
            )
            status_code = _response.status_code
            if status_code == 204:
                self.logger.info("Command passed to power ON server, code return is %s." % status_code)
            else:
                self.logger.error("Command failed to power ON server, status code is: %s." % status_code)
                self.logger.error("Extended Info Message: {0}.".format(_response.json()))
                sys.exit(1)
        else:
            self.logger.error("Unable to get current server power state to perform either reboot or power on.")
            sys.exit(1)

    def reset_idrac(self):
        _url = "https://%s/redfish/v1/Managers/iDRAC.Embedded.1/Actions/Manager.Reset/" % self.host
        _payload = {"ResetType": "GracefulRestart"}
        _headers = {'content-type': 'application/json'}
        _response = requests.post(
            _url, data=json.dumps(_payload), headers=_headers, verify=False, auth=(self.username, self.password)
        )
        status_code = _response.status_code
        if status_code == 204:
            self.logger.info("Status code %s returned for POST command to reset iDRAC." % status_code)
        else:
            data = _response.json()
            self.logger.error("Status code %s returned, error is: \n%s." % (status_code, data))
            sys.exit(1)
        time.sleep(15)

        self.logger.info("iDRAC will now reset and be back online within a few minutes.")

    def boot_to_device(self, _boot_to):
        _url = "https://%s%s" % (self.host, BIOS_URI)
        _payload = {"Attributes": {"OneTimeBootMode": "OneTimeBootSeq", "OneTimeBootSeqDev": _boot_to}}
        _headers = {"content-type": "application/json"}
        try:
            _response = requests.patch(
                _url, data=json.dumps(_payload), headers=_headers, verify=False, auth=(self.username, self.password)
            )
        except ConnectionError:
            self.logger.error("Failed to communicate with server.")
            sys.exit(1)
        status_code = _response.status_code
        if status_code == 200:
            self.logger.info("Command passed to set BIOS attribute pending values.")
        else:
            self.logger.error("Command failed, error code is: %s." % status_code)
            self.logger.error(str(_response.__dict__))
            sys.exit(1)

    def check_boot(self, _interfaces_path):
        bios_boot_mode = self.get_bios_boot_mode()
        boot_seq = self.get_boot_seq(bios_boot_mode)
        boot_devices = self.get_boot_devices(boot_seq)
        if _interfaces_path:

            with open(_interfaces_path, "r") as f:
                try:
                    definitions = yaml.safe_load(f)
                except yaml.YAMLError as ex:
                    self.logger.error(ex)
                    return 1

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
                    self.logger.info("Current boot order is set to '%s'." % _host)
                    return _host

            self.logger.warning("Current boot order does not match any of the given.")
            self.logger.info("Current boot order:")
            for device in sorted(boot_devices, key=lambda x: x[u"Index"]):
                self.logger.info("%s: %s" % (int(device[u"Index"]) + 1, device[u"Name"]))
            return

        else:
            self.logger.info("Current boot order:")
            for device in sorted(boot_devices, key=lambda x: x[u"Index"]):
                self.logger.info("%s: %s" % (int(device[u"Index"]) + 1, device[u"Name"]))
            return

    def get_power_state(self):
        _url = 'https://%s/redfish/v1/Systems/System.Embedded.1/' % self.host
        try:
            response = requests.get(_url, verify=False, auth=(self.username, self.password), timeout=20)
        except (ConnectionError, ConnectTimeout, ReadTimeout):
            self.logger.debug("Can't communicate with host.")
            return "Down"
        if response.ok:
            data = response.json()
        else:
            self.logger.debug("Couldn't get power state. Retrying.")
            return "Down"
        self.logger.debug("Current server power state is: %s." % data[u'PowerState'])

        return data[u'PowerState']

    def boot_to(self, device):
        jobs_queue = self.get_job_queue()
        if jobs_queue:
            self.clear_job_queue(jobs_queue)
        self.reset_idrac()
        powering_up = True
        count = 0
        while powering_up and count < self.retries:
            count += 1
            time.sleep(5)
            state = self.get_power_state()
            powering_up = state != "On"
            self.progress_bar(count, self.retries, state)
        if not powering_up:
            self.boot_to_device(device)
            job_id = self.create_bios_config_job(BIOS_URI)
            if job_id:
                self.get_job_status(job_id)
            self.reboot_server()
        else:
            self.logger.error("Couldn't communicate with host after %s attempts." % self.retries)
            return 1

    def change_boot(self, host_type, interfaces_path, pxe=False):
        jobs_queue = self.get_job_queue()
        if jobs_queue:
            self.clear_job_queue(jobs_queue)
        self.reset_idrac()
        self.logger.warning("Waiting for host to be up.")
        powering_up = True
        count = 0
        while powering_up and count < self.retries:
            count += 1
            time.sleep(5)
            state = self.get_power_state()
            powering_up = state != "On"
            self.progress_bar(count, self.retries, state)
        if not powering_up:
            if host_type:
                if host_type.lower() not in ("foreman", "director"):
                    raise argparse.ArgumentTypeError('Expected values for -t argument are "foreman" or "director"')

            if interfaces_path:
                if not os.path.exists(interfaces_path):
                    self.logger.error("No such file or directory: %s." % interfaces_path)
                    return 1
                if host_type:
                    self.change_boot_order(interfaces_path, host_type)
            else:
                self.logger.error(
                    "You must provide a path to the interfaces yaml via `-i` optional argument."
                )
                return 1
            if pxe:
                self.set_next_boot_pxe()
            job_id = self.create_bios_config_job(BIOS_URI)
            if job_id:
                self.get_job_status(job_id)
            self.reboot_server()
        else:
            self.logger.error("Couldn't communicate with host after %s attempts." % self.retries)
            return 1


def main(argv=None):
    parser = argparse.ArgumentParser(description="Client tool for changing boot order via Redfish API.")
    parser.add_argument("-H", help="iDRAC host address", required=True)
    parser.add_argument("-u", help="iDRAC username", required=True)
    parser.add_argument("-p", help="iDRAC password", required=True)
    parser.add_argument("-i", help="Path to iDRAC interfaces yaml", default=None)
    parser.add_argument("-t", help="Type of host. Accepts: foreman, director")
    parser.add_argument("-l", "--log", help="Optional argument for logging results to a file")
    parser.add_argument("--pxe", help="Set next boot to one-shot boot PXE", action="store_true")
    parser.add_argument("--boot-to", help="Set next boot to one-shot boot to a specific device")
    parser.add_argument("--reboot-only", help="Flag for only rebooting the host", action="store_true")
    parser.add_argument("--racreset", help="Flag for iDRAC reset", action="store_true")
    parser.add_argument("--check-boot", help="Flag for checking the host boot order", action="store_true")
    parser.add_argument("-v", "--verbose", help="Verbose output", action="store_true")
    parser.add_argument("-r", "--retries", help="Number of retries for executing actions.", default=15)
    args = vars(parser.parse_args(argv))
    host = args["H"]
    username = args["u"]
    password = args["p"]
    host_type = args["t"]
    log = args["log"]
    interfaces_path = args["i"]
    pxe = args["pxe"]
    device = args["boot_to"]
    reboot_only = args["reboot_only"]
    racreset = args["racreset"]
    check_boot = args["check_boot"]
    verbose = args["verbose"]
    retries = args["retries"]

    log_level = DEBUG if verbose else INFO

    badfish = Badfish(host, username, password, retries)
    badfish.logger.start(level=log_level)

    if log:
        file_handler = FileHandler(log)
        file_handler.setFormatter(Formatter(badfish.logger.LOGFMT))
        file_handler.setLevel(DEBUG)
        badfish.logger.addHandler(file_handler)

    if reboot_only:
        badfish.reboot_server()
    elif racreset:
        badfish.reset_idrac()
    elif device:
        badfish.boot_to(device)
    elif check_boot:
        badfish.check_boot(interfaces_path)
    else:
        _type = badfish.check_boot(interfaces_path)
        if _type and _type.lower() != host_type.lower():
            badfish.change_boot(host_type, interfaces_path, pxe)
        else:
            badfish.logger.warning(
                "No changes were made since the boot order already matches the requested."
            )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nBadfish terminated.")
