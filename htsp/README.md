This folder contains helper functions / classes to implement an HTSP client.

HTSP is detailed here:
https://tvheadend.org/projects/tvheadend/wiki/Htsp

Usage
=====
>manager = HtspManager(['localhost', 9982], 'username', 'password')
>manager.start()
>
>// list scheduled recordings
>dvr_entries = manager.dvr_entries
