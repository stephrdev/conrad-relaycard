================
Conrad Relaycard
================

Control Conrad relaycard via python

https://www.conrad.com/p/conrad-components-197720-relay-card-component-12-v-dc-24-v-dc-197720

Usage
=====

.. code-block:: python

    from conrad_relaycard import Relaycard

    rly = Relaycard()
    rly.setup()
    rly.get_port(1, 1)
    rly.set_port(1, 1, True)

via CLI
*******

.. code-block:: console

    usage: conrad-relaycard [-h] [-v] [-q] [-i INTERFACE] [-a ADDRESS] [-p PORT] [--scan] [--get-ports] [--set-ports STATE] [--toggle-ports]

    options:
      -h, --help            show this help message and exit
      -v, --verbose         Output verbosity
      -q, --quiet           Minimized output (allow easier parsing)
      -i INTERFACE, --interface INTERFACE
                            Serial interface to use
      -a ADDRESS, --address ADDRESS
                            Relaycard address (not needed for --scan)
      -p PORT, --port PORT  Ports to get/set (only for some commands)
      --scan                Scan for relay cards
      --get-ports           Get port states on relay card
      --set-ports STATE     Set port states on relay card <on/off>
      --toggle-ports        Toggle port states on relay card
