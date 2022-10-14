from . import expressvpn_actions_utils as utils
import subprocess
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GObject as gobject
from gi.repository import GLib as glib
import os


class ExpressVpnActions:

    def __init__(self, logger):
        self.REFRESH_INTERVAL = 5000
        self.ICONS_DIR = os.path.dirname(os.path.realpath(__file__))
        self.check_image()
        # Remember logger.
        self.logger = logger

        # Check status.
        self.vpn_status = utils.status()
        self.has_update = utils.has_update()
        self.is_connected = 'Not connected' not in self.vpn_status
        self.locations = utils.locations()
        self.locations_all = utils.locations_all()

        # Create tray icon.
        self.tray = Gtk.StatusIcon()
        self.tray.connect('popup-menu', self.on_right_click)

        # Update tray icon
        self.update_icon()

        # Setup refresh interval
        self.refresh(self.tray)

    def check_image(self):
        from os import path
        import os
        print(os.getcwd())
        print()
        print(path.exists(self.ICONS_DIR+'/connected.png'))

    def on_right_click(self, icon, event_button, event_time):
        self.make_menu(event_button, event_time)

    def make_menu(self, event_button, event_time):
        menu = Gtk.Menu()

        # Status
        status = Gtk.MenuItem("Status: " + self.vpn_status)
        status.set_sensitive(False)
        status.show()
        menu.append(status)

        # Connect/Disconnect
        toggle = Gtk.MenuItem(
            'Disconnect' if self.is_connected else 'Connect to last location')
        toggle.show()
        menu.append(toggle)
        toggle.connect('activate', self.toggle)

        # Update now/Updated
        update = Gtk.MenuItem(
            'Update now' if self.has_update else 'Latest version')
        update.show()
        menu.append(update)
        update.connect('activate', self.update)

        # Smart locations.
        if not self.is_connected:
            smart_submenu = Gtk.Menu()
            for location in self.locations:
                item = Gtk.MenuItem(location.title)
                item.show()
                item.connect('activate', self.connect, location.id)
                smart_submenu.append(item)

            smart = Gtk.MenuItem('Recommended locations')
            smart.set_submenu(smart_submenu)
            smart.show()
            menu.append(smart)

        # All locations.
        if not self.is_connected:
            all_submenu = Gtk.Menu()
            for location in self.locations_all:
                item = Gtk.MenuItem(location.title)
                item.show()
                item.connect('activate', self.connect, location.id)
                all_submenu.append(item)

            all = Gtk.MenuItem('All locations')
            all.set_submenu(all_submenu)
            all.show()
            menu.append(all)

        # Quit
        quit = Gtk.MenuItem('Quit')
        quit.show()
        menu.append(quit)
        quit.connect('activate', Gtk.main_quit)

        # Show the menu.
        menu.popup(None, None, None, Gtk.StatusIcon.position_menu,
                   event_button, event_time)

    def toggle(self, widget):
        try:
            action = 'disconnect' if self.is_connected else 'connect'
            output = subprocess.run(
                ['expressvpn', action], check=True, stdout=subprocess.PIPE).stdout
            self.is_connected = not self.is_connected
            self.update_icon()
        except:
            logger.write('Failed to connect.\n')

    def update(self, widget):
        try:
            utils.update_now()
        except:
            self.logger.write('Failed to update.\n')

    def connect(self, widget, location):
        try:
            output = subprocess.run(
                ['expressvpn', 'connect', location], check=True, stdout=subprocess.PIPE).stdout
            self.is_connected = not self.is_connected
            self.update_icon()
        except:
            self.logger.write('Failed to connect to ' + location + '.\n')

    def update_icon(self):
        self.tray.set_from_file(
            self.ICONS_DIR+'/connected.png' if self.is_connected else self.ICONS_DIR+'/not-connected.png')

    def refresh(self, widget):
        try:
            # Check status.
            self.vpn_status = utils.status()
            self.is_connected = 'Not connected' not in self.vpn_status

            # Update tray icon
            self.update_icon()

            # Update the list of smart locations.
            self.locations = utils.locations()

            # Schedule next refresh.
            glib.timeout_add(self.REFRESH_INTERVAL, self.refresh, self.tray)
        except:
            self.logger.write('Failed to refresh status\n')
            # self.vpn_status = status


if __name__ == "__main__":
    run()
