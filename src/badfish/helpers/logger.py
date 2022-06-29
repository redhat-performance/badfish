import json
import yaml

try:
    # Python 3.7 and newer, fast reentrant implementation
    # without task tracking (not needed for that when logging)
    from queue import SimpleQueue as Queue
except ImportError:
    from queue import Queue
from logging.handlers import QueueHandler, QueueListener

from logging import (
    Formatter,
    FileHandler,
    DEBUG,
    INFO,
    ERROR,
    StreamHandler,
    getLogger,
)


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


class BadfishHandler(StreamHandler):
    def __init__(self, format_flag=False):
        StreamHandler.__init__(self)
        self.messages = {}
        self.formatted_msg = []
        self.output_dict = dict()
        self.host = None
        self.format_flag = format_flag

    def emit(self, record):
        if not self.format_flag:
            self.formatted_msg.append(self.formatter.format(record))
            return

        if record.levelno == INFO and record.msg != "*" * 48:
            if record.name not in self.messages:
                self.messages.update({record.name: record.msg + "\n"})
            else:
                self.messages[record.name] += record.msg + "\n"
        elif record.levelno == ERROR:
            self.output_dict = {"error": True, "error_msg": record.msg}

    def parse(self):
        try:
            if self.host:
                host_name = self.host.strip().split(".")[0]
                new_dict = yaml.safe_load(self.messages[host_name])
                self.output_dict.update({self.host: new_dict.copy()})
                self.host = None
            else:
                new_dict = yaml.safe_load(self.messages["src.badfish.helpers.logger"])
                self.output_dict.update(new_dict.copy())
        except yaml.YAMLError:
            self.output_dict = {"unsupported_command": True}

    def diff(self):
        try:
            if self.output_dict["error"]:
                return f"ERROR - {self.output_dict['error_msg']}"
        except KeyError:
            host_first, host_second, *_ = self.output_dict.keys()
            first, second, *_ = self.output_dict.values()
            diff_dict = {host_first: {}, host_second: {}}
            for i in first:
                for j in second:
                    if first[i]["SoftwareId"] == second[j]["SoftwareId"] \
                        and first[i]["Version"] != second[j]["Version"] \
                            and first[i]["SoftwareId"] != 0:
                        diff_dict[host_first].update({i: {
                            "Version": first[i]["Version"],
                            "Name": first[i]["Name"],
                        }})
                        diff_dict[host_second].update({j: {
                            "Version": second[j]["Version"],
                            "Name": second[j]["Name"],
                        }})

            if diff_dict[host_first] == {}:
                return "{}"
            output = ""
            formatted = json.dumps(diff_dict[host_first], indent=4, sort_keys=False, default=str)
            len_first = (max(len(line) for line in formatted.splitlines())) + 10
            output += f"{host_first}:".ljust(len_first)
            output += f"{host_second}:\n"
            for i, j in zip(diff_dict[host_first], diff_dict[host_second]):
                output += f"{i}".ljust(len_first)
                output += f"{j}\n"
                output += f"\t- Name: {(diff_dict[host_first][i])['Name']}".ljust(len_first)
                output += f"\t- Name: {(diff_dict[host_second][j])['Name']}\n"
                output += f"\t- Version: {(diff_dict[host_first][i])['Version']}".ljust(len_first)
                output += f"\t- Version: {(diff_dict[host_second][j])['Version']}\n"
            return output

    def output(self, output_type, host_order=None):
        if output_type == "json":
            return json.dumps(self.output_dict, indent=4, sort_keys=False, default=str)
        elif output_type == "yaml":
            return yaml.dump(
                self.output_dict,
                sort_keys=False,
                indent=4,
                default_flow_style=False,
                Dumper=NoAliasDumper,
            )
        else:
            if len(host_order) > 2:
                sorted_msg = [
                    x
                    for x in sorted(
                        self.formatted_msg, key=lambda y: host_order[y.split()[0][1:-1]]
                    )
                ]
            else:
                sorted_msg = self.formatted_msg
            return "\n".join(sorted_msg)


class BadfishLogger:
    def __init__(self, verbose=False, multi_host=False, log_file=None, output=None):
        self.log_level = DEBUG if verbose else INFO
        self.multi_host = multi_host
        self.log_file = log_file

        _host_name_tag = "[%(name)s] " if self.multi_host else ""
        _format_str = f"{_host_name_tag}- %(levelname)-8s - %(message)s"
        _file_format_str = (
            f"%(asctime)-12s: {_host_name_tag}- %(levelname)-8s - %(message)s"
        )

        self.badfish_handler = BadfishHandler(True if output else False)
        self.badfish_handler.setFormatter(Formatter(_format_str))
        self.badfish_handler.setLevel(INFO)

        _queue = Queue()
        self.queue_listener = QueueListener(_queue, self.badfish_handler)
        self.queue_handler = QueueHandler(_queue)

        self.logger = getLogger(__name__)
        self.logger.addHandler(self.queue_handler)
        self.logger.setLevel(self.log_level)

        self.queue_listener.start()

        if self.log_file:
            self.file_handler = FileHandler(self.log_file)
            self.file_handler.setFormatter(Formatter(_file_format_str))
            self.file_handler.setLevel(self.log_level)
            self.queue_listener.handlers = self.queue_listener.handlers + (
                self.file_handler,
            )
