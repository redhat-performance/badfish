#!/usr/bin/env python3
import asyncio
import functools
import aiohttp
import json
import argparse
import os
import re
import sys
import warnings
import yaml

try:
    # Python 3.7 and newer, fast reentrant implementation
    # without task tracking (not needed for that when logging)
    from queue import SimpleQueue as Queue
except ImportError:
    from queue import Queue
from logging.handlers import QueueHandler, QueueListener

from async_lru import alru_cache
from logging import (
    Formatter,
    FileHandler,
    DEBUG,
    INFO,
    StreamHandler,
    getLogger,
)

warnings.filterwarnings("ignore")

RETRIES = 15


async def badfish_factory(_host, _username, _password, _logger, _retries, _loop=None):
    badfish = Badfish(_host, _username, _password, _logger, _retries, _loop)
    await badfish.init()
    return badfish


class BadfishException(Exception):
    pass


class Badfish:
    def __init__(self, _host, _username, _password, _logger, _retries, _loop=None):
        self.host = _host
        self.username = _username
        self.password = _password
        self.retries = _retries
        self.host_uri = "https://%s" % _host
        self.redfish_uri = "/redfish/v1"
        self.root_uri = "%s%s" % (self.host_uri, self.redfish_uri)
        self.logger = _logger
        self.semaphore = asyncio.Semaphore(50)
        if not _loop:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = _loop

        self.system_resource = None
        self.manager_resource = None
        self.bios_uri = None
        self.boot_devices = None

    async def init(self):
        await self.validate_credentials()
        self.system_resource = await self.find_systems_resource()
        self.manager_resource = await self.find_managers_resource()
        self.bios_uri = (
            "%s/Bios/Settings" % self.system_resource[len(self.redfish_uri) :]
        )

    @staticmethod
    def progress_bar(value, end_value, state, bar_length=20):
        ratio = float(value) / end_value
        arrow = "-" * int(round(ratio * bar_length) - 1) + ">"
        spaces = " " * (bar_length - len(arrow))
        percent = int(round(ratio * 100))

        if state.lower() == "on":
            state = "On  "
        ret = "\r" if percent != 100 else "\n"
        sys.stdout.write(
            "\r- POLLING: [{0}] {1}% - Host state: {2}{3}".format(
                arrow + spaces, percent, state, ret
            )
        )
        sys.stdout.flush()

    async def error_handler(self, _response):
        try:
            raw = await _response.text("utf-8", "ignore")
            data = json.loads(raw.strip())
        except ValueError:
            self.logger.error("Error reading response from host.")
            raise BadfishException

        if "error" in data:
            detail_message = str(data["error"]["@Message.ExtendedInfo"][0]["Message"])
            self.logger.warning(detail_message)

        raise BadfishException

    @alru_cache(maxsize=64)
    async def get_request(self, uri, _continue=False):
        try:
            async with self.semaphore:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        uri,
                        auth=aiohttp.BasicAuth(self.username, self.password),
                        verify_ssl=False,
                        timeout=60,
                    ) as _response:
                        await _response.read()
        except (Exception, TimeoutError) as ex:
            if _continue:
                return
            else:
                self.logger.debug(ex)
                self.logger.error("Failed to communicate with server.")
                raise BadfishException
        return _response

    async def post_request(self, uri, payload, headers):
        try:
            async with self.semaphore:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        uri,
                        data=json.dumps(payload),
                        headers=headers,
                        auth=aiohttp.BasicAuth(self.username, self.password),
                        verify_ssl=False,
                    ) as _response:
                        if _response.status != 204:
                            await _response.read()
                        else:
                            return _response
        except (Exception, TimeoutError):
            self.logger.exception("Failed to communicate with server.")
            raise BadfishException
        return _response

    async def patch_request(self, uri, payload, headers, _continue=False):
        try:
            async with self.semaphore:
                async with aiohttp.ClientSession() as session:
                    async with session.patch(
                        uri,
                        data=json.dumps(payload),
                        headers=headers,
                        auth=aiohttp.BasicAuth(self.username, self.password),
                        verify_ssl=False,
                    ) as _response:
                        await _response.read()
        except Exception as ex:
            if _continue:
                return
            else:
                self.logger.debug(ex)
                self.logger.error("Failed to communicate with server.")
                raise BadfishException
        return _response

    async def delete_request(self, uri, headers):
        try:
            async with self.semaphore:
                async with aiohttp.ClientSession() as session:
                    async with session.delete(
                        uri,
                        headers=headers,
                        auth=aiohttp.BasicAuth(self.username, self.password),
                        ssl=False,
                    ) as _response:
                        await _response.read()
        except (Exception, TimeoutError):
            self.logger.exception("Failed to communicate with server.")
            raise BadfishException
        return _response

    async def get_boot_seq(self):
        bios_boot_mode = await self.get_bios_boot_mode()
        if bios_boot_mode == "Uefi":
            return "UefiBootSeq"
        else:
            return "BootSeq"

    async def get_bios_boot_mode(self):
        self.logger.debug("Getting bios boot mode.")
        _uri = "%s%s/Bios" % (self.host_uri, self.system_resource)
        _response = await self.get_request(_uri)

        try:
            raw = await _response.text("utf-8", "ignore")
            data = json.loads(raw.strip())
        except ValueError:
            self.logger.error("Could not retrieve Bios Boot mode.")
            raise BadfishException

        try:
            bios_boot_mode = data["Attributes"]["BootMode"]
            return bios_boot_mode
        except KeyError:
            self.logger.warning("Could not retrieve Bios Attributes. Assuming Bios.")
            return "Bios"

    async def get_boot_devices(self):
        if not self.boot_devices:
            _boot_seq = await self.get_boot_seq()
            _uri = "%s%s/BootSources" % (self.host_uri, self.system_resource)
            _response = await self.get_request(_uri)

            if _response.status == 404:
                self.logger.debug(_response.text)
                self.logger.error(
                    "Boot order modification is not supported by this host."
                )
                raise BadfishException

            raw = await _response.text("utf-8", "ignore")
            data = json.loads(raw.strip())
            if "Attributes" in data:
                self.boot_devices = data["Attributes"][_boot_seq]
            else:
                self.logger.debug(data)
                self.logger.error(
                    "Boot order modification is not supported by this host."
                )
                raise BadfishException
        return self.boot_devices

    async def get_job_queue(self):
        self.logger.debug("Getting job queue.")
        _url = "%s%s/Jobs" % (self.host_uri, self.manager_resource)
        _response = await self.get_request(_url)

        data = await _response.text("utf-8", "ignore")
        job_queue = re.findall(r"[JR]ID_.+?\d+", data)
        jobs = [job.strip("}").strip('"').strip("'") for job in job_queue]
        return jobs

    async def get_job_status(self, _job_id):
        self.logger.debug("Getting job status.")
        _uri = "%s%s/Jobs/%s" % (self.host_uri, self.manager_resource, _job_id)

        for _ in range(self.retries):
            _response = await self.get_request(_uri, _continue=True)
            if not _response:
                continue

            status_code = _response.status
            if status_code == 200:
                self.logger.info(f"Command passed to check job status {_job_id}")
                await asyncio.sleep(10)
            else:
                self.logger.error(
                    f"Command failed to check job status {_job_id}, return code is %s."
                    % status_code
                )

                await self.error_handler(_response)

            raw = await _response.text("utf-8", "ignore")
            data = json.loads(raw.strip())
            if data["Message"] == "Task successfully scheduled.":
                self.logger.info("Job id %s successfully scheduled." % _job_id)
                return
            else:
                self.logger.warning(
                    "JobStatus not scheduled, current status is: %s." % data["Message"]
                )

        self.logger.error("Not able to successfully schedule the job.")
        raise BadfishException

    async def get_reset_types(self):
        self.logger.debug("Getting allowable reset types.")
        _url = "%s%s" % (self.host_uri, self.manager_resource)
        _response = await self.get_request(_url)
        reset_types = []
        if _response:
            raw = await _response.text("utf-8", "ignore")
            data = json.loads(raw.strip())
            if "Actions" not in data:
                self.logger.warning("Actions resource not found")
            else:
                manager_reset = data["Actions"].get("#Manager.Reset")
                if manager_reset:
                    reset_types = manager_reset.get("ResetType@Redfish.AllowableValues")
                    if not reset_types:
                        self.logger.warning("Could not get allowable reset types")
        return reset_types

    async def get_host_type(self, _interfaces_path):
        boot_devices = await self.get_boot_devices()

        if _interfaces_path:
            with open(_interfaces_path, "r") as f:
                try:
                    definitions = yaml.safe_load(f)
                except yaml.YAMLError as ex:
                    self.logger.error("Couldn't read file: %s" % _interfaces_path)
                    self.logger.debug(ex)
                    raise BadfishException

            host_model = self.host.split(".")[0].split("-")[-1]
            host_blade = self.host.split(".")[0].split("-")[-2]
            b_pattern = re.compile("b0[0-9]")
            if b_pattern.match(host_blade):
                host_model = "%s_%s" % (host_model, host_blade)
            for _host in ["foreman", "director"]:
                match = True
                interfaces = definitions[
                    "%s_%s_interfaces" % (_host, host_model)
                ].split(",")
                for device in sorted(
                    boot_devices[: len(interfaces)], key=lambda x: x["Index"]
                ):
                    if device["Name"] == interfaces[device["Index"]]:
                        continue
                    else:
                        match = False
                        break
                if match:
                    return _host

        return None

    async def validate_credentials(self):
        response = await self.get_request(self.root_uri + "/Systems")

        if response.status == 401:
            self.logger.error(
                f"Failed to authenticate. Verify your credentials for {self.host}"
            )
            raise BadfishException

        if response.status not in [200, 201]:
            self.logger.error(f"Failed to communicate with {self.host}")
            raise BadfishException

    async def get_interfaces_endpoints(self):
        _uri = "%s%s/EthernetInterfaces" % (self.host_uri, self.system_resource)
        _response = await self.get_request(_uri)

        raw = await _response.text("utf-8", "ignore")
        data = json.loads(raw.strip())

        if _response.status == 404:
            self.logger.debug(raw)
            self.logger.error(
                "EthernetInterfaces entry point not supported by this host."
            )
            raise BadfishException

        endpoints = []
        if data.get("Members"):
            for member in data["Members"]:
                endpoints.append(member["@odata.id"])
        else:
            self.logger.error(
                "EthernetInterfaces's Members array is either empty or missing"
            )
            raise BadfishException

        return endpoints

    async def get_interface(self, endpoint):
        _uri = "%s%s" % (self.host_uri, endpoint)
        _response = await self.get_request(_uri)

        raw = await _response.text("utf-8", "ignore")

        if _response.status == 404:
            self.logger.debug(raw)
            self.logger.error(
                "EthernetInterface entry point not supported by this host."
            )
            raise BadfishException

        data = json.loads(raw.strip())

        return data

    async def find_systems_resource(self):
        response = await self.get_request(self.root_uri)
        if response:

            if response.status == 401:
                self.logger.error("Failed to authenticate. Verify your credentials.")
                raise BadfishException

            raw = await response.text("utf-8", "ignore")
            data = json.loads(raw.strip())
            if "Systems" not in data:
                self.logger.error("Systems resource not found")
                raise BadfishException
            else:
                systems = data["Systems"]["@odata.id"]
                _response = await self.get_request(self.host_uri + systems)
                if _response.status == 401:
                    self.logger.error("Authorization Error: verify credentials.")
                    raise BadfishException

                raw = await _response.text("utf-8", "ignore")
                data = json.loads(raw.strip())
                if data.get("Members"):
                    for member in data["Members"]:
                        systems_service = member["@odata.id"]
                        self.logger.debug("Systems service: %s." % systems_service)
                        return systems_service
                else:
                    try:
                        msg = (
                            data.get("error")
                            .get("@Message.ExtendedInfo")[0]
                            .get("Message")
                        )
                        resolution = (
                            data.get("error")
                            .get("@Message.ExtendedInfo")[0]
                            .get("Resolution")
                        )
                        self.logger.error(msg)
                        self.logger.info(resolution)
                    except (IndexError, TypeError, AttributeError):
                        pass
                    else:
                        self.logger.error(
                            "ComputerSystem's Members array is either empty or missing"
                        )
                    raise BadfishException
        else:
            self.logger.error("Failed to communicate with server.")
            raise BadfishException

    async def find_managers_resource(self):
        response = await self.get_request(self.root_uri)
        if response:
            raw = await response.text("utf-8", "ignore")
            data = json.loads(raw.strip())
            if "Managers" not in data:
                self.logger.error("Managers resource not found")
                raise BadfishException
            else:
                managers = data["Managers"]["@odata.id"]
                response = await self.get_request(self.host_uri + managers)
                if response:
                    raw = await response.text("utf-8", "ignore")
                    data = json.loads(raw.strip())
                    if data.get("Members"):
                        for member in data["Members"]:
                            managers_service = member["@odata.id"]
                            self.logger.debug(
                                "Managers service: %s." % managers_service
                            )
                            return managers_service
                    else:
                        self.logger.error(
                            "Manager's Members array is either empty or missing"
                        )
                        raise BadfishException

    async def get_power_state(self):
        _uri = "%s%s" % (self.host_uri, self.system_resource)
        self.logger.debug("url: %s" % _uri)

        _response = await self.get_request(_uri, _continue=True)
        if not _response:
            return "Down"
        if _response.status == 200:
            raw = await _response.text("utf-8", "ignore")
            data = json.loads(raw.strip())
        else:
            self.logger.debug("Couldn't get power state. Retrying.")
            return "Down"

        if not data["PowerState"]:
            self.logger.debug("Power state not found. Try to racreset.")
            raise BadfishException
        else:
            self.logger.debug("Current server power state is: %s." % data["PowerState"])

        return data["PowerState"]

    async def set_power_state(self, state):
        if state.lower() not in ["on", "off"]:
            self.logger.error("Power state not valid. 'on' or 'off' only accepted.")
            raise BadfishException

        _uri = "%s%s" % (self.host_uri, self.system_resource)
        self.logger.debug("url: %s" % _uri)

        _response = await self.get_request(_uri, _continue=True)
        if not _response and state.lower() == "off":
            self.logger.warning("Power state appears to be already set to 'off'.")
            return

        if _response.status == 200:
            raw = await _response.text("utf-8", "ignore")
            data = json.loads(raw.strip())
        else:
            self.logger.debug("Couldn't get power state.")
            raise BadfishException

        if not data["PowerState"]:
            self.logger.debug("Power state not found. Try to racreset.")
            raise BadfishException
        else:
            self.logger.debug("Current server power state is: %s." % data["PowerState"])

        if state.lower() == "off":
            await self.send_reset("ForceOff")
        elif state.lower() == "on":
            await self.send_reset("On")

        return data["PowerState"]

    async def change_boot(self, host_type, interfaces_path, pxe=False):
        if host_type.lower() not in ("foreman", "director"):
            self.logger.error(
                'Expected values for -t argument are "foreman" or "director"'
            )
            raise BadfishException

        if interfaces_path:
            if not os.path.exists(interfaces_path):
                self.logger.error("No such file or directory: %s." % interfaces_path)
                raise BadfishException
        else:
            self.logger.error(
                "You must provide a path to the interfaces yaml via `-i` optional argument."
            )
            raise BadfishException

        _type = await self.get_host_type(interfaces_path)
        if (_type and _type.lower() != host_type.lower()) or not _type:
            await self.clear_job_queue()
            self.logger.warning("Waiting for host to be up.")
            host_up = await self.polling_host_state("On")
            if host_up:
                await self.change_boot_order(interfaces_path, host_type)

                if pxe:
                    await self.set_next_boot_pxe()

                await self.create_bios_config_job(self.bios_uri)

                await self.reboot_server(graceful=False)

            else:
                self.logger.error(
                    "Couldn't communicate with host after %s attempts." % self.retries
                )
                raise BadfishException
        else:
            self.logger.warning(
                "No changes were made since the boot order already matches the requested."
            )
        return True

    async def change_boot_order(self, _interfaces_path, _host_type):
        with open(_interfaces_path, "r") as f:
            try:
                definitions = yaml.safe_load(f)
            except yaml.YAMLError as ex:
                self.logger.error(ex)
                raise BadfishException

        host_model = self.host.split(".")[0].split("-")[-1]
        host_blade = self.host.split(".")[0].split("-")[-2]
        b_pattern = re.compile("b0[0-9]")
        if b_pattern.match(host_blade):
            host_model = "%s_%s" % (host_model, host_blade)
        interfaces = definitions["%s_%s_interfaces" % (_host_type, host_model)].split(
            ","
        )

        boot_devices = await self.get_boot_devices()
        devices = [device["Name"] for device in boot_devices]
        valid_devices = [device for device in interfaces if device in devices]
        if len(valid_devices) < len(interfaces):
            diff = [device for device in interfaces if device not in valid_devices]
            self.logger.warning(
                "Some interfaces are not valid boot devices. Ignoring: %s"
                % ", ".join(diff)
            )
        change = False
        for i, interface in enumerate(valid_devices):
            for device in boot_devices:
                if interface == device["Name"]:
                    if device["Index"] != i:
                        device["Index"] = i
                        change = True
                    break

        if change:
            await self.patch_boot_seq(boot_devices)

        else:
            self.logger.warning(
                "No changes were made since the boot order already matches the requested."
            )

    async def patch_boot_seq(self, boot_devices):
        _boot_seq = await self.get_boot_seq()
        boot_sources_uri = "%s/BootSources/Settings" % self.system_resource
        url = "%s%s" % (self.host_uri, boot_sources_uri)
        payload = {"Attributes": {_boot_seq: boot_devices}}
        headers = {"content-type": "application/json"}
        response = None
        _status_code = 400

        for _ in range(self.retries):
            if _status_code != 200:
                response = await self.patch_request(url, payload, headers, True)
                if response:
                    raw = await response.text("utf-8", "ignore")
                    self.logger.debug(raw)
                    _status_code = response.status
            else:
                break

        if _status_code == 200:
            self.logger.info("PATCH command passed to update boot order.")
        else:
            self.logger.error("There was something wrong with your request.")

            if response:
                await self.error_handler(response)

    async def set_next_boot_pxe(self):
        _url = "%s%s" % (self.host_uri, self.system_resource)
        _payload = {
            "Boot": {
                "BootSourceOverrideTarget": "Pxe",
                "BootSourceOverrideEnabled": "Once",
            }
        }
        _headers = {"content-type": "application/json"}
        _response = await self.patch_request(_url, _payload, _headers)

        await asyncio.sleep(5)

        if _response.status == 200:
            self.logger.info(
                'PATCH command passed to set next boot onetime boot device to: "%s".'
                % "Pxe"
            )
        else:
            self.logger.error("Command failed, error code is %s." % _response.status)

            await self.error_handler(_response)

    async def check_supported_idrac_version(self):
        _url = "%s/Dell/Managers/iDRAC.Embedded.1/DellJobService/" % self.root_uri
        _response = await self.get_request(_url)
        if _response.status != 200:
            self.logger.warning(
                "iDRAC version installed does not support DellJobService"
            )
            return False

        return True

    async def delete_job_queue_dell(self, force):
        _url = (
            "%s/Dell/Managers/iDRAC.Embedded.1/DellJobService/Actions/DellJobService.DeleteJobQueue"
            % self.root_uri
        )
        job_id = "JID_CLEARALL"
        if force:
            job_id = f"{job_id}_FORCE"
        _payload = {"JobID": job_id}
        _headers = {"content-type": "application/json"}
        response = await self.post_request(_url, _payload, _headers)
        if response.status == 200:
            self.logger.info("Job queue for iDRAC %s successfully cleared." % self.host)
        else:
            raw = await response.text("utf-8", "ignore")
            data = json.loads(raw.strip())
            if data.get("error"):
                if data["error"].get("@Message.ExtendedInfo"):
                    self.logger.debug(data["error"].get("@Message.ExtendedInfo"))
            self.logger.error(
                "Job queue not cleared, there was something wrong with your request."
            )
            raise BadfishException

    async def delete_job_queue_force(self):
        _url = "%s%s/Jobs" % (self.host_uri, self.manager_resource)
        _headers = {"content-type": "application/json"}
        url = "%s/JID_CLEARALL_FORCE" % _url
        try:
            _response = await self.delete_request(url, _headers)
        except BadfishException:
            self.logger.warning("There was something wrong clearing the job queue.")
            raise
        return _response

    async def clear_job_list(self, _job_queue):
        _url = "%s%s/Jobs" % (self.host_uri, self.manager_resource)
        _headers = {"content-type": "application/json"}
        self.logger.warning("Clearing job queue for job IDs: %s." % _job_queue)
        failed = False
        for _job in _job_queue:
            job = _job.strip("'")
            url = "/".join([_url, job])
            response = await self.delete_request(url, _headers)
            if response.status != 200:
                failed = True

        if not failed:
            self.logger.info("Job queue for iDRAC %s successfully cleared." % self.host)
        else:
            self.logger.error(
                "Job queue not cleared, there was something wrong with your request."
            )
            raise BadfishException

    async def clear_job_queue(self, force=False):
        _job_queue = await self.get_job_queue()
        if _job_queue or force:
            supported = await self.check_supported_idrac_version()
            if supported:
                await self.delete_job_queue_dell(force)
            else:
                try:
                    _response = await self.delete_job_queue_force()
                    if _response.status == 400:
                        await self.clear_job_list(_job_queue)
                except BadfishException:
                    self.logger.info("Attempting to clear job list instead.")
                    await self.clear_job_list(_job_queue)
        else:
            self.logger.warning(
                "Job queue already cleared for iDRAC %s, DELETE command will not execute."
                % self.host
            )

    async def create_job(self, _url, _payload, _headers, expected=None):
        if not expected:
            expected = [200, 204]
        _response = await self.post_request(_url, _payload, _headers)

        status_code = _response.status

        if status_code in expected:
            self.logger.info("POST command passed to create target config job.")
        else:
            self.logger.error(
                "POST command failed to create BIOS config job, status code is %s."
                % status_code
            )

            await self.error_handler(_response)

    async def create_bios_config_job(self, uri):
        _url = "%s%s/Jobs" % (self.host_uri, self.manager_resource)
        _payload = {"TargetSettingsURI": "%s%s" % (self.redfish_uri, uri)}
        _headers = {"content-type": "application/json"}
        await self.create_job(_url, _payload, _headers)

    async def send_reset(self, reset_type):
        _url = "%s%s/Actions/ComputerSystem.Reset" % (
            self.host_uri,
            self.system_resource,
        )
        _payload = {"ResetType": reset_type}
        _headers = {"content-type": "application/json"}
        _response = await self.post_request(_url, _payload, _headers)

        status_code = _response.status
        if status_code in [200, 204]:
            self.logger.info(
                "Command passed to %s server, code return is %s."
                % (reset_type, status_code)
            )
            await asyncio.sleep(10)
        elif status_code == 409:
            self.logger.warning(
                "Command failed to %s server, host appears to be already in that state."
                % reset_type
            )
        else:
            self.logger.error(
                "Command failed to %s server, status code is: %s."
                % (reset_type, status_code)
            )

            await self.error_handler(_response)

    async def reboot_server(self, graceful=True):
        self.logger.debug("Rebooting server: %s." % self.host)
        power_state = await self.get_power_state()
        if power_state.lower() == "on":
            if graceful:
                await self.send_reset("GracefulRestart")

                host_down = await self.polling_host_state("Off")

                if not host_down:
                    self.logger.warning(
                        "Unable to graceful shutdown the server, will perform forced shutdown now."
                    )
                    await self.send_reset("ForceOff")
            else:
                await self.send_reset("ForceOff")

            host_not_down = await self.polling_host_state("Down", False)

            if host_not_down:
                await self.send_reset("On")

        elif power_state.lower() == "off":
            await self.send_reset("On")
        return True

    async def reset_idrac(self):
        self.logger.debug("Running reset iDRAC.")
        _reset_types = await self.get_reset_types()
        reset_type = "ForceRestart"
        if reset_type not in _reset_types:
            for rt in _reset_types:
                if "restart" in rt.lower():
                    reset_type = rt
        _url = "%s%s/Actions/Manager.Reset/" % (self.host_uri, self.manager_resource)
        _payload = {"ResetType": reset_type}
        _headers = {"content-type": "application/json"}
        self.logger.debug("url: %s" % _url)
        self.logger.debug("payload: %s" % _payload)
        self.logger.debug("headers: %s" % _headers)
        _response = await self.post_request(_url, _payload, _headers)

        status_code = _response.status
        if status_code == 204:
            self.logger.info(
                "Status code %s returned for POST command to reset iDRAC." % status_code
            )
        else:
            data = await _response.text("utf-8", "ignore")
            self.logger.error(
                "Status code %s returned, error is: \n%s." % (status_code, data)
            )
            raise BadfishException

        self.logger.info(
            "iDRAC will now reset and be back online within a few minutes."
        )
        return True

    async def reset_bios(self):
        self.logger.debug("Running BIOS reset.")
        _url = "%s%s/Bios/Actions/Bios.ResetBios/" % (
            self.host_uri,
            self.system_resource,
        )
        _payload = {}
        _headers = {"content-type": "application/json"}
        self.logger.debug("url: %s" % _url)
        self.logger.debug("payload: %s" % _payload)
        self.logger.debug("headers: %s" % _headers)
        _response = await self.post_request(_url, _payload, _headers)

        status_code = _response.status
        if status_code in [200, 204]:
            self.logger.info(
                "Status code %s returned for POST command to reset BIOS." % status_code
            )
        else:
            data = await _response.text("utf-8", "ignore")
            self.logger.error(
                "Status code %s returned, error is: \n%s." % (status_code, data)
            )
            raise BadfishException

        self.logger.info("BIOS will now reset and be back online within a few minutes.")
        return True

    async def boot_to(self, device):
        device_check = await self.check_device(device)
        if device_check:
            await self.clear_job_queue()
            await self.send_one_time_boot(device)
            await self.create_bios_config_job(self.bios_uri)
        else:
            raise BadfishException
        return True

    async def boot_to_type(self, host_type, _interfaces_path):
        if host_type.lower() not in ("foreman", "director"):
            self.logger.error(
                'Expected values for -t argument are "foreman" or "director"'
            )
            raise BadfishException

        if _interfaces_path:
            if not os.path.exists(_interfaces_path):
                self.logger.error("No such file or directory: %s." % _interfaces_path)
                raise BadfishException

        device = self.get_host_type_boot_device(host_type, _interfaces_path)

        await self.boot_to(device)

    async def boot_to_mac(self, mac_address):
        interfaces_endpoints = await self.get_interfaces_endpoints()

        device = None
        for endpoint in interfaces_endpoints:
            interface = await self.get_interface(endpoint)
            if interface.get("MACAddress", "").upper() == mac_address.upper():
                device = interface.get("Id")
                break

        if device:
            await self.boot_to(device)
        else:
            self.logger.error("MAC Address does not match any of the existing")
            raise BadfishException

    async def send_one_time_boot(self, device):
        _url = "%s%s" % (self.root_uri, self.bios_uri)
        _payload = {
            "Attributes": {
                "OneTimeBootMode": "OneTimeBootSeq",
                "OneTimeBootSeqDev": device,
            }
        }
        _headers = {"content-type": "application/json"}
        _first_reset = False
        for i in range(self.retries):
            _response = await self.patch_request(_url, _payload, _headers)
            status_code = _response.status
            if status_code == 200:
                self.logger.info("Command passed to set BIOS attribute pending values.")
                break
            else:
                self.logger.error("Command failed, error code is: %s." % status_code)
                if status_code == 503 and i - 1 != self.retries:
                    self.logger.info("Retrying to send one time boot.")
                    continue
                elif status_code == 400:
                    await self.clear_job_queue()
                    if not _first_reset:
                        await self.reset_idrac()
                        await asyncio.sleep(10)
                        _first_reset = True
                        await self.polling_host_state("On")
                    continue
                await self.error_handler(_response)

    async def check_boot(self, _interfaces_path):
        if _interfaces_path:

            _host_type = await self.get_host_type(_interfaces_path)

            if _host_type:
                self.logger.warning("Current boot order is set to: %s." % _host_type)
            else:
                boot_devices = await self.get_boot_devices()

                self.logger.warning(
                    "Current boot order does not match any of the given."
                )
                self.logger.info("Current boot order:")
                for device in sorted(boot_devices, key=lambda x: x["Index"]):
                    self.logger.info(
                        "%s: %s" % (int(device["Index"]) + 1, device["Name"])
                    )

        else:
            boot_devices = await self.get_boot_devices()
            self.logger.info("Current boot order:")
            for device in sorted(boot_devices, key=lambda x: x["Index"]):
                self.logger.info("%s: %s" % (int(device["Index"]) + 1, device["Name"]))
        return True

    async def check_device(self, device):
        self.logger.debug("Checking device %s." % device)
        devices = await self.get_boot_devices()
        self.logger.debug(devices)
        boot_devices = [_device["Name"].lower() for _device in devices]
        if device.lower() in boot_devices:
            return True
        else:
            self.logger.error(
                "Device %s does not match any of the available boot devices for host %s"
                % (device, self.host)
            )
            return False

    async def polling_host_state(self, state, equals=True):
        state_str = "Not %s" % state if not equals else state
        self.logger.info("Polling for host state: %s" % state_str)
        desired_state = False
        for count in range(self.retries):
            current_state = await self.get_power_state()
            if equals:
                desired_state = current_state.lower() == state.lower()
            else:
                desired_state = current_state.lower() != state.lower()
            await asyncio.sleep(5)
            if desired_state:
                self.progress_bar(self.retries, self.retries, current_state)
                break
            self.progress_bar(count, self.retries, current_state)

        return desired_state

    async def get_firmware_inventory(self):
        self.logger.debug(
            "Getting firmware inventory for all devices supported by iDRAC."
        )

        _url = "%s/UpdateService/FirmwareInventory/" % self.root_uri
        _response = await self.get_request(_url)

        try:
            raw = await _response.text("utf-8", "ignore")
            data = json.loads(raw.strip())
        except ValueError:
            self.logger.error("Not able to access Firmware inventory.")
            raise BadfishException
        installed_devices = []
        if "error" in data:
            self.logger.debug(data["error"])
            self.logger.error("Not able to access Firmware inventory.")
            raise BadfishException
        for device in data["Members"]:
            a = device["@odata.id"]
            a = a.replace("/redfish/v1/UpdateService/FirmwareInventory/", "")
            if "Installed" in a:
                installed_devices.append(a)

        for device in installed_devices:
            self.logger.debug("Getting device info for %s" % device)
            _uri = "%s/UpdateService/FirmwareInventory/%s" % (self.root_uri, device)

            _response = await self.get_request(_uri, _continue=True)
            if not _response:
                continue

            raw = await _response.text("utf-8", "ignore")
            data = json.loads(raw.strip())
            for info in data.items():
                if "odata" not in info[0] and "Description" not in info[0]:
                    self.logger.info("%s: %s" % (info[0], info[1]))

            self.logger.info("*" * 48)

    def get_host_type_boot_device(self, host_type, _interfaces_path):
        if _interfaces_path:
            with open(_interfaces_path, "r") as f:
                try:
                    definitions = yaml.safe_load(f)
                except yaml.YAMLError as ex:
                    self.logger.error("Couldn't read file: %s" % _interfaces_path)
                    self.logger.debug(ex)
                    raise BadfishException

            host_model = self.host.split(".")[0].split("-")[-1]
            host_blade = self.host.split(".")[0].split("-")[-2]
            b_pattern = re.compile("b0[0-9]")
            if b_pattern.match(host_blade):
                host_model = "%s_%s" % (host_model, host_blade)
            if host_model.startswith("r"):
                host_model = host_model[1:]
            return definitions["%s_%s_interfaces" % (host_type, host_model)].split(",")[0]
        return None


async def execute_badfish(_host, _args, logger):
    _username = _args["u"]
    _password = _args["p"]
    host_type = _args["t"]
    interfaces_path = _args["i"]
    force = _args["force"]
    pxe = _args["pxe"]
    device = _args["boot_to"]
    boot_to_type = _args["boot_to_type"]
    boot_to_mac = _args["boot_to_mac"]
    reboot_only = _args["reboot_only"]
    power_state = _args["power_state"]
    power_on = _args["power_on"]
    power_off = _args["power_off"]
    power_cycle = _args["power_cycle"]
    rac_reset = _args["racreset"]
    factory_reset = _args["factory_reset"]
    check_boot = _args["check_boot"]
    firmware_inventory = _args["firmware_inventory"]
    clear_jobs = _args["clear_jobs"]
    retries = int(_args["retries"])

    result = True

    try:
        badfish = await badfish_factory(
            _host=_host,
            _username=_username,
            _password=_password,
            _logger=logger,
            _retries=retries,
        )

        if _args["host_list"]:
            badfish.logger.info("Executing actions on host: %s" % _host)

        if device:
            await badfish.boot_to(device)
        elif boot_to_type:
            await badfish.boot_to_type(boot_to_type, interfaces_path)
        elif boot_to_mac:
            await badfish.boot_to_mac(boot_to_mac)
        elif check_boot:
            await badfish.check_boot(interfaces_path)
        elif firmware_inventory:
            await badfish.get_firmware_inventory()
        elif clear_jobs:
            await badfish.clear_job_queue(force)
        elif host_type:
            await badfish.change_boot(host_type, interfaces_path, pxe)
        elif rac_reset:
            await badfish.reset_idrac()
        elif factory_reset:
            await badfish.reset_bios()
        elif power_state:
            state = await badfish.get_power_state()
            logger.info(f"Power state for {_host}: {state}")
        elif power_on:
            await badfish.set_power_state("on")
        elif power_off:
            await badfish.set_power_state("off")
        elif power_cycle:
            await badfish.reboot_server(graceful=False)
        elif reboot_only:
            await badfish.reboot_server()

        if pxe and not host_type:
            await badfish.set_next_boot_pxe()

    except BadfishException as ex:
        logger.debug(ex)
        logger.error("There was something wrong executing Badfish.")
        result = False

    if _args["host_list"]:
        logger.info("*" * 48)

    return _host, result


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Tool for managing server hardware via the Redfish API."
    )
    parser.add_argument("-H", help="iDRAC host address")
    parser.add_argument("-u", help="iDRAC username", required=True)
    parser.add_argument("-p", help="iDRAC password", required=True)
    parser.add_argument("-i", help="Path to iDRAC interfaces yaml", default=None)
    parser.add_argument("-t", help="Type of host. Accepts: foreman, director")
    parser.add_argument(
        "-l", "--log", help="Optional argument for logging results to a file"
    )
    parser.add_argument(
        "-f",
        "--force",
        dest="force",
        action="store_true",
        help="Optional argument for forced clear-jobs",
    )
    parser.add_argument(
        "--host-list",
        help="Path to a plain text file with a list of hosts.",
        default=None,
    )
    parser.add_argument(
        "--pxe", help="Set next boot to one-shot boot PXE", action="store_true"
    )
    parser.add_argument(
        "--boot-to", help="Set next boot to one-shot boot to a specific device"
    )
    parser.add_argument(
        "--boot-to-type",
        help="Set next boot to one-shot boot to either director or foreman",
    )
    parser.add_argument(
        "--boot-to-mac",
        help="Set next boot to one-shot boot to a specific MAC address on the target",
    )
    parser.add_argument(
        "--reboot-only", help="Flag for only rebooting the host", action="store_true"
    )
    parser.add_argument(
        "--power-cycle",
        help="Flag for sending ForceOff instruction to the host",
        action="store_true",
    )
    parser.add_argument(
        "--power-state", help="Get power state", action="store_true",
    )
    parser.add_argument(
        "--power-on", help="Power on host", action="store_true",
    )
    parser.add_argument(
        "--power-off", help="Power off host", action="store_true",
    )
    parser.add_argument("--racreset", help="Flag for iDRAC reset", action="store_true")
    parser.add_argument(
        "--factory-reset",
        help="Reset BIOS to default factory settings",
        action="store_true",
    )
    parser.add_argument(
        "--check-boot",
        help="Flag for checking the host boot order",
        action="store_true",
    )
    parser.add_argument(
        "--firmware-inventory", help="Get firmware inventory", action="store_true"
    )
    parser.add_argument(
        "--clear-jobs",
        help="Clear any schedule jobs from the queue",
        action="store_true",
    )
    parser.add_argument("-v", "--verbose", help="Verbose output", action="store_true")
    parser.add_argument(
        "-r",
        "--retries",
        help="Number of retries for executing actions.",
        default=RETRIES,
    )
    _args = vars(parser.parse_args(argv))

    log_level = DEBUG if _args["verbose"] else INFO

    host_list = _args["host_list"]
    host = _args["H"]
    result = True

    if host_list:
        FMT = "[%(name)s] - %(levelname)-8s - %(message)s"
        FILEFMT = "%(asctime)-12s: [%(name)s] - %(levelname)-8s - %(message)s"
    else:
        FMT = "- %(levelname)-8s - %(message)s"
        FILEFMT = "%(asctime)-12s: %(levelname)-8s - %(message)s"

    _queue = Queue()
    _stream_handler = StreamHandler()
    _stream_handler.setFormatter(Formatter(FMT))
    _queue_listener = QueueListener(_queue, _stream_handler)
    _logger = getLogger(__name__)
    _queue_handler = QueueHandler(_queue)
    _logger.addHandler(_queue_handler)
    _logger.setLevel(log_level)

    _queue_listener.start()

    if _args["log"]:
        file_handler = FileHandler(_args["log"])
        file_handler.setFormatter(Formatter(FILEFMT))
        file_handler.setLevel(log_level)
        _queue_listener.handlers = _queue_listener.handlers + (file_handler,)

    loop = asyncio.get_event_loop()
    tasks = []
    if host_list:
        try:
            with open(host_list, "r") as _file:
                for _host in _file.readlines():
                    logger = getLogger(_host.split(".")[0])
                    logger.addHandler(_queue_handler)
                    logger.setLevel(log_level)
                    fn = functools.partial(
                        execute_badfish, _host.strip(), _args, logger
                    )
                    tasks.append(fn)
        except IOError as ex:
            _logger.debug(ex)
            _logger.error("There was something wrong reading from %s" % host_list)
        results = []
        try:
            results = loop.run_until_complete(
                asyncio.gather(*[task() for task in tasks], return_exceptions=True)
            )
        except KeyboardInterrupt:
            _logger.warning("\nBadfish terminated.")
            result = False
        except (asyncio.CancelledError, BadfishException) as ex:
            _logger.warning("There was something wrong executing Badfish.")
            _logger.debug(ex)
            result = False
        if results:
            result = True
            _logger.info("RESULTS:")
            for res in results:
                if len(res) > 1 and res[1]:
                    _logger.info(f"{res[0]}: SUCCESSFUL")
                else:
                    _logger.info(f"{res[0]}: FAILED")
                    result = False
    elif not host:
        _logger.error(
            "You must specify at least either a host (-H) or a host list (--host-list)."
        )
    else:
        try:
            _host, result = loop.run_until_complete(execute_badfish(host, _args, _logger))
        except KeyboardInterrupt:
            _logger.warning("Badfish terminated.")
        except BadfishException as ex:
            _logger.warning("There was something wrong executing Badfish.")
            _logger.debug(ex)
            result = False
    _queue_listener.stop()

    if result:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
