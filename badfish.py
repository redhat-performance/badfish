#!/usr/bin/env python3

from core.logger import Logger
from logging import FileHandler, Formatter, DEBUG, INFO
from requests.exceptions import RequestException

import json
import argparse
import os
import re
import requests
import sys
import time
import warnings
import yaml

warnings.filterwarnings("ignore")

RETRIES = 15


class Badfish:
    def __init__(self, _host, _username, _password, logger, _retries=RETRIES):
        self.host = _host
        self.username = _username
        self.password = _password
        self.retries = _retries
        self.host_uri = "https://%s" % _host
        self.redfish_uri = "/redfish/v1"
        self.root_uri = "%s%s" % (self.host_uri, self.redfish_uri)
        self.logger = logger
        self.system_resource = self.find_systems_resource()
        self.manager_resource = self.find_managers_resource()
        self.bios_uri = "%s/Bios/Settings" % self.system_resource[len(self.redfish_uri):]

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

    def get_request(self, uri, _continue=False):
        try:
            _response = requests.get(uri, auth=(self.username, self.password), verify=False, timeout=60)
        except RequestException:
            self.logger.exception("Failed to communicate with server.")
            if _continue:
                return
            else:
                sys.exit(1)
        return _response

    def post_request(self, uri, payload, headers):
        try:
            _response = requests.post(
                uri,
                data=json.dumps(payload),
                headers=headers,
                verify=False,
                auth=(self.username, self.password)
            )
        except RequestException:
            self.logger.exception("Failed to communicate with server.")
            sys.exit(1)
        return _response

    def patch_request(self, uri, payload, headers, _continue=False):
        try:
            _response = requests.patch(
                uri,
                data=json.dumps(payload),
                headers=headers,
                verify=False,
                auth=(self.username, self.password)
            )
        except RequestException:
            self.logger.exception("Failed to communicate with server.")
            if _continue:
                return
            else:
                sys.exit(1)
        return _response

    def delete_request(self, uri, headers):
        try:
            requests.delete(
                uri,
                headers=headers,
                verify=False,
                auth=(self.username, self.password)
            )
        except RequestException:
            self.logger.exception("Failed to communicate with server.")
            sys.exit(1)
        return

    def get_boot_seq(self):
        bios_boot_mode = self.get_bios_boot_mode()
        if bios_boot_mode == "Uefi":
            return "UefiBootSeq"
        else:
            return "BootSeq"

    def get_bios_boot_mode(self):
        self.logger.debug("Getting bios boot mode.")
        _uri = "%s%s/Bios" % (self.host_uri, self.system_resource)
        _response = self.get_request(_uri)

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
        _uri = "%s%s/BootSources" % (self.host_uri, self.system_resource)
        _response = self.get_request(_uri)

        data = _response.json()
        if "Attributes" in data:
            return data[u"Attributes"][_boot_seq]
        else:
            self.logger.debug(data)
            self.logger.error("Boot order modification is not supported by this host.")
            sys.exit(1)

    def get_job_queue(self):
        self.logger.debug("Getting job queue.")
        _url = "%s%s/Jobs" % (self.host_uri, self.manager_resource)
        _response = self.get_request(_url)

        data = _response.json()
        data = str(data)
        job_queue = re.findall("[JR]ID_.+?'", data)
        jobs = [job.strip("}").strip("\"").strip("'") for job in job_queue]
        return jobs

    def get_job_status(self, _job_id):
        self.logger.debug("Getting job status.")
        _uri = "%s%s/Jobs/%s" % (self.host_uri, self.manager_resource, _job_id)

        for _ in range(self.retries):
            _response = self.get_request(_uri, _continue=True)
            if not _response:
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
            if host_model.startswith("r"):
                host_model = host_model[1:]
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

    def find_systems_resource(self):
        response = self.get_request(self.root_uri)

        if response.status_code == 401:
            self.logger.error("Failed to authenticate. Verify your credentials.")
            sys.exit(1)

        if response:
            data = response.json()
            if 'Systems' not in data:
                self.logger.error("Systems resource not found")
                sys.exit(1)
            else:
                systems = data["Systems"]["@odata.id"]
                _response = self.get_request(self.host_uri + systems)
                if _response:
                    data = _response.json()
                    if data.get(u'Members'):
                        for member in data[u'Members']:
                            systems_service = member[u'@odata.id']
                            self.logger.info("Systems service: %s." % systems_service)
                            return systems_service
                    else:
                        self.logger.error("ComputerSystem's Members array is either empty or missing")
                        sys.exit(1)

    def find_managers_resource(self):
        response = self.get_request(self.root_uri)
        if response:
            data = response.json()
            if 'Managers' not in data:
                self.logger.error("Managers resource not found")
                sys.exit(1)
            else:
                managers = data["Managers"]["@odata.id"]
                response = self.get_request(self.host_uri + managers)
                if response:
                    data = response.json()
                    if data.get(u'Members'):
                        for member in data[u'Members']:
                            managers_service = member[u'@odata.id']
                            self.logger.info("Managers service: %s." % managers_service)
                            return managers_service
                    else:
                        self.logger.error("Manager's Members array is either empty or missing")
                        sys.exit(1)

    def get_power_state(self):
        _uri = '%s%s' % (self.host_uri, self.system_resource)
        self.logger.debug("url: %s" % _uri)

        _response = self.get_request(_uri, _continue=True)
        if not _response:
            return "Down"

        if _response.ok:
            data = _response.json()
        else:
            self.logger.debug("Couldn't get power state. Retrying.")
            return "Down"
        self.logger.debug("Current server power state is: %s." % data[u'PowerState'])

        return data[u'PowerState']

    def change_boot(self, host_type, interfaces_path, pxe=False):
        if host_type.lower() not in ("foreman", "director"):
            self.logger.error('Expected values for -t argument are "foreman" or "director"')
            sys.exit(1)

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
        if (_type and _type.lower() != host_type.lower()) or not _type:
            self.clear_job_queue()
            self.logger.warning("Waiting for host to be up.")
            host_up = self.polling_host_state("On")
            if host_up:
                self.change_boot_order(interfaces_path, host_type)

                if pxe:
                    self.set_next_boot_pxe()

                job_id = self.create_bios_config_job(self.bios_uri)
                if job_id:
                    self.get_job_status(job_id)

                self.reset_idrac()
                self.polling_host_state("On")
                self.reboot_server()

            else:
                self.logger.error("Couldn't communicate with host after %s attempts." % self.retries)
                sys.exit(1)
        else:
            self.logger.warning(
                "No changes were made since the boot order already matches the requested."
            )
        return True

    def change_boot_order(self, _interfaces_path, _host_type):
        with open(_interfaces_path, "r") as f:
            try:
                definitions = yaml.safe_load(f)
            except yaml.YAMLError as ex:
                self.logger.error(ex)
                sys.exit(1)

        host_model = self.host.split(".")[0].split("-")[-1]
        if host_model.startswith("r"):
            host_model = host_model[1:]
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
        boot_sources_uri = "%s/BootSources/Settings" % self.system_resource
        url = "%s%s" % (self.host_uri, boot_sources_uri)
        payload = {"Attributes": {_boot_seq: boot_devices}}
        headers = {"content-type": "application/json"}
        response = None
        _status_code = 400

        for _ in range(self.retries):
            if _status_code != 200:
                response = self.patch_request(url, payload, headers, True)
                if response:
                    _status_code = response.status_code
            else:
                break

        if _status_code == 200:
            self.logger.info("PATCH command passed to update boot order.")
        else:
            self.logger.error("There was something wrong with your request.")

            if response:
                self.error_handler(response)

    def set_next_boot_pxe(self):
        _url = "%s%s" % (self.host_uri, self.system_resource)
        _payload = {"Boot": {"BootSourceOverrideTarget": "Pxe"}}
        _headers = {"content-type": "application/json"}
        _response = self.patch_request(_url, _payload, _headers)

        time.sleep(5)

        if _response.status_code == 200:
            self.logger.info('PATCH command passed to set next boot onetime boot device to: "%s".' % "Pxe")
        else:
            self.logger.error("Command failed, error code is %s." % _response.status_code)

            self.error_handler(_response)

    def check_supported_idrac_version(self):
        _url = "%s/Dell/Managers/iDRAC.Embedded.1/DellJobService/" % self.root_uri
        _response = self.get_request(_url)
        if _response.status_code != 200:
            self.logger.warning("iDRAC version installed does not support DellJobService")
            return False

        return True

    def delete_job_queue(self):
        _url = "%s/Dell/Managers/iDRAC.Embedded.1/DellJobService/Actions/DellJobService.DeleteJobQueue" % self.root_uri
        _payload = {"JobID": "JID_CLEARALL"}
        _headers = {'content-type': 'application/json'}
        response = self.post_request(_url, _payload, _headers)
        if response.status_code == 200:
            self.logger.info("Job queue for iDRAC %s successfully cleared." % self.host)
        else:
            self.logger.error("Job queue not cleared, there was something wrong with your request.")
            sys.exit(1)

    def clear_job_list(self, _job_queue):
        _url = "%s%s/Jobs" % (self.host_uri, self.manager_resource)
        _headers = {"content-type": "application/json"}
        self.logger.warning("Clearing job queue for job IDs: %s." % _job_queue)
        for _job in _job_queue:
            job = _job.strip("'")
            url = "/".join([_url, job])
            self.delete_request(url, _headers)
        job_queue = self.get_job_queue()
        if not job_queue:
            self.logger.info("Job queue for iDRAC %s successfully cleared." % self.host)
        else:
            self.logger.error("Job queue not cleared, current job queue contains jobs: %s." % job_queue)
            sys.exit(1)

    def clear_job_queue(self):
        _job_queue = self.get_job_queue()
        if _job_queue:
            if self.check_supported_idrac_version():
                self.delete_job_queue()
            else:
                self.clear_job_list(_job_queue)
        else:
            self.logger.warning(
                "Job queue already cleared for iDRAC %s, DELETE command will not execute." % self.host
            )

    def create_job(self, _url, _payload, _headers, expected=200):
        _response = self.post_request(_url, _payload, _headers)

        status_code = _response.status_code

        if status_code == expected:
            self.logger.info("POST command passed to create target config job.")
        else:
            self.logger.error("POST command failed to create BIOS config job, status code is %s." % status_code)

            self.error_handler(_response)

        convert_to_string = str(_response.__dict__)
        job_id_search = re.search("[RJ]ID_.+?,", convert_to_string).group()
        _job_id = re.sub("[,']", "", job_id_search).strip("}").strip("\"").strip("'")
        self.logger.info("%s job ID successfully created." % _job_id)
        return _job_id

    def create_bios_config_job(self, uri):
        _url = "%s%s/Jobs" % (self.host_uri, self.manager_resource)
        _payload = {"TargetSettingsURI": "%s%s" % (self.redfish_uri, uri)}
        _headers = {"content-type": "application/json"}
        return self.create_job(_url, _payload, _headers)

    def send_reset(self, reset_type):
        _url = "%s%s/Actions/ComputerSystem.Reset" % (self.host_uri, self.system_resource)
        _payload = {"ResetType": reset_type}
        _headers = {"content-type": "application/json"}
        _response = self.post_request(_url, _payload, _headers)

        status_code = _response.status_code
        if status_code in [200, 204]:
            self.logger.info(
                "Command passed to %s server, code return is %s." % (reset_type, status_code)
            )
            time.sleep(10)
        elif status_code == 409:
            self.logger.warning(
                "Command failed to %s server, host appears to be already in that state." % reset_type
            )
        else:
            self.logger.error(
                "Command failed to %s server, status code is: %s." % (reset_type, status_code)
            )

            self.error_handler(_response)

    def reboot_server(self, graceful=True):
        self.logger.debug("Rebooting server: %s." % self.host)
        power_state = self.get_power_state()
        if power_state.lower() == "on":
            if graceful:
                self.send_reset("GracefulRestart")

                host_down = self.polling_host_state("Off")

                if not host_down:
                    self.logger.warning(
                        "Unable to graceful shutdown the server, will perform forced shutdown now."
                    )
                    self.send_reset("ForceOff")
            else:
                self.send_reset("ForceOff")

            host_not_down = self.polling_host_state("Down", False)

            if host_not_down:
                self.send_reset("On")

        elif power_state.lower() == "off":
            self.send_reset("On")
        return True

    def reset_idrac(self):
        self.logger.debug("Running reset iDRAC.")
        _url = "%s%s/Actions/Manager.Reset/" % (self.host_uri, self.manager_resource)
        _payload = {"ResetType": "GracefulRestart"}
        _headers = {'content-type': 'application/json'}
        self.logger.debug("url: %s" % _url)
        self.logger.debug("payload: %s" % _payload)
        self.logger.debug("headers: %s" % _headers)
        _response = self.post_request(_url, _payload, _headers)

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
            self.send_one_time_boot(device)
            job_id = self.create_bios_config_job(self.bios_uri)
            if job_id:
                self.get_job_status(job_id)
        else:
            sys.exit(1)
        return True

    def boot_to_type(self, host_type, _interfaces_path):
        if host_type.lower() not in ("foreman", "director"):
            self.logger.error('Expected values for -t argument are "foreman" or "director"')
            sys.exit(1)

        if _interfaces_path:
            if not os.path.exists(_interfaces_path):
                self.logger.error("No such file or directory: %s." % _interfaces_path)
                sys.exit(1)

        device = self.get_host_type_boot_device(host_type, _interfaces_path)

        self.boot_to(device)

    def send_one_time_boot(self, device):
        _url = "%s%s" % (self.root_uri, self.bios_uri)
        _payload = {"Attributes": {"OneTimeBootMode": "OneTimeBootSeq", "OneTimeBootSeqDev": device}}
        _headers = {"content-type": "application/json"}
        _first_reset = False
        for i in range(self.retries):
            _response = self.patch_request(_url, _payload, _headers)
            status_code = _response.status_code
            if status_code == 200:
                self.logger.info("Command passed to set BIOS attribute pending values.")
                break
            else:
                self.logger.error("Command failed, error code is: %s." % status_code)
                if status_code == 503 and i - 1 != self.retries:
                    self.logger.info("Retrying to send one time boot.")
                    continue
                elif status_code == 400:
                    self.clear_job_queue()
                    if not _first_reset:
                        self.reset_idrac()
                        self.polling_host_state("On")
                    continue
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
        boot_devices = [_device["Name"].lower() for _device in devices]
        if device.lower() in boot_devices:
            return True
        else:
            self.logger.error("Device %s does not match any of the existing for host %s" % (device, self.host))
            return False

    def polling_host_state(self, state, equals=True):
        state_str = "Not %s" % state if not equals else state
        self.logger.info("Polling for host state: %s" % state_str)
        desired_state = False
        for count in range(self.retries):
            current_state = self.get_power_state()
            if equals:
                desired_state = current_state.lower() == state.lower()
            else:
                desired_state = current_state.lower() != state.lower()
            time.sleep(5)
            if desired_state:
                self.progress_bar(self.retries, self.retries, current_state)
                break
            self.progress_bar(count, self.retries, current_state)

        return desired_state

    def get_firmware_inventory(self):
        self.logger.debug("Getting firmware inventory for all devices supported by iDRAC.")

        _url = '%s/UpdateService/FirmwareInventory/' % self.root_uri
        _response = self.get_request(_url)

        try:
            data = _response.json()
        except ValueError:
            self.logger.error("Not able to access Firmware inventory.")
            sys.exit(1)
        installed_devices = []
        if "error" in data:
            self.logger.debug(data["error"])
            self.logger.error("Not able to access Firmware inventory.")
            sys.exit(1)
        for device in data[u'Members']:
            a = device[u'@odata.id']
            a = a.replace("/redfish/v1/UpdateService/FirmwareInventory/", "")
            if "Installed" in a:
                installed_devices.append(a)

        for device in installed_devices:
            self.logger.debug("Getting device info for %s" % device)
            _uri = '%s/UpdateService/FirmwareInventory/%s' % (self.root_uri, device)

            _response = self.get_request(_uri, _continue=True)
            if not _response:
                continue

            data = _response.json()
            for info in data.items():
                if "odata" not in info[0] and "Description" not in info[0]:
                    self.logger.info("%s: %s" % (info[0], info[1]))

            self.logger.info("*" * 48)

    def export_configuration(self):
        _url = '%s%s/Actions/' \
               'Oem/EID_674_Manager.ExportSystemConfiguration' % (self.host_uri, self.manager_resource)
        _payload = {"ExportFormat": "XML", "ShareParameters": {"Target": "ALL"},
                    "IncludeInExport": "IncludeReadOnly,IncludePasswordHashValues"}
        _headers = {'content-type': 'application/json'}
        job_id = self.create_job(_url, _payload, _headers, 202)

        _uri = '%s/TaskService/Tasks/%s' % (self.root_uri, job_id)

        for _ in range(self.retries):

            _response = self.get_request(_uri, _continue=True)
            if not _response:
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

        self.logger.error("Could not export settings after %s attempts." % self.retries)

    def get_host_type_boot_device(self, host_type, _interfaces_path):
        if _interfaces_path:
            with open(_interfaces_path, "r") as f:
                try:
                    definitions = yaml.safe_load(f)
                except yaml.YAMLError as ex:
                    self.logger.error("Couldn't read file: %s" % _interfaces_path)
                    self.logger.debug(ex)
                    sys.exit(1)

            host_model = self.host.split(".")[0].split("-")[-1]
            if host_model.startswith("r"):
                host_model = host_model[1:]
            return definitions["%s_%s_interfaces" % (host_type, host_model)].split(",")[0]
        return None


def execute_badfish(_host, _args, logger):
    username = _args["u"]
    password = _args["p"]
    host_type = _args["t"]
    interfaces_path = _args["i"]
    pxe = _args["pxe"]
    device = _args["boot_to"]
    boot_to_type = _args["boot_to_type"]
    reboot_only = _args["reboot_only"]
    racreset = _args["racreset"]
    check_boot = _args["check_boot"]
    firmware_inventory = _args["firmware_inventory"]
    export_configuration = _args["export_configuration"]
    clear_jobs = _args["clear_jobs"]
    retries = _args["retries"]

    badfish = Badfish(_host, username, password, logger, retries)

    if _args["host_list"]:
        badfish.logger.info("Executing actions on host: %s" % _host)

    if reboot_only:
        badfish.reboot_server()
    elif racreset:
        badfish.reset_idrac()
    elif device:
        badfish.boot_to(device)
    elif boot_to_type:
        badfish.boot_to_type(boot_to_type, interfaces_path)
    elif check_boot:
        badfish.check_boot(interfaces_path)
    elif firmware_inventory:
        badfish.get_firmware_inventory()
    elif export_configuration:
        badfish.export_configuration()
    elif clear_jobs:
        badfish.clear_job_queue()
    elif host_type:
        badfish.change_boot(host_type, interfaces_path, pxe)

    if pxe and not host_type:
        badfish.set_next_boot_pxe()

    if _args["host_list"]:
        badfish.logger.info("*" * 48)


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
    parser.add_argument("--boot-to-type", help="Set next boot to one-shot boot to either director or foreman")
    parser.add_argument("--reboot-only", help="Flag for only rebooting the host", action="store_true")
    parser.add_argument("--racreset", help="Flag for iDRAC reset", action="store_true")
    parser.add_argument("--check-boot", help="Flag for checking the host boot order", action="store_true")
    parser.add_argument("--firmware-inventory", help="Get firmware inventory", action="store_true")
    parser.add_argument("--export-configuration", help="Export system configuration to XML", action="store_true")
    parser.add_argument("--clear-jobs", help="Clear any schedule jobs from the queue", action="store_true")
    parser.add_argument("-v", "--verbose", help="Verbose output", action="store_true")
    parser.add_argument("-r", "--retries", help="Number of retries for executing actions.", default=RETRIES)
    args = vars(parser.parse_args(argv))

    log_level = DEBUG if args["verbose"] else INFO

    logger = Logger()
    logger.start(level=log_level)

    if args["log"]:
        file_handler = FileHandler(args["log"])
        file_handler.setFormatter(Formatter(logger.LOGFMT))
        file_handler.setLevel(DEBUG)
        logger.addHandler(file_handler)

    host_list = args["host_list"]
    host = args["H"]

    if host_list:
        try:
            with open(host_list, "r") as _file:
                for _host in _file.readlines():
                    try:
                        execute_badfish(_host.strip(), args, logger)
                    except SystemExit:
                        continue
        except IOError as ex:
            logger.debug(ex)
            logger.error("There was something wrong reading from %s" % host_list)
    elif not host:
        logger.error("You must specify at least either a host (-H) or a host list (--host-list).")
    else:
        execute_badfish(host, args, logger)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nBadfish terminated.")
