#!/usr/bin/env python2
import argparse
import logging

from .card import RelayCard
from .exceptions import RelayCardError
from .state import RelayState


# TODO use typed-argument-parser
def get_opts() -> tuple[argparse.ArgumentParser, argparse.Namespace]:
    parser = argparse.ArgumentParser()

    parser.add_argument("-v", "--verbose", dest="verbose", default=0, action="count", help="Output verbosity")

    parser.add_argument(
        "-q", "--quiet", action="store_true", dest="quiet", help="Minimized output (allow easier parsing)"
    )

    parser.add_argument("-i", "--interface", dest="interface", default="/dev/ttyAMA0", help="Serial interface to use")

    parser.add_argument(
        "-a", "--address", dest="address", default=None, type=int, help="Relaycard address (not needed for --scan)"
    )

    parser.add_argument(
        "-p",
        "--port",
        dest="ports",
        action="append",
        metavar="PORT",
        default=None,
        help="Ports to get/set (only for some commands)",
        choices=("0", "1", "2", "3", "4", "5", "6", "7", "all"),
    )

    do_group = parser.add_mutually_exclusive_group()
    do_group.add_argument("--scan", action="store_true", dest="do_scan", help="Scan for relay cards")
    do_group.add_argument("--get-ports", action="store_true", dest="do_get_ports", help="Get port states on relay card")
    do_group.add_argument(
        "--set-ports", default=None, metavar="STATE", dest="do_set_ports", help="Set port states on relay card <on/off>"
    )
    do_group.add_argument(
        "--toggle-ports", action="store_true", dest="do_toggle_ports", help="Toggle port states on relay card"
    )

    args = parser.parse_args()

    if args.ports:
        if "all" in args.ports and len(args.ports) > 1:
            raise RelayCardError(f"Wrong ports {args.ports}. Do not mix relay port option all")

        if "all" in args.ports:
            args.ports = range(0, 8)
        else:
            args.ports = [int(i) for i in args.ports]

    args.loglevel = max(logging.WARNING - (args.verbose * 10), 10)

    return parser, args


def main() -> None:  # noqa C901
    parser, args = get_opts()

    logging.basicConfig(level=args.loglevel, format="%(asctime)s [%(levelname)s] %(message)s")

    card = RelayCard(args.interface)

    if args.do_scan or args.do_get_ports or args.do_set_ports or args.do_toggle_ports:
        for _ in range(0, 4):
            if card.setup():
                break

    if args.do_scan:
        if not args.quiet:
            print("Available relay cards:")

        for i in range(0, card.card_count):
            if not args.quiet:
                print(f"- Card {i} -> address for --address: {i+1}")
            else:
                print(f"card{i}={i+1}")

    elif args.do_get_ports and args.address:
        if not args.quiet:
            print(f"Reading port states on relay card {args.address}")

        state = card.get_ports(args.address)

        for i in sorted(state._state):
            if args.ports and i not in args.ports:
                continue

            if not args.quiet:
                print(f"Port {i} is {'on' if state._state[i] else 'off'}")
            else:
                print(f"port{i}={1 if state._state[i] else 0}")

    elif args.do_set_ports and args.do_set_ports in ("on", "off") and args.address:
        if not args.quiet:
            print(f"Setting port states on relay card {args.address}")

        state = card.get_ports(args.address)
        for port in args.ports:
            if not args.quiet:
                print(f"Setting port {port} to {args.do_set_ports}")

            state.set_port(port, args.do_set_ports == "on")

        card.set_ports(args.address, state)

    elif args.do_toggle_ports and args.address:
        if not args.quiet:
            print(f"Toggling port states on relay card {args.address}")

        toggle_state = RelayState()
        for port in args.ports:
            if not args.quiet:
                print(f"Toggling port {port}")
            toggle_state.set_port(port, True)

        card.toggle_ports(args.address, toggle_state)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
