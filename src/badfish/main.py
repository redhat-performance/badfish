#!/usr/bin/env python3
import asyncio
import base64
import functools
import aiohttp
import json
import argparse
import os
import re
import sys
import time
import warnings
import yaml
import tempfile

from src.badfish.helpers.async_lru import alru_cache
from src.badfish.helpers.logger import (
    BadfishLogger,
)

from logging import (
    DEBUG,
    INFO,
    getLogger,
)

warnings.filterwarnings("ignore")

RETRIES = 15


async def badfish_factory(
    _host, _username, _password, _logger=None, _retries=RETRIES, _loop=None
):
    if not _logger:
        bfl = BadfishLogger()
        _logger = bfl.logger

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
        self.loop = _loop
        if not self.loop:
            self.loop = asyncio.get_event_loop()
        self.system_resource = None
        self.manager_resource = None
        self.bios_uri = None
        self.boot_devices = None
        self.session_uri = None
        self.session_id = None
        self.token = None

    async def init(self):
        self.session_uri = await self.find_session_uri()
        self.token = await self.validate_credentials()
        self.system_resource = await self.find_systems_resource()
        self.manager_resource = await self.find_managers_resource()
        self.bios_uri = (
            "%s/Bios/Settings" % self.system_resource[len(self.redfish_uri) :]
        )

    @staticmethod
    def progress_bar(value, end_value, state, prompt="Host state", bar_length=20):
        ratio = float(value) / end_value
        arrow = "-" * int(round(ratio * bar_length) - 1) + ">"
        spaces = " " * (bar_length - len(arrow))
        percent = int(round(ratio * 100))

        if state.lower() == "on":
            state = "On  "
        ret = "\r" if percent != 100 else "\n"
        sys.stdout.write(
            f"\r- POLLING: [{arrow + spaces}] {percent}% - {prompt}: {state}{ret}"
        )
        sys.stdout.flush()

    async def error_handler(self, _response, message=None):
        try:
            raw = await _response.text("utf-8", "ignore")
            data = json.loads(raw.strip())
        except ValueError:
            raise BadfishException("Error reading response from host.")

        detail_message = data
        if "error" in data:
            try:
                detail_message = str(
                    data["error"]["@Message.ExtendedInfo"][0]["Message"]
                )
                resolution = str(
                    data["error"]["@Message.ExtendedInfo"][0]["Resolution"]
                )
                self.logger.debug(resolution)
            except (KeyError, IndexError) as ex:
                self.logger.debug(ex)
        if message:
            self.logger.debug(detail_message)
            raise BadfishException(message)
        else:
            raise BadfishException(detail_message)

    @alru_cache(maxsize=64)
    async def get_request(self, uri, _continue=False, _get_token=False):
        try:
            async with self.semaphore:
                async with aiohttp.ClientSession() as session:
                    if not _get_token:
                        async with session.get(
                            uri,
                            headers={"X-Auth-Token": self.token},
                            ssl=False,
                            timeout=60,
                        ) as _response:
                            await _response.read()
                    else:
                        async with session.get(
                            uri,
                            auth=aiohttp.BasicAuth(self.username, self.password),
                            ssl=False,
                            timeout=60,
                        ) as _response:
                            await _response.read()
        except (Exception, TimeoutError) as ex:
            if _continue:
                return
            else:
                self.logger.debug(ex)
                raise BadfishException("Failed to communicate with server.")
        return _response

    async def post_request(self, uri, payload, headers, _get_token=False):
        try:
            async with self.semaphore:
                async with aiohttp.ClientSession() as session:
                    if not _get_token:
                        headers.update({"X-Auth-Token": self.token})
                    async with session.post(
                        uri,
                        data=json.dumps(payload),
                        headers=headers,
                        ssl=False,
                    ) as _response:
                        if _response.status != 204:
                            await _response.read()
                        else:
                            return _response
        except (Exception, TimeoutError):
            raise BadfishException("Failed to communicate with server.")
        return _response

    async def patch_request(self, uri, payload, headers, _continue=False):
        try:
            async with self.semaphore:
                async with aiohttp.ClientSession() as session:
                    headers.update({"X-Auth-Token": self.token})
                    async with session.patch(
                        uri,
                        data=json.dumps(payload),
                        headers=headers,
                        ssl=False,
                    ) as _response:
                        await _response.read()
        except Exception as ex:
            if _continue:
                return
            else:
                self.logger.debug(ex)
                raise BadfishException("Failed to communicate with server.")
        return _response

    async def delete_request(self, uri, headers):
        try:
            async with self.semaphore:
                async with aiohttp.ClientSession() as session:
                    headers.update({"X-Auth-Token": self.token})
                    async with session.delete(
                        uri,
                        headers=headers,
                        ssl=False,
                    ) as _response:
                        await _response.read()
        except (Exception, TimeoutError):
            raise BadfishException("Failed to communicate with server.")
        return _response

    async def get_interfaces_by_type(self, host_type, _interfaces_path):
        definitions = await self.read_yaml(_interfaces_path)

        host_name_split = self.host.split(".")[0].split("-")
        host_model = host_name_split[-1]
        host_blade = host_name_split[-2]
        uloc = host_name_split[-3]
        rack = host_name_split[-4]

        prefix = [host_type, rack, uloc]

        b_pattern = re.compile("b0[0-9]")
        if b_pattern.match(host_blade):
            host_model = "%s_%s" % (host_model, host_blade)

        len_prefix = len(prefix)
        key = "None"
        for _ in range(len_prefix):
            prefix_string = "_".join(prefix)
            key = "%s_%s_interfaces" % (prefix_string, host_model)
            interfaces_string = definitions.get(key)
            if interfaces_string:
                return interfaces_string.split(",")
            else:
                prefix.pop()

        raise BadfishException(
            f"Couldn't find a valid key defined on the interfaces yaml: {key}"
        )

    async def get_boot_seq(self):
        bios_boot_mode = await self.get_bios_boot_mode()
        if bios_boot_mode == "Uefi":
            return "UefiBootSeq"
        else:
            return "BootSeq"

    async def get_bios_boot_mode(self):
        self.logger.debug("Getting bios boot mode.")
        attribute = "BootMode"
        bios_boot_mode = await self.get_bios_attribute(attribute)
        if not bios_boot_mode:
            self.logger.warning("Assuming boot mode is Bios.")
            bios_boot_mode = "Bios"
        self.logger.debug("Current boot mode: %s" % bios_boot_mode)
        return bios_boot_mode

    async def get_sriov_mode(self):
        self.logger.debug("Getting global SRIOV mode.")
        attribute = "SriovGlobalEnable"
        sriov_mode = await self.get_bios_attribute(attribute)
        return sriov_mode

    async def get_bios_attributes_registry(self):
        self.logger.debug("Getting BIOS attribute registry.")
        _uri = "%s%s/Bios/BiosRegistry" % (self.host_uri, self.system_resource)
        _response = await self.get_request(_uri)

        if _response.status == 404:
            self.logger.error("Operation not supported by vendor.")
            return False

        try:
            raw = await _response.text("utf-8", "ignore")
            data = json.loads(raw.strip())
        except ValueError:
            raise BadfishException("Could not retrieve Bios Attributes.")

        return data

    async def get_bios_attribute_registry(self, attribute):
        data = await self.get_bios_attributes_registry()
        attribute_value = await self.get_bios_attribute(attribute)
        for entry in data["RegistryEntries"]["Attributes"]:
            entries = [
                low_entry.lower()
                for low_entry in entry.values()
                if type(low_entry) == str
            ]
            if attribute.lower() in entries:
                for values in entry.items():
                    if values[0] == "CurrentValue":
                        self.logger.info(f"{values[0]}: {attribute_value}")
                    else:
                        self.logger.info(f"{values[0]}: {values[1]}")
                return True
        raise BadfishException(f"Unable to locate the Bios attribute: {attribute}")

    async def get_bios_attributes(self):
        self.logger.debug("Getting BIOS attributes.")
        _uri = "%s%s/Bios" % (self.host_uri, self.system_resource)
        _response = await self.get_request(_uri)

        if _response.status == 404:
            self.logger.error("Operation not supported by vendor.")
            return False

        try:
            raw = await _response.text("utf-8", "ignore")
            data = json.loads(raw.strip())
        except ValueError:
            raise BadfishException("Could not retrieve Bios Attributes.")
        return data

    async def get_bios_attribute(self, attribute):
        data = await self.get_bios_attributes()
        try:
            bios_attribute = data["Attributes"][attribute]
            return bios_attribute
        except KeyError:
            self.logger.warning("Could not retrieve Bios Attributes.")
            return None

    async def set_bios_attribute(self, attributes):
        data = await self.get_bios_attributes_registry()
        accepted = False
        for entry in data["RegistryEntries"]["Attributes"]:
            entries = [
                low_entry.lower()
                for low_entry in entry.values()
                if type(low_entry) == str
            ]
            _warnings = []
            _not_found = []
            _remove = []
            for attribute, value in attributes.items():
                if attribute.lower() in entries:
                    for values in entry.items():
                        if values[0] == "Value":
                            accepted_values = [
                                value["ValueName"] for value in values[1]
                            ]
                            for accepted_value in accepted_values:
                                if value.lower() == accepted_value.lower():
                                    value = accepted_value
                                    accepted = True
                            if not accepted:
                                _warnings.append(
                                    f"List of accepted values for '{attribute}': {accepted_values}"
                                )

                attribute_value = await self.get_bios_attribute(attribute)
                if attribute_value:
                    if value.lower() == attribute_value.lower():
                        self.logger.warning(
                            f"Attribute value for {attribute} is already in that state. IGNORING."
                        )
                        _remove.append(attribute)
                else:
                    _not_found.append(
                        f"{attribute} not found. Please check attribute name."
                    )
            if _warnings:
                for warning in _warnings:
                    self.logger.warning(warning)
                raise BadfishException("Value not accepted")
            if _not_found:
                for warning in _not_found:
                    self.logger.error(warning)
                raise BadfishException("Attribute not found")
            if _remove:
                for attribute in _remove:
                    attributes.pop(attribute)

        _payload = {"Attributes": attributes}

        await self.patch_bios(_payload, insist=False)
        await self.reboot_server()

    async def get_boot_devices(self):
        if not self.boot_devices:
            _boot_seq = await self.get_boot_seq()
            _uri = "%s%s/BootSources" % (self.host_uri, self.system_resource)
            _response = await self.get_request(_uri)

            if _response.status == 404:
                self.logger.debug(_response.text)
                raise BadfishException(
                    "Boot order modification is not supported by this host."
                )

            raw = await _response.text("utf-8", "ignore")
            data = json.loads(raw.strip())
            if "Attributes" in data:
                try:
                    self.boot_devices = data["Attributes"][_boot_seq]
                except KeyError:
                    for key in data["Attributes"].keys():
                        if "bootseq" in key.lower():
                            self.logger.debug("Boot sequence found: %s" % key)
                    raise BadfishException(
                        "The boot mode does not match the boot sequence. Try again in a few minutes."
                    )
            else:
                self.logger.debug(data)
                raise BadfishException(
                    "Boot order modification is not supported by this host."
                )

    async def get_job_queue(self):
        self.logger.debug("Getting job queue.")
        _url = "%s%s/Jobs" % (self.host_uri, self.manager_resource)
        _response = await self.get_request(_url)

        data = await _response.text("utf-8", "ignore")
        job_queue = re.findall(r"[JR]ID_.+?\d+", data)
        jobs = [job.strip("}").strip('"').strip("'") for job in job_queue]
        return jobs

    async def get_reset_types(self, manager=False):
        if manager:
            resource = self.manager_resource
            endpoint = "#Manager.Reset"
        else:
            resource = self.system_resource
            endpoint = "#ComputerSystem.Reset"

        self.logger.debug("Getting allowable reset types.")
        _url = "%s%s" % (self.host_uri, resource)
        _response = await self.get_request(_url)
        reset_types = []
        if _response:
            raw = await _response.text("utf-8", "ignore")
            data = json.loads(raw.strip())
            if "Actions" not in data:
                self.logger.warning("Actions resource not found")
            else:
                reset = data["Actions"].get(endpoint)
                if reset:
                    reset_types = reset.get("ResetType@Redfish.AllowableValues", [])
                    if not reset_types:
                        self.logger.warning("Could not get allowable reset types")
        return reset_types

    async def read_yaml(self, _yaml_file):
        with open(_yaml_file, "r") as f:
            try:
                definitions = yaml.safe_load(f)
            except yaml.YAMLError as ex:
                self.logger.debug(ex)
                raise BadfishException("Couldn't read file: %s" % _yaml_file)
        return definitions

    async def get_host_types_from_yaml(self, _interfaces_path):
        definitions = await self.read_yaml(_interfaces_path)
        host_types = set()
        for line in definitions:
            _split = line.split("_")
            host_types.add(_split[0])

        ordered_types = sorted(list(host_types))
        return ordered_types

    async def get_host_type(self, _interfaces_path):
        await self.get_boot_devices()
        if _interfaces_path:
            host_types = await self.get_host_types_from_yaml(_interfaces_path)
            for host_type in host_types:
                match = True
                interfaces = await self.get_interfaces_by_type(
                    host_type, _interfaces_path
                )

                for device in sorted(
                    self.boot_devices[: len(interfaces)], key=lambda x: x["Index"]
                ):
                    if device["Name"] == interfaces[device["Index"]]:
                        continue
                    else:
                        match = False
                        break
                if match:
                    return host_type

        return None

    async def find_session_uri(self):
        _response = await self.get_request(self.root_uri, _get_token=True)
        raw = await _response.text("utf-8", "ignore")
        data = json.loads(raw.strip())

        status = _response.status
        if status == 401:
            raise BadfishException(
                f"Failed to authenticate. Verify your credentials for {self.host}"
            )
        if status not in [200, 201]:
            raise BadfishException(f"Failed to communicate with {self.host}")

        redfish_version = int(data["RedfishVersion"].replace(".", ""))
        session_uri = None
        if redfish_version >= 160:
            session_uri = "/redfish/v1/SessionService/Sessions"
        elif redfish_version < 160:
            session_uri = "/redfish/v1/Sessions"

        _uri = "%s%s" % (self.host_uri, session_uri)
        check_response = await self.get_request(_uri, _get_token=True)
        if check_response.status == 404:
            session_uri = "/redfish/v1/SessionService/Sessions"

        return session_uri

    async def validate_credentials(self):
        payload = {"UserName": self.username, "Password": self.password}
        headers = {"content-type": "application/json"}
        _uri = "%s%s" % (self.host_uri, self.session_uri)
        _response = await self.post_request(
            _uri, headers=headers, payload=payload, _get_token=True
        )

        # Mock shifting value on value access and not on call.
        await _response.text("utf-8", "ignore")

        status = _response.status
        if status == 401:
            raise BadfishException(
                f"Failed to authenticate. Verify your credentials for {self.host}"
            )
        if status not in [200, 201]:
            raise BadfishException(f"Failed to communicate with {self.host}")

        self.session_id = _response.headers.get("Location")
        return _response.headers.get("X-Auth-Token")

    async def get_interfaces_endpoints(self):
        _uri = "%s%s/EthernetInterfaces" % (self.host_uri, self.system_resource)
        _response = await self.get_request(_uri)

        raw = await _response.text("utf-8", "ignore")
        data = json.loads(raw.strip())

        if _response.status == 404:
            self.logger.debug(raw)
            raise BadfishException(
                "EthernetInterfaces entry point not supported by this host."
            )

        endpoints = []
        if data.get("Members"):
            for member in data["Members"]:
                endpoints.append(member["@odata.id"])
        else:
            raise BadfishException(
                "EthernetInterfaces's Members array is either empty or missing"
            )

        return endpoints

    async def get_interface(self, endpoint):
        _uri = "%s%s" % (self.host_uri, endpoint)
        _response = await self.get_request(_uri)

        raw = await _response.text("utf-8", "ignore")

        if _response.status == 404:
            self.logger.debug(raw)
            raise BadfishException(
                "EthernetInterface entry point not supported by this host."
            )

        data = json.loads(raw.strip())

        return data

    async def find_systems_resource(self):
        response = await self.get_request(self.root_uri)
        if response:
            if response.status == 401:
                raise BadfishException(
                    "Failed to authenticate. Verify your credentials."
                )

            raw = await response.text("utf-8", "ignore")
            data = json.loads(raw.strip())
            if "Systems" not in data:
                raise BadfishException("Systems resource not found")
            else:
                systems = data["Systems"]["@odata.id"]
                _response = await self.get_request(self.host_uri + systems)
                if _response.status == 401:
                    raise BadfishException("Authorization Error: verify credentials.")

                raw = await _response.text("utf-8", "ignore")
                data = json.loads(raw.strip())
                if data.get("Members"):
                    for member in data["Members"]:
                        systems_service = member["@odata.id"]
                        self.logger.debug("Systems service: %s." % systems_service)
                        return systems_service
                else:
                    await self.error_handler(
                        _response,
                        message="ComputerSystem's Members array is either empty or missing",
                    )
        else:
            raise BadfishException("Failed to communicate with server.")

    async def find_managers_resource(self):
        response = await self.get_request(self.root_uri)
        if response:
            raw = await response.text("utf-8", "ignore")
            data = json.loads(raw.strip())
            if "Managers" not in data:
                raise BadfishException("Managers resource not found")
            else:
                managers = data["Managers"]["@odata.id"]
                response = await self.get_request(self.host_uri + managers)
                if response and response.status in [200, 201]:
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
                        raise BadfishException(
                            "Manager's Members array is either empty or missing"
                        )

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

        if not data.get("PowerState"):
            raise BadfishException("Power state not found. Try to racreset.")
        else:
            self.logger.debug("Current server power state is: %s." % data["PowerState"])

        return data["PowerState"]

    async def set_power_state(self, state):
        if state.lower() not in ["on", "off"]:
            raise BadfishException(
                "Power state not valid. 'on' or 'off' only accepted."
            )

        _uri = "%s%s" % (self.host_uri, self.system_resource)
        self.logger.debug("url: %s" % _uri)

        _response = await self.get_request(_uri, _continue=True)
        if not _response and state.lower() == "off":
            self.logger.warning("Power state appears to be already set to 'off'.")
            return

        status = _response.status
        if status == 200:
            raw = await _response.text("utf-8", "ignore")
            data = json.loads(raw.strip())
        else:
            raise BadfishException("Couldn't get power state.")

        if not data.get("PowerState"):
            raise BadfishException("Power state not found. Try to racreset.")
        else:
            self.logger.debug("Current server power state is: %s." % data["PowerState"])

        if state.lower() == "off":
            await self.send_reset("ForceOff")
        elif state.lower() == "on":
            await self.send_reset("On")

        return data["PowerState"]

    async def change_boot(self, host_type, interfaces_path, pxe=False):
        if interfaces_path:
            if not os.path.exists(interfaces_path):
                raise BadfishException(
                    "No such file or directory: '%s'." % interfaces_path
                )
            host_types = await self.get_host_types_from_yaml(interfaces_path)
            if host_type.lower() not in host_types:
                raise BadfishException(
                    f"Expected values for -t argument are: {host_types}"
                )
        else:
            raise BadfishException(
                "You must provide a path to the interfaces yaml via `-i` optional argument."
            )
        _type = None
        if host_type.lower() != "uefi":
            _type = await self.get_host_type(interfaces_path)
        if (_type and _type.lower() != host_type.lower()) or not _type:
            await self.clear_job_queue()
            if host_type.lower() == "uefi":
                payload = dict()
                boot_mode = await self.get_bios_boot_mode()
                if boot_mode.lower() != "uefi":
                    payload["BootMode"] = "Uefi"
                interfaces = await self.get_interfaces_by_type(
                    host_type, interfaces_path
                )

                for i, interface in enumerate(interfaces, 1):
                    payload[f"PxeDev{i}Interface"] = interface
                    payload[f"PxeDev{i}EnDis"] = "Enabled"

                await self.set_bios_attribute(payload)

            else:
                boot_mode = await self.get_bios_boot_mode()
                if boot_mode.lower() == "uefi":
                    self.logger.warning(
                        "Changes being requested will be valid for Bios BootMode. "
                        "Current boot mode is set to Uefi."
                    )
                await self.change_boot_order(host_type, interfaces_path)

                if pxe:
                    await self.set_next_boot_pxe()

                await self.create_bios_config_job(self.bios_uri)

                await self.reboot_server(graceful=False)

        else:
            self.logger.warning(
                "No changes were made since the boot order already matches the requested."
            )
        return True

    async def change_boot_order(self, _host_type, _interfaces_path):
        interfaces = await self.get_interfaces_by_type(_host_type, _interfaces_path)

        await self.get_boot_devices()
        devices = [device["Name"] for device in self.boot_devices]
        valid_devices = [device for device in interfaces if device in devices]
        if len(valid_devices) < len(interfaces):
            diff = [device for device in interfaces if device not in valid_devices]
            self.logger.warning(
                "Some interfaces are not valid boot devices. Ignoring: %s"
                % ", ".join(diff)
            )
        change = False
        ordered_devices = self.boot_devices.copy()
        for i, interface in enumerate(valid_devices):
            for device in ordered_devices:
                if interface == device["Name"]:
                    if device["Index"] != i:
                        device["Index"] = i
                        change = True
                    break

        if change:
            await self.patch_boot_seq(ordered_devices)
        else:
            self.logger.warning(
                "No changes were made since the boot order already matches the requested."
            )

    async def patch_boot_seq(self, ordered_devices):
        _boot_seq = await self.get_boot_seq()
        boot_sources_uri = "%s/BootSources/Settings" % self.system_resource
        url = "%s%s" % (self.host_uri, boot_sources_uri)
        payload = {"Attributes": {_boot_seq: ordered_devices}}
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
            self.logger.debug("PATCH command passed to update boot order.")
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

    async def check_supported_network_interfaces(self, endpoint):
        _url = "%s%s/%s" % (self.host_uri, self.system_resource, endpoint)
        _response = await self.get_request(_url)
        if _response.status != 200:
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
            await self.error_handler(
                response,
                message="Job queue not cleared, there was something wrong with your request.",
            )

    async def delete_job_queue_force(self):
        _url = "%s%s/Jobs" % (self.host_uri, self.manager_resource)
        _headers = {"content-type": "application/json"}
        url = "%s/JID_CLEARALL_FORCE" % _url
        try:
            _response = await self.delete_request(url, _headers)
            if _response.status in [200, 204]:
                self.logger.info(
                    "Job queue for iDRAC %s successfully cleared." % self.host
                )
        except BadfishException as ex:
            self.logger.debug(ex)
            raise BadfishException("There was something wrong clearing the job queue.")
        return _response

    async def clear_job_list(self, _job_queue):
        _url = "%s%s/Jobs" % (self.host_uri, self.manager_resource)
        _headers = {"content-type": "application/json"}
        self.logger.warning("Clearing job queue for job IDs: %s." % _job_queue)
        for _job in _job_queue:
            job = _job.strip("'")
            url = "/".join([_url, job])
            response = await self.delete_request(url, _headers)
            if response.status != 200:
                raise BadfishException(
                    "Job queue not cleared, there was something wrong with your request."
                )

        self.logger.info("Job queue for iDRAC %s successfully cleared." % self.host)
        return True

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

    async def list_job_queue(self):
        _job_queue = await self.get_job_queue()
        if _job_queue:
            self.logger.info("Found active jobs:")
            for job in _job_queue:
                self.logger.info("    JobID: " + job)
        else:
            self.logger.info("Found active jobs: None")

    async def create_job(self, _url, _payload, _headers, expected=None):
        if not expected:
            expected = [200, 204]
        _response = await self.post_request(_url, _payload, _headers)

        status_code = _response.status
        if status_code in expected:
            self.logger.debug("POST command passed to create target config job.")
        else:
            self.logger.error(
                "POST command failed to create BIOS config job, status code is %s."
                % status_code
            )

            await self.error_handler(_response)

        raw = await _response.text("utf-8", "ignore")
        result = re.search("JID_.+?", raw)
        res_group = ""
        if result:
            res_group = result.group()
        job_id = re.sub("[,']", "", res_group)
        if job_id:
            self.logger.debug("%s job ID successfully created" % job_id)
        return job_id

    async def create_bios_config_job(self, uri):
        _url = "%s%s/Jobs" % (self.host_uri, self.manager_resource)
        _payload = {"TargetSettingsURI": "%s%s" % (self.redfish_uri, uri)}
        _headers = {"content-type": "application/json"}
        return await self.create_job(_url, _payload, _headers)

    async def check_schedule_job_status(self, job_id):
        _url = f"{self.host_uri}{self.manager_resource}/Jobs/{job_id}"
        _response = await self.get_request(_url)

        if _response:
            status_code = _response.status
            raw = await _response.text("utf-8", "ignore")
            data = json.loads(raw.strip())

            if status_code == 200:
                await asyncio.sleep(10)
            else:
                self.logger.error(
                    f"Command failed to check job status, return code is {status_code}"
                )
                self.logger.debug(f"Extended Info Message: {data}")
                return False

            self.logger.info(f"JobID: {data[u'Id']}")
            self.logger.info(f"Name: {data[u'Name']}")
            self.logger.info(f"Message: {data[u'Message']}")
            self.logger.info(f"PercentComplete: {str(data[u'PercentComplete'])}")
        else:
            self.logger.error("Command failed to check job status")
            return False

    async def check_job_status(self, job_id):
        for count in range(self.retries):
            _url = f"{self.host_uri}{self.manager_resource}/Jobs/{job_id}"
            self.get_request.cache_clear()
            _response = await self.get_request(_url)

            status_code = _response.status
            raw = await _response.text("utf-8", "ignore")
            data = json.loads(raw.strip())
            if status_code == 200:
                pass
            else:
                self.logger.error(
                    f"Command failed to check job status, return code is {status_code}"
                )
                self.logger.debug(f"Extended Info Message: {data}")
                return False
            if "Fail" in data["Message"] or "fail" in data["Message"]:
                self.logger.debug(f"\n{job_id} job failed.")
                return False
            elif data["Message"] == "Job completed successfully.":
                self.logger.info(f"JobID: {data[u'Id']}")
                self.logger.info(f"Name: {data[u'Name']}")
                self.logger.info(f"Message: {data[u'Message']}")
                self.logger.info(f"PercentComplete: {str(data[u'PercentComplete'])}")
                break
            else:
                self.progress_bar(count, self.retries, data["Message"], prompt="Status")
                await asyncio.sleep(30)

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
            return True
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
        return False

    async def reboot_server(self, graceful=True):
        _reset_types = await self.get_reset_types()
        reset_type = "GracefulRestart"
        if reset_type not in _reset_types:
            for rt in _reset_types:
                if "restart" in rt.lower():
                    reset_type = rt

        self.logger.debug("Rebooting server: %s." % self.host)
        power_state = await self.get_power_state()
        if power_state.lower() == "on":
            if graceful:
                response = await self.send_reset(reset_type)

                if not response:
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
        _reset_types = await self.get_reset_types(manager=True)
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
            raise BadfishException(
                "Status code %s returned, error is: \n%s." % (status_code, data)
            )

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
            raise BadfishException(
                "Status code %s returned, error is: \n%s." % (status_code, data)
            )

        self.logger.info("BIOS will now reset and be back online within a few minutes.")
        return True

    async def boot_to(self, device):
        device_check = await self.check_device(device)
        if device_check:
            await self.clear_job_queue()
            await self.send_one_time_boot(device)
            await self.create_bios_config_job(self.bios_uri)
        else:
            return False
        return True

    async def boot_to_type(self, host_type, _interfaces_path):
        if _interfaces_path:
            if not os.path.exists(_interfaces_path):
                raise BadfishException(
                    "No such file or directory: %s." % _interfaces_path
                )
        else:
            raise BadfishException(
                "You must provide a path to the interfaces yaml via `-i` optional argument."
            )
        host_types = await self.get_host_types_from_yaml(_interfaces_path)
        if host_type.lower() not in host_types:
            raise BadfishException(f"Expected values for -t argument are: {host_types}")

        device = await self.get_host_type_boot_device(host_type, _interfaces_path)

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
            raise BadfishException("MAC Address does not match any of the existing")

    async def send_one_time_boot(self, device):
        _payload = {
            "Attributes": {
                "OneTimeBootMode": "OneTimeBootSeq",
                "OneTimeBootSeqDev": device,
            }
        }
        await self.patch_bios(_payload)

    async def send_sriov_mode(self, enable):
        value = "Enabled" if enable else "Disabled"
        _payload = {
            "Attributes": {
                "SriovGlobalEnable": value,
            }
        }

        sriov_mode = await self.get_sriov_mode()
        if (sriov_mode.lower() == "enabled" and enable) or (
            sriov_mode.lower() == "disabled" and not enable
        ):
            self.logger.warning("SRIOV mode is already in that state. IGNORING.")
            return

        await self.patch_bios(_payload)
        await self.reboot_server()

    async def patch_bios(self, payload, insist=True):
        _url = "%s%s" % (self.root_uri, self.bios_uri)
        _headers = {"content-type": "application/json"}
        _first_reset = False
        payload_patch = {"@Redfish.SettingsApplyTime": {"ApplyTime": "OnReset"}}
        payload_patch.update(payload)
        for i in range(self.retries):
            _response = await self.patch_request(_url, payload_patch, _headers)
            status_code = _response.status
            if status_code in [200, 202]:
                self.logger.info("Command passed to set BIOS attribute pending values.")
                break
            else:
                self.logger.error("Command failed, error code is: %s." % status_code)
                if status_code == 503 and i - 1 != self.retries:
                    self.logger.info("Retrying to send one time boot.")
                    continue
                elif status_code == 400 and insist:
                    await self.clear_job_queue()
                    if not _first_reset:
                        await self.reset_idrac()
                        await asyncio.sleep(10)
                        _first_reset = True
                        await self.polling_host_state("On")
                    continue
                await self.error_handler(_response)

    async def check_boot(self, _interfaces_path):
        if not self.boot_devices:
            await self.get_boot_devices()

        if _interfaces_path:
            _host_type = await self.get_host_type(_interfaces_path)
            if _host_type:
                self.logger.warning("Current boot order is set to: %s." % _host_type)
                return True
            else:
                self.logger.warning(
                    "Current boot order does not match any of the given."
                )
                self.logger.info("Current boot order:")
        else:
            self.logger.info("Current boot order:")
        for device in sorted(self.boot_devices, key=lambda x: x["Index"]):
            enabled = "" if device["Enabled"] else " (DISABLED)"
            self.logger.info(
                "%s: %s%s" % (int(device["Index"]) + 1, device["Name"], enabled)
            )
        return True

    async def check_device(self, device):
        self.logger.debug("Checking device %s." % device)
        await self.get_boot_devices()
        self.logger.debug(self.boot_devices)
        boot_devices = [_device["Name"].lower() for _device in self.boot_devices]
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
            raise BadfishException("Not able to access Firmware inventory.")
        installed_devices = []
        if "error" in data:
            self.logger.debug(data["error"])
            raise BadfishException("Not able to access Firmware inventory.")
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
                if "Id" == info[0]:
                    self.logger.info("%s:" % info[1])
                if (
                    "odata" not in info[0]
                    and "Description" not in info[0]
                    and "Oem" not in info[0]
                ):
                    self.logger.info("    %s: %s" % (info[0], info[1]))

    async def get_host_type_boot_device(self, host_type, _interfaces_path):
        if _interfaces_path:
            interfaces = await self.get_interfaces_by_type(host_type, _interfaces_path)
        else:
            raise BadfishException(
                "You must provide a path to the interfaces yaml via `-i` optional argument."
            )

        return interfaces[0]

    async def toggle_boot_device(self, device):
        if not self.boot_devices:
            await self.get_boot_devices()

        if device not in [boot_device["Name"] for boot_device in self.boot_devices]:
            self.logger.warning("Accepted device names:")
            for device in self.boot_devices:
                self.logger.warning(f"{device['Name']}")
            raise BadfishException("Boot device name not found")

        new_boot_seq = self.boot_devices.copy()
        state = ""
        for boot_device in new_boot_seq:
            if boot_device["Name"] == device:
                boot_device["Enabled"] = not boot_device["Enabled"]
                state = "enabled" if boot_device["Enabled"] else "disabled"

        await self.patch_boot_seq(new_boot_seq)
        if state:
            self.logger.info(f"{device} has now been {state}")

        await self.create_bios_config_job(self.bios_uri)
        await self.reboot_server(graceful=False)
        return True

    async def get_virtual_media_config_uri(self):
        _url = "%s%s" % (self.host_uri, self.manager_resource)
        _response = await self.get_request(_url)

        try:
            raw = await _response.text("utf-8", "ignore")
            data = json.loads(raw.strip())
        except ValueError:
            raise BadfishException("Not able to access Firmware inventory.")

        vm_endpoint = data.get("VirtualMedia")
        if vm_endpoint:
            virtual_media = vm_endpoint.get("@odata.id")
            if virtual_media:
                vm_url = "%s%s" % (self.host_uri, virtual_media)
                vm_response = await self.get_request(vm_url)
                try:
                    raw = await vm_response.text("utf-8", "ignore")
                    vm_data = json.loads(raw.strip())

                    oem = vm_data.get("Oem")
                    if oem:
                        sm = oem.get("Supermicro")
                        if sm:
                            vmc = sm.get("VirtualMediaConfig")
                            if vmc:
                                return vmc.get("@odata.id")

                except ValueError:
                    raise BadfishException(
                        "Not able to check for supported virtual media unmount"
                    )

        return None

    async def get_virtual_media(self):
        _url = "%s%s" % (self.host_uri, self.manager_resource)
        _response = await self.get_request(_url)

        try:
            raw = await _response.text("utf-8", "ignore")
            data = json.loads(raw.strip())
        except ValueError:
            raise BadfishException("Not able to access Firmware inventory.")

        vm_endpoint = data.get("VirtualMedia")
        vms = []
        if vm_endpoint:
            virtual_media = vm_endpoint.get("@odata.id")
            if virtual_media:
                vm_url = "%s%s" % (self.host_uri, virtual_media)
                vm_response = await self.get_request(vm_url)
                try:
                    raw = await vm_response.text("utf-8", "ignore")
                    vm_data = json.loads(raw.strip())

                    if vm_data.get("Members"):
                        for member in vm_data["Members"]:
                            vms.append(member["@odata.id"])
                    else:
                        self.logger.warning("No active VirtualMedia found")
                        return vms

                except ValueError:
                    raise BadfishException("Not able to access Firmware inventory.")
            else:
                raise BadfishException("No VirtualMedia endpoint found")
        else:
            raise BadfishException("No VirtualMedia endpoint found")

        return vms

    async def check_virtual_media(self):
        vms = await self.get_virtual_media()
        for vm in vms:
            disc_url = "%s%s" % (self.host_uri, vm)
            disc_response = await self.get_request(disc_url)
            try:
                raw = await disc_response.text("utf-8", "ignore")
                disc_data = json.loads(raw.strip())
                self.logger.info(f"{disc_data.get('Id')}:")
                self.logger.info(f"    Name: {disc_data.get('Name')}")
                self.logger.info(f"    ImageName: {disc_data.get('ImageName')}")
                self.logger.info(f"    Inserted: {disc_data.get('Inserted')}")
            except ValueError:
                raise BadfishException(
                    "There was something wrong getting values for VirtualMedia"
                )

        return True

    async def unmount_virtual_media(self):

        vmc = await self.get_virtual_media_config_uri()
        if not vmc:
            self.logger.warning("OOB management does not support Virtual Media unmount")
            return False

        _vmc_url = "%s%s/Actions/IsoConfig.UnMount" % (self.host_uri, vmc)
        _headers = {"content-type": "application/json"}
        _payload = {}
        disc_response = await self.post_request(_vmc_url, _payload, _headers)
        if disc_response.status == 200:
            self.logger.info("Successfully unmounted all VirtualMedia")
        else:
            raise BadfishException(
                "There was something wrong unmounting the VirtualMedia"
            )

        return True

    async def get_network_adapters(self):
        _url = "%s%s/NetworkAdapters" % (self.host_uri, self.system_resource)
        _response = await self.get_request(_url)
        try:
            raw = await _response.text("utf-8", "ignore")
            na_data = json.loads(raw.strip())

            root_nics = []
            if na_data.get("Members"):
                for member in na_data["Members"]:
                    root_nics.append(member["@odata.id"])

            data = {}
            for nic in root_nics:
                net_ports_url = "%s%s/NetworkPorts" % (self.host_uri, nic)
                rn_response = await self.get_request(net_ports_url)
                rn_raw = await rn_response.text("utf-8", "ignore")
                rn_data = json.loads(rn_raw.strip())

                nic_ports = []
                if rn_data.get("Members"):
                    for member in rn_data["Members"]:
                        nic_ports.append(member["@odata.id"])

                net_df_url = "%s%s/NetworkDeviceFunctions" % (self.host_uri, nic)
                ndf_response = await self.get_request(net_df_url)
                ndf_raw = await ndf_response.text("utf-8", "ignore")
                ndf_data = json.loads(ndf_raw.strip())

                ndf_members = []
                if ndf_data.get("Members"):
                    for member in ndf_data["Members"]:
                        ndf_members.append(member["@odata.id"])

                for i, nic_port in enumerate(nic_ports):
                    np_url = "%s%s" % (self.host_uri, nic_port)
                    np_response = await self.get_request(np_url)
                    np_raw = await np_response.text("utf-8", "ignore")
                    np_data = json.loads(np_raw.strip())

                    interface = nic_port.split("/")[-1]

                    fields = [
                        "Id",
                        "LinkStatus",
                        "SupportedLinkCapabilities",
                    ]
                    values = {}
                    for field in fields:
                        value = np_data.get(field)
                        if value:
                            values[field] = value

                    ndf_url = "%s%s" % (self.host_uri, ndf_members[i])
                    ndf_response = await self.get_request(ndf_url)
                    ndf_raw = await ndf_response.text("utf-8", "ignore")
                    ndf_data = json.loads(ndf_raw.strip())
                    oem = ndf_data.get("Oem")
                    ethernet = ndf_data.get("Ethernet")
                    if ethernet:
                        mac_address = ethernet.get("MACAddress")
                        if mac_address:
                            values["MACAddress"] = mac_address
                    if oem:
                        dell = oem.get("Dell")
                        if dell:
                            dell_nic = dell.get("DellNIC")
                            vendor = dell_nic.get("VendorName")
                            if dell_nic.get("VendorName"):
                                values["Vendor"] = vendor

                    data.update({interface: values})

        except (ValueError, AttributeError):
            raise BadfishException(
                "There was something wrong getting network interfaces"
            )

        return data

    async def get_ethernet_interfaces(self):
        _url = "%s%s/EthernetInterfaces" % (self.host_uri, self.system_resource)
        _response = await self.get_request(_url)

        if _response.status == 404:
            raise BadfishException("Server does not support this functionality")

        try:
            raw = await _response.text("utf-8", "ignore")
            ei_data = json.loads(raw.strip())

            interfaces = []
            if ei_data.get("Members"):
                for member in ei_data["Members"]:
                    interfaces.append(member["@odata.id"])

            data = {}
            for interface in interfaces:
                interface_url = "%s%s" % (self.host_uri, interface)
                int_response = await self.get_request(interface_url)
                int_raw = await int_response.text("utf-8", "ignore")
                int_data = json.loads(int_raw.strip())

                int_name = int_data.get("Id")
                fields = [
                    "Name",
                    "MACAddress",
                    "Status",
                    "LinkStatus",
                    "SpeedMbps",
                ]

                values = {}
                for field in fields:
                    value = int_data.get(field)
                    if value:
                        values[field] = value

                data.update({int_name: values})

        except (ValueError, AttributeError):
            raise BadfishException(
                "There was something wrong getting network interfaces"
            )

        return data

    async def list_interfaces(self):
        na_supported = await self.check_supported_network_interfaces("NetworkAdapters")
        if na_supported:
            self.logger.debug("Getting Network Adapters")
            data = await self.get_network_adapters()
        else:
            ei_supported = await self.check_supported_network_interfaces(
                "EthernetInterfaces"
            )
            if ei_supported:
                self.logger.debug("Getting Ethernet interfaces")
                data = await self.get_ethernet_interfaces()
            else:
                self.logger.error("Server does not support this functionality")
                return False

        for interface, properties in data.items():
            self.logger.info(f"{interface}:")
            for key, value in properties.items():
                if key == "SupportedLinkCapabilities":
                    speed_key = "LinkSpeedMbps"
                    speed = value[0].get(speed_key)
                    if speed:
                        self.logger.info(f"    {speed_key}: {speed}")
                elif key == "Status":
                    health_key = "Health"
                    health = value.get(health_key)
                    if health:
                        self.logger.info(f"    {health_key}: {health}")
                else:
                    self.logger.info(f"    {key}: {value}")

        return True

    async def get_processor_summary(self):
        _url = "%s%s" % (self.host_uri, self.system_resource)
        _response = await self.get_request(_url)

        try:
            raw = await _response.text("utf-8", "ignore")
            data = json.loads(raw.strip())

            proc_data = data.get("ProcessorSummary")

            if not proc_data:
                raise BadfishException("Server does not support this functionality")

            fields = [
                "Count",
                "LogicalProcessorCount",
                "Model",
            ]

            values = {}
            for field in fields:
                value = proc_data.get(field)
                if value:
                    values[field] = value

        except (ValueError, AttributeError):
            raise BadfishException(
                "There was something wrong getting processor summary"
            )

        return values

    async def get_processor_details(self):

        _url = "%s%s/Processors" % (self.host_uri, self.system_resource)
        _response = await self.get_request(_url)

        if _response.status == 404:
            raise BadfishException("Server does not support this functionality")

        try:
            raw = await _response.text("utf-8", "ignore")
            data = json.loads(raw.strip())

            processors = []
            if data.get("Members"):
                for member in data["Members"]:
                    processors.append(member["@odata.id"])

            proc_details = {}
            for processor in processors:
                processor_url = "%s%s" % (self.host_uri, processor)
                proc_response = await self.get_request(processor_url)
                proc_raw = await proc_response.text("utf-8", "ignore")
                proc_data = json.loads(proc_raw.strip())

                proc_name = proc_data.get("Id")
                fields = [
                    "Name",
                    "InstructionSet",
                    "Manufacturer",
                    "MemoryDeviceType",
                    "MaxSpeedMHz",
                    "Model",
                    "TotalCores",
                    "TotalThreads",
                ]

                values = {}
                for field in fields:
                    value = proc_data.get(field)
                    if value:
                        values[field] = value

                proc_details.update({proc_name: values})

        except (ValueError, AttributeError):
            raise BadfishException(
                "There was something wrong getting processor details"
            )

        return proc_details

    async def get_memory_summary(self):
        _url = "%s%s" % (self.host_uri, self.system_resource)
        _response = await self.get_request(_url)

        try:
            raw = await _response.text("utf-8", "ignore")
            data = json.loads(raw.strip())

            proc_data = data.get("MemorySummary")

            if not proc_data:
                raise BadfishException("Server does not support this functionality")

            fields = [
                "MemoryMirroring",
                "TotalSystemMemoryGiB",
            ]

            values = {}
            for field in fields:
                value = proc_data.get(field)
                if value:
                    values[field] = value

        except (ValueError, AttributeError):
            raise BadfishException("There was something wrong getting memory summary")

        return values

    async def get_memory_details(self):

        _url = "%s%s/Memory" % (self.host_uri, self.system_resource)
        _response = await self.get_request(_url)

        if _response.status == 404:
            raise BadfishException("Server does not support this functionality")

        try:
            raw = await _response.text("utf-8", "ignore")
            data = json.loads(raw.strip())

            memories = []
            if data.get("Members"):
                for member in data["Members"]:
                    memories.append(member["@odata.id"])

            mem_details = {}
            for memory in memories:
                memory_url = "%s%s" % (self.host_uri, memory)
                mem_response = await self.get_request(memory_url)
                mem_raw = await mem_response.text("utf-8", "ignore")
                mem_data = json.loads(mem_raw.strip())

                mem_name = mem_data.get("Name")
                fields = [
                    "CapacityMiB",
                    "Description",
                    "Manufacturer",
                    "MemoryDeviceType",
                    "OperatingSpeedMhz",
                ]

                values = {}
                for field in fields:
                    value = mem_data.get(field)
                    if value:
                        values[field] = value

                mem_details.update({mem_name: values})

        except (ValueError, AttributeError):
            raise BadfishException("There was something wrong getting memory details")

        return mem_details

    async def get_serial_summary(self):
        _uri = "%s%s" % (self.host_uri, self.redfish_uri)
        _response = await self.get_request(_uri)

        if _response.status in [400, 404]:
            raise BadfishException("Server does not support this functionality")

        try:
            raw = await _response.text("utf-8", "ignore")
            data = json.loads(raw.strip())
            service_data = data.get("Oem").get("Dell")

            if not service_data:
                serial_uri = "%s%s/Systems/1" % (self.host_uri, self.redfish_uri)
                serial_response = await self.get_request(serial_uri)

                if _response.status in [400, 404]:
                    raise BadfishException("Server does not support this functionality")

                serial_raw = await serial_response.text("utf-8", "ignore")
                serial_data = json.loads(serial_raw.strip())
                serial_number_data = serial_data.get("SerialNumber")

                if not serial_number_data:
                    raise BadfishException("Server does not support this functionality")
                else:
                    return serial_number_data

        except (ValueError, AttributeError):
            raise BadfishException("There was something wrong getting serial summary")

        return service_data

    async def list_processors(self):
        data = await self.get_processor_summary()

        self.logger.info("Processor Summary:")
        for _key, _value in data.items():
            self.logger.info(f"    {_key}: {_value}")

        processor_data = await self.get_processor_details()

        for _processor, _properties in processor_data.items():
            self.logger.info(f"{_processor}:")
            for _key, _value in _properties.items():
                self.logger.info(f"    {_key}: {_value}")

        return True

    async def list_memory(self):
        data = await self.get_memory_summary()

        self.logger.info("Memory Summary:")
        for _key, _value in data.items():
            self.logger.info(f"    {_key}: {_value}")

        memory_data = await self.get_memory_details()

        for _memory, _properties in memory_data.items():
            self.logger.info(f"{_memory}:")
            for _key, _value in _properties.items():
                self.logger.info(f"    {_key}: {_value}")

        return True

    async def list_serial(self):
        data = await self.get_serial_summary()

        if "ServiceTag" in data:
            self.logger.info("ServiceTag:")
            self.logger.info(f"    {self.host}: {data.get('ServiceTag')}")
        else:
            self.logger.info("Serial Number:")
            self.logger.info(f"    {self.host}: {data}")

        return True

    async def change_bios_password(self, old_password, new_password):
        _url = "%s%s/Bios/Actions/Bios.ChangePassword" % (
            self.host_uri,
            self.system_resource,
        )
        _payload = {
            "PasswordName": "SetupPassword",
            "OldPassword": old_password,
            "NewPassword": new_password,
        }
        _headers = {"content-type": "application/json"}
        _response = await self.post_request(_url, _payload, _headers)

        status_code = _response.status

        if status_code in [200, 204]:
            self.logger.info("Command passed to set BIOS password.")
        elif status_code == 404:
            self.logger.error("BIOS password change not supported on this system.")
            return False
        else:
            self.logger.warning("Command failed to set BIOS password")

            await self.error_handler(_response)

        job_id = await self.create_bios_config_job(self.bios_uri)
        self.logger.warning("Host will now be rebooted for changes to take place.")
        await asyncio.sleep(5)
        await self.reboot_server()
        await asyncio.sleep(5)
        await self.check_job_status(job_id)

    async def set_bios_password(self, old_password, new_password):
        if new_password == "":
            self.logger.error("Missing argument: `--new-password`")
            return False

        await self.change_bios_password(old_password, new_password)

    async def remove_bios_password(self, old_password):
        if old_password == "":
            self.logger.error("Missing argument: `--old-password`")
            return False
        await self.change_bios_password(old_password, "")

    async def get_screenshot(self):
        _uri = self.host_uri + self.redfish_uri + "/Dell" + self.manager_resource[11:]
        _url = "%s/DellLCService/Actions/DellLCService.ExportServerScreenShot" % _uri
        _headers = {"content-type": "application/json"}
        _payload = {"FileType": "ServerScreenShot"}
        _response = await self.post_request(_url, _payload, _headers)

        status_code = _response.status
        if status_code in [200, 202]:
            self.logger.debug("POST command passed to get server screenshot.")
        elif status_code == 404:
            raise BadfishException("The system does not support screenshots.")
        else:
            if status_code == 400:
                self.logger.error("POST command failed to get the server screenshot.")
                await self.error_handler(_response)
            else:
                return None

        try:
            raw = await _response.text("utf-8", "ignore")
            data = json.loads(raw.strip())
        except ValueError:
            raise BadfishException("Error reading response from host.")

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        fqdn_short = self.host.split(".")[0]
        filename = f"{fqdn_short}_screenshot_{timestamp}.png"
        with open(filename, "wb") as fh:
            fh.write(base64.decodebytes(bytes(data["ServerScreenShotFile"], "utf-8")))
        return filename

    async def take_screenshot(self):
        filename = await self.get_screenshot()
        self.logger.info(f"Image saved: {filename}")
        return True

    async def delete_session(self):
        headers = {"content-type": "application/json"}
        _uri = "%s%s" % (self.host_uri, self.session_id)
        _response = await self.delete_request(_uri, headers=headers)
        if _response.status not in [200, 201]:
            raise BadfishException(f"Failed to delete X-Auth-Token for {self.host}")
        return


async def execute_badfish(_host, _args, logger, format_handler=None):
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
    toggle_boot_device = _args["toggle_boot_device"]
    firmware_inventory = _args["firmware_inventory"]
    clear_jobs = _args["clear_jobs"]
    check_job = _args["check_job"]
    list_jobs = _args["ls_jobs"]
    list_interfaces = _args["ls_interfaces"]
    list_processors = _args["ls_processors"]
    list_memory = _args["ls_memory"]
    list_serial = _args["ls_serial"]
    check_virtual_media = _args["check_virtual_media"]
    unmount_virtual_media = _args["unmount_virtual_media"]
    get_sriov = _args["get_sriov"]
    enable_sriov = _args["enable_sriov"]
    disable_sriov = _args["disable_sriov"]
    set_bios_attribute = _args["set_bios_attribute"]
    get_bios_attribute = _args["get_bios_attribute"]
    attribute = _args["attribute"]
    value = _args["value"]
    set_bios_password = _args["set_bios_password"]
    remove_bios_password = _args["remove_bios_password"]
    new_password = _args["new_password"]
    old_password = _args["old_password"]
    screenshot = _args["screenshot"]
    retries = int(_args["retries"])
    output = _args["output"]

    result = True

    try:
        badfish = await badfish_factory(
            _host=_host,
            _username=_username,
            _password=_password,
            _logger=logger,
            _retries=retries,
        )

        if _args["host_list"] and not _args["output"]:
            badfish.logger.info("Executing actions on host: %s" % _host)

        if device:
            await badfish.boot_to(device)
        elif boot_to_type:
            await badfish.boot_to_type(boot_to_type, interfaces_path)
        elif boot_to_mac:
            await badfish.boot_to_mac(boot_to_mac)
        elif check_boot:
            await badfish.check_boot(interfaces_path)
        elif toggle_boot_device:
            await badfish.toggle_boot_device(toggle_boot_device)
        elif firmware_inventory:
            await badfish.get_firmware_inventory()
        elif clear_jobs:
            await badfish.clear_job_queue(force)
        elif check_job:
            await badfish.check_schedule_job_status(check_job)
        elif list_jobs:
            await badfish.list_job_queue()
        elif host_type:
            await badfish.change_boot(host_type, interfaces_path, pxe)
        elif rac_reset:
            await badfish.reset_idrac()
        elif factory_reset:
            await badfish.reset_bios()
        elif power_state:
            state = await badfish.get_power_state()
            logger.info("Power state:")
            logger.info(f"    {_host}: '{state}'")
        elif power_on:
            await badfish.set_power_state("on")
        elif power_off:
            await badfish.set_power_state("off")
        elif power_cycle:
            await badfish.reboot_server(graceful=False)
        elif reboot_only:
            await badfish.reboot_server()
        elif list_interfaces:
            await badfish.list_interfaces()
        elif list_processors:
            await badfish.list_processors()
        elif list_memory:
            await badfish.list_memory()
        elif list_serial:
            await badfish.list_serial()
        elif check_virtual_media:
            await badfish.check_virtual_media()
        elif unmount_virtual_media:
            await badfish.unmount_virtual_media()
        elif get_sriov:
            sriov_mode = await badfish.get_sriov_mode()
            if sriov_mode:
                logger.info(sriov_mode)
        elif enable_sriov:
            await badfish.send_sriov_mode(True)
        elif disable_sriov:
            await badfish.send_sriov_mode(False)
        elif get_bios_attribute:
            if attribute:
                await badfish.get_bios_attribute_registry(attribute)
            else:
                data = await badfish.get_bios_attributes()
                for attribute, value in data["Attributes"].items():
                    logger.info(f"{attribute}: {value}")
        elif set_bios_attribute:
            payload = {attribute: value}
            await badfish.set_bios_attribute(payload)
        elif set_bios_password:
            await badfish.set_bios_password(old_password, new_password)
        elif remove_bios_password:
            await badfish.remove_bios_password(old_password)
        elif screenshot:
            await badfish.take_screenshot()

        if pxe and not host_type:
            await badfish.set_next_boot_pxe()

        await badfish.delete_session()
    except BadfishException as ex:
        logger.error(ex)
        result = False

    if _args["host_list"]:
        logger.info("*" * 48)
        if output and result:
            format_handler.host = _host
            format_handler.parse()
    else:
        if output and result:
            format_handler.parse()

    return _host, result


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="badfish",
        description="Tool for managing server hardware via the Redfish API.",
        allow_abbrev=False,
    )
    parser.add_argument("-H", "--host", help="iDRAC host address")
    parser.add_argument("-u", help="iDRAC username", required=True)
    parser.add_argument("-p", help="iDRAC password", required=True)
    parser.add_argument("-i", help="Path to iDRAC interfaces yaml", default=None)
    parser.add_argument("-t", help="Type of host as defined on iDRAC interfaces yaml")
    parser.add_argument(
        "-l", "--log", help="Optional argument for logging results to a file"
    )
    parser.add_argument(
        "-o",
        "--output",
        choices=["json", "yaml"],
        help="Optional argument for choosing a special output format (json/yaml), otherwise our normal format is used.",
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
        help="Path to a plain text file with a list of hosts",
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
        help="Set next boot to one-shot boot to a specific type as defined on iDRAC interfaces yaml",
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
        "--power-state",
        help="Get power state",
        action="store_true",
    )
    parser.add_argument(
        "--power-on",
        help="Power on host",
        action="store_true",
    )
    parser.add_argument(
        "--power-off",
        help="Power off host",
        action="store_true",
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
        "--toggle-boot-device",
        help="Change the enabled status of a boot device",
        default="",
    )
    parser.add_argument(
        "--firmware-inventory",
        help="Get firmware inventory",
        action="store_true",
    )
    parser.add_argument(
        "--delta",
        help="Address of the other host between which the delta should be made",
        default="",
    )
    parser.add_argument(
        "--clear-jobs",
        help="Clear any scheduled jobs from the queue",
        action="store_true",
    )
    parser.add_argument(
        "--check-job",
        help="Check a job status and details",
    )
    parser.add_argument(
        "--ls-jobs",
        help="List any scheduled jobs in queue",
        action="store_true",
    )
    parser.add_argument(
        "--ls-interfaces",
        help="List Network interfaces",
        action="store_true",
    )
    parser.add_argument(
        "--ls-processors",
        help="List Processor Summary",
        action="store_true",
    )
    parser.add_argument(
        "--ls-memory",
        help="List Memory Summary",
        action="store_true",
    )
    parser.add_argument(
        "--ls-serial",
        help="List 'Serial Number'/'Service Tag'",
        action="store_true",
    )
    parser.add_argument(
        "--check-virtual-media",
        help="Check for mounted iso images",
        action="store_true",
    )
    parser.add_argument(
        "--unmount-virtual-media",
        help="Unmount any mounted iso images",
        action="store_true",
    )
    parser.add_argument(
        "--get-sriov",
        help="Gets global SRIOV mode state",
        action="store_true",
    )
    parser.add_argument(
        "--enable-sriov",
        help="Enables global SRIOV mode",
        action="store_true",
    )
    parser.add_argument(
        "--disable-sriov",
        help="Disables global SRIOV mode",
        action="store_true",
    )
    parser.add_argument(
        "--get-bios-attribute",
        help="Get a BIOS attribute value",
        action="store_true",
    )
    parser.add_argument(
        "--set-bios-attribute",
        help="Set a BIOS attribute value",
        action="store_true",
    )
    parser.add_argument(
        "--attribute",
        help="BIOS attribute name",
        default="",
    )
    parser.add_argument(
        "--value",
        help="BIOS attribute value",
        default="",
    )
    parser.add_argument(
        "--set-bios-password",
        help="Set the BIOS password",
        action="store_true",
    )
    parser.add_argument(
        "--remove-bios-password",
        help="Removes BIOS password",
        action="store_true",
    )
    parser.add_argument(
        "--new-password",
        help="The new password value",
        default="",
    )
    parser.add_argument(
        "--old-password",
        help="The old password value",
        default="",
    )
    parser.add_argument(
        "--screenshot",
        help="Take a screenshot of the system an store it in jpg format",
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
    host = _args["host"]

    delta = _args["delta"]
    if _args["firmware_inventory"] and delta:
        tp = tempfile.NamedTemporaryFile()
        tp.write(f"{host}\n{delta}".encode())
        tp.flush()
        _args["host_list"] = tp.name
        if not _args["output"]:
            _args["output"] = "json"

    host_list = _args["host_list"]
    multi_host = True if host_list else False
    result = True
    output = _args["output"]
    bfl = BadfishLogger(_args["verbose"], multi_host, _args["log"], output)

    loop = asyncio.get_event_loop()
    tasks = []
    host_order = {}
    if host_list:
        try:
            with open(host_list, "r") as _file:
                for i, _host in enumerate(_file.readlines()):
                    if _host.isspace():
                        continue

                    host_name = _host.strip().split(".")[0]
                    host_order.update({host_name: i})
                    logger = getLogger(host_name)
                    logger.addHandler(bfl.queue_handler)
                    logger.setLevel(log_level)
                    bfl.badfish_handler.host = _host if output else None
                    fn = functools.partial(
                        execute_badfish,
                        _host.strip(),
                        _args,
                        logger,
                        bfl.queue_listener.handlers[0] if output else None,
                    )
                    tasks.append(fn)
        except IOError as ex:
            bfl.logger.debug(ex)
            bfl.logger.error("There was something wrong reading from %s" % host_list)
        results = []
        try:
            results = loop.run_until_complete(
                asyncio.gather(*[task() for task in tasks], return_exceptions=True)
            )
        except KeyboardInterrupt:
            bfl.logger.warning("Badfish terminated")
            result = False
        except (asyncio.CancelledError, BadfishException) as ex:
            bfl.logger.warning("There was something wrong executing Badfish")
            bfl.logger.debug(ex)
            result = False
        if results and not output:
            result = True
            bfl.logger.info("RESULTS:")
            for res in results:
                if len(res) > 1 and res[1]:
                    bfl.logger.info(f"{res[0]}: SUCCESSFUL")
                else:
                    bfl.logger.info(f"{res[0]}: FAILED")
                    result = False
    elif not host:
        bfl.logger.error(
            "You must specify at least either a host (-H) or a host list (--host-list)."
        )
    else:
        try:
            _host, result = loop.run_until_complete(
                execute_badfish(host, _args, bfl.logger, bfl.queue_listener.handlers[0])
            )
        except KeyboardInterrupt:
            bfl.logger.warning("Badfish terminated")
        except BadfishException as ex:
            bfl.logger.warning("There was something wrong executing Badfish")
            bfl.logger.debug(ex)
            result = False
    bfl.queue_listener.stop()

    if delta:
        bfh_output = bfl.badfish_handler.diff()
    else:
        bfh_output = bfl.badfish_handler.output(
            output if output else "normal", host_order
        )
    if _args["log"]:
        og_stdout = sys.stdout
        with open(_args["log"], "w") as f:
            sys.stdout = f
            print(bfh_output)
            sys.stdout = og_stdout
    else:
        if bfh_output:
            print(bfh_output, file=sys.stderr)

    if result:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
