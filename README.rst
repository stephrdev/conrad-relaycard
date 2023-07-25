================
Conrad Relaycard
================

Control Conrad relaycard via python

https://www.conrad.com/p/conrad-components-197720-relay-card-component-12-v-dc-24-v-dc-197720

Usage
=====

.. code-block:: python

    from relaycard import Relaycard

    rly = Relaycard()
    rly.setup()
    rly.get_port(1, 1)
    rly.set_port(1, 1, True)