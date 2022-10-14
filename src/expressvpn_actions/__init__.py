from expressvpn_actions import expressvpn_actions_gui


def run():
    import sys
    print(__file__)

    # Create log file.
    logger = sys.stderr
    sys.stderr = logger

    # Instantiate the app.
    app = expressvpn_actions_gui.ExpressVpnActions(logger)
    expressvpn_actions_gui.Gtk.main()

if __name__ == '__main__':
    run()