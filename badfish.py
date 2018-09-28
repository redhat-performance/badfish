#! /usr/bin/env python

import argparse
import json
import re
import requests
import sys
import time
import warnings
import yaml

warnings.filterwarnings("ignore")


def get_bios_boot_mode(_host, _username, _password):
    _response = requests.get(
        "https://%s/redfish/v1/Systems/System.Embedded.1/Bios" % _host, verify=False, auth=(_username, _password)
    )
    data = _response.json()
    return data[u"Attributes"]["BootMode"]


def get_boot_seq(_bios_boot_mode):
    if _bios_boot_mode == "Uefi":
        return "UefiBootSeq"
    else:
        return "BootSeq"


def get_boot_devices(_host, _username, _password, _boot_seq):
    _response = requests.get(
        "https://%s/redfish/v1/Systems/System.Embedded.1/BootSources" % _host,
        verify=False,
        auth=(_username, _password),
    )
    data = _response.json()
    return data[u"Attributes"][_boot_seq]


def change_boot_order(_host, _username, _password):
    with open(interfaces_path, "r") as f:
        try:
            definitions = yaml.safe_load(f)
        except yaml.YAMLError as ex:
            print(ex)
            sys.exit(1)

    host_model = host.split(".")[0].split("-")[-1]
    interfaces = definitions["%s_%s_interfaces" % (host_type, host_model)].split(",")

    bios_boot_mode = get_bios_boot_mode(_host, _username, _password)
    boot_seq = get_boot_seq(bios_boot_mode)
    boot_devices = get_boot_devices(_host, _username, _password, boot_seq)
    change = False
    for i in range(len(interfaces)):
        for device in boot_devices:
            if interfaces[i] == device[u"Name"]:
                if device[u"Index"] != i:
                    device[u"Index"] = i
                    change = True
                break

    if change:
        url = "https://%s/redfish/v1/Systems/System.Embedded.1/BootSources/Settings" % host
        payload = {"Attributes": {boot_seq: boot_devices}}
        headers = {"content-type": "application/json"}
        response = requests.patch(
            url, data=json.dumps(payload), headers=headers, verify=False, auth=(username, password)
        )
        if response.status_code == 200:
            print("- PASS: PATCH command passed to update boot order")
        else:
            print("- FAIL: There was something wrong with your request")
    else:
        print("- WARNING: No changes were made since the boot order already matches the requested.")
        sys.exit()


def set_next_boot_pxe(_host, _username, _password):
    _url = "https://%s/redfish/v1/Systems/System.Embedded.1" % _host
    _payload = {"Boot": {"BootSourceOverrideTarget": "Pxe"}}
    _headers = {"content-type": "application/json"}
    _response = requests.patch(
        _url, data=json.dumps(_payload), headers=_headers, verify=False, auth=(_username, _password)
    )
    status_code = _response.status_code
    time.sleep(5)
    if status_code == 200:
        print('- PASS: PATCH command passed to set next boot onetime boot device to: "%s"' % "Pxe")
    else:
        print("- FAIL: Command failed, error code is %s" % status_code)
        detail_message = str(_response.__dict__)
        print(detail_message)
        sys.exit()


def create_bios_config_job(_host, _username, _password):
    _url = "https://%s/redfish/v1/Managers/iDRAC.Embedded.1/Jobs" % _host
    _payload = {"TargetSettingsURI": "/redfish/v1/Systems/System.Embedded.1/Bios/Settings"}
    _headers = {"content-type": "application/json"}
    _response = requests.post(
        _url, data=json.dumps(_payload), headers=_headers, verify=False, auth=(_username, _password)
    )
    statusCode = _response.status_code

    if statusCode == 200:
        print("- PASS: POST command passed to create target config job, status code 200 returned.")
    else:
        print("- FAIL: POST command failed to create BIOS config job, status code is %s" % statusCode)
        detail_message = str(_response.__dict__)
        print(detail_message)
        sys.exit()
    convert_to_string = str(_response.__dict__)
    job_id_search = re.search("JID_.+?,", convert_to_string).group()
    _job_id = re.sub("[,']", "", job_id_search)
    print("- INFO: %s job ID successfully created" % _job_id)
    return _job_id


def get_job_status(_host, _username, _password, _job_id):
    while True:
        req = requests.get(
            "https://%s/redfish/v1/Managers/iDRAC.Embedded.1/Jobs/%s" % (_host, _job_id),
            verify=False,
            auth=(_username, _password),
        )
        statusCode = req.status_code
        if statusCode == 200:
            print("- PASS: Command passed to check job status, code 200 returned")
            time.sleep(10)
        else:
            print("- FAIL: Command failed to check job status, return code is %s" % statusCode)
            print("    Extended Info Message: {0}".format(req.json()))
            sys.exit()
        data = req.json()
        if data[u"Message"] == "Task successfully scheduled.":
            print("- PASS: job id %s successfully scheduled" % _job_id)
            break
        else:
            print("- WARNING: JobStatus not scheduled, current status is: %s" % data[u"Message"])


def reboot_server(_host, _username, _password):
    _response = requests.get(
        "https://%s/redfish/v1/Systems/System.Embedded.1/" % _host, verify=False, auth=(_username, _password)
    )
    data = _response.json()
    print("- WARNING: Current server power state is: %s" % data[u"PowerState"])
    if data[u"PowerState"] == "On":
        _url = "https://%s/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset" % _host
        _payload = {"ResetType": "GracefulRestart"}
        _headers = {"content-type": "application/json"}
        _response = requests.post(
            _url, data=json.dumps(_payload), headers=_headers, verify=False, auth=(_username, _password)
        )
        statusCode = _response.status_code
        if statusCode == 204:
            print("- PASS: Command passed to gracefully restart server, code return is %s" % statusCode)
            time.sleep(3)
        else:
            print("- FAIL: Command failed to gracefully restart server, status code is: %s" % statusCode)
            print("    Extended Info Message: {0}".format(_response.json()))
            sys.exit()
        count = 0
        while True:
            _response = requests.get(
                "https://%s/redfish/v1/Systems/System.Embedded.1/" % _host, verify=False, auth=(_username, _password)
            )
            data = _response.json()
            if data[u"PowerState"] == "Off":
                print("- PASS: GET command passed to verify server is in OFF state")
                break
            elif count == 20:
                print("- WARNING: unable to graceful shutdown the server, will perform forced shutdown now")
                _url = "https://%s/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset" % _host
                _payload = {"ResetType": "ForceOff"}
                _headers = {"content-type": "application/json"}
                _response = requests.post(
                    _url, data=json.dumps(_payload), headers=_headers, verify=False, auth=(_username, _password)
                )
                statusCode = _response.status_code
                if statusCode == 204:
                    print("- PASS: Command passed to forcefully power OFF server, code return is %s" % statusCode)
                    time.sleep(10)
                else:
                    print("- FAIL, Command failed to gracefully power OFF server, status code is: %s" % statusCode)
                    print("    Extended Info Message: {0}".format(_response.json()))
                    sys.exit()

            else:
                time.sleep(1)
                count += 1
                continue

        _payload = {"ResetType": "On"}
        _headers = {"content-type": "application/json"}
        _response = requests.post(
            _url, data=json.dumps(_payload), headers=_headers, verify=False, auth=(_username, _password)
        )
        statusCode = _response.status_code
        if statusCode == 204:
            print("- PASS: Command passed to power ON server, code return is %s" % statusCode)
        else:
            print("- FAIL: Command failed to power ON server, status code is: %s" % statusCode)
            print("    Extended Info Message: {0}".format(_response.json()))
            sys.exit()
    elif data[u"PowerState"] == "Off":
        _url = "https://%s/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset" % _host
        _payload = {"ResetType": "On"}
        _headers = {"content-type": "application/json"}
        _response = requests.post(
            _url, data=json.dumps(_payload), headers=_headers, verify=False, auth=(_username, _password)
        )
        statusCode = _response.status_code
        if statusCode == 204:
            print("- PASS: Command passed to power ON server, code return is %s" % statusCode)
        else:
            print("- FAIL: Command failed to power ON server, status code is: %s" % statusCode)
            print("    Extended Info Message: {0}".format(_response.json()))
            sys.exit()
    else:
        print("- FAIL: unable to get current server power state to perform either reboot or power on")
        sys.exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Client tool for changing boot order via Redfish API.")
    parser.add_argument("-H", help="iDRAC host address", required=True)
    parser.add_argument("-u", help="iDRAC username", required=True)
    parser.add_argument("-p", help="iDRAC password", required=True)
    parser.add_argument("-i", help="Path to iDRAC interfaces yaml", required=True)
    parser.add_argument("-t", help="Type of host. Accepts: foreman, director", required=True)
    parser.add_argument("--pxe", help="Set next boot to one-shot boot PXE", action="store_true")

    args = vars(parser.parse_args())

    host = args["H"]
    username = args["u"]
    password = args["p"]
    host_type = args["t"]
    interfaces_path = args["i"]
    pxe = args["pxe"]

    if host_type.lower() not in ("foreman", "director"):
        raise argparse.ArgumentTypeError('Expected values for -t argument are "foreman" or "director"')

    change_boot_order(host, username, password)
    if pxe:
        set_next_boot_pxe(host, username, password)
    job_id = create_bios_config_job(host, username, password)
    get_job_status(host, username, password, job_id)
    reboot_server(host, username, password)
