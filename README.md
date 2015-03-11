This project creates a [REST](http://en.wikipedia.org/wiki/Representational_state_transfer) server wrapper around a selected functionality of the [HTSP](https://tvheadend.org/projects/tvheadend/wiki/Htsp) protocol, written in Python.

The main advantage is that it will make it easier to script simple interaction with server. (Otherwise HTSP requires the client to hold a state to be able to use it)

Configuration
=============
You will need to configure the server to tell it where the HTSP server is and what credentials to use.
In the _config_ folder, Copy _htsp_rest_config.py.template_ to _htsp_rest_config.py_ and change to to match your environment.

Start / Stop
============

Either use the provided scripts:

`start-htsp-rest.server.sh

and

`stop-htsp-rest.server.sh

Or run it directly using python:

`python htsp_rest_server.py

Clients
=======
A REST cli wrapper is also provided to allow you to schedule recordings via the command line:
See [clients](clients) for further details.
