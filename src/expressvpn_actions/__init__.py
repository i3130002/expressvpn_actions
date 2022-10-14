from . import expressvpn_actions


def run():
    import sys
    print(__file__)

    # Create log file.
    logger = sys.stderr
    sys.stderr = logger

    # Instantiate the app.
    app = expressvpn_actions.ExpressVpnActions(logger)
    expressvpn_actions.Gtk.main()

if __name__ == '__main__':
    run()