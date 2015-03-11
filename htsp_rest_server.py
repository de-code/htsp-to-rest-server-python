#!/usr/bin/env python

if __name__ == "__main__":
    import logging
    from utils.logging_utils import StreamToLoggingRedirect
    from htsp.htsp_client import HtspManager
    from htsp_rest.htsp_rest import HtspRest
    from htsp_rest import basic_auth
    from config import htsp_rest_config
    import logging.config
    import sys

    config = htsp_rest_config.config
    logging.config.fileConfig(config['logging.configuration'])

    sys.stdout = StreamToLoggingRedirect(logging.getLogger('htsp_rest.stdout'), logging.INFO, sys.stdout)
    sys.stderr = StreamToLoggingRedirect(logging.getLogger('htsp_rest.stderr'), logging.ERROR, sys.stderr)

    # load .passwd file
    basic_auth.init()

    manager = HtspManager(config['htsp.address'], config['htsp.username'], config['htsp.password'])
    manager.init()
    rest = HtspRest(manager, htsp_rest_config.config['port'])
    rest.run()
