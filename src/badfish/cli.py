""" Implementation of the command line interface.

"""
from argparse import ArgumentParser, ArgumentTypeError

from .badfish import Badfish
from . import __version__
from .core import config
from .core import logger

__all__ = "main",


def main(argv=None):
    """ Execute the application CLI.

    :param argv: argument list to parse (sys.argv by default)
    """
    args = _args(argv)
    logger.start(args.warn)
    logger.debug("starting execution")
    config.core.logging = args.warn
    host = args.host
    username = args.username
    password = args.password
    host_type = args.type
    interfaces_path = args.interfaces
    pxe = args.pxe
    reboot = args.reboot_only

    badfish = Badfish(host, username, password)

    if reboot:
        badfish.reboot_server()
    else:
        if host_type.lower() not in ("foreman", "director"):
            raise ArgumentTypeError('Expected values for -t argument are "foreman" or "director"')

        badfish.change_boot_order(interfaces_path, host_type)

        if pxe:
            badfish.set_next_boot_pxe()
        jobs_queue = badfish.get_job_queue()
        if jobs_queue:
            badfish.clear_job_queue(jobs_queue)
        job_id = badfish.create_bios_config_job()
        badfish.get_job_status(job_id)
        badfish.reboot_server()
    logger.debug("successful completion")
    return 0


def _args(argv):
    """ Parse command line arguments.

    :param argv: argument list to parse
    """
    parser = ArgumentParser()
    parser.add_argument("-H", "--host", help="iDRAC host address", required=True)
    parser.add_argument("-u", "--username", help="iDRAC username", required=True)
    parser.add_argument("-p", "--password", help="iDRAC password", required=True)
    parser.add_argument("-i", "--interfaces", help="Path to iDRAC interfaces yaml", required=True)
    parser.add_argument("-t", "--type", help="Type of host. Accepts: foreman, director", required=True)
    parser.add_argument("--pxe", action="store_true",
                        help="Set next boot to one-shot boot PXE")
    parser.add_argument("-r", "--reboot-only", action="store_true",
                        help="Flag for only rebooting the host")
    parser.add_argument("-v", "--version", action="version",
                        version="badfish {:s}".format(__version__),
                        help="print version and exit")
    parser.add_argument("-w", "--warn", default="WARN",
                        help="logger warning level [WARN]")
    args = parser.parse_args(argv)
    return args


# Make the module executable.

if __name__ == "__main__":
    try:
        status = main()
    except Exception:
        logger.critical("shutting down due to fatal error")
        raise  # print stack trace
    else:
        raise SystemExit(status)
