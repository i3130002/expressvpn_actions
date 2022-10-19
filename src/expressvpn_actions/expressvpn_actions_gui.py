import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib as glib
from gi.repository import Gtk
import subprocess


class ExpressVpnActions:

    def __init__(self, logger):
        from expressvpn_actions import expressvpn_actions_utils as utils
        self.utils = utils
        self.STATUS_REFRESH_INTERVAL = 1000
        self.UPDATE_REFRESH_INTERVAL = 1000 * 3600
        self.ICONS_DIR = os.path.dirname(os.path.realpath(__file__))
        self.check_image()
        # Remember logger.
        self.logger = logger
        self.tray = Gtk.StatusIcon()

        # Setup refresh interval
        self.refresh_status(self.tray)
        self.refresh_update(self.tray)

        # Create tray icon.
        self.tray.connect('popup-menu', self.on_right_click)
        self.tray.connect('activate', self.make_menu)

    def check_image(self):
        from os import path
        # import os
        # print(os.getcwd())
        # print()
        print("Working images:", path.exists(self.ICONS_DIR+'/connected.png'))

    def on_right_click(self, icon, event_button, event_time):
        self.make_menu(icon)

    def make_menu(self, icon):
        menu = Gtk.Menu()
        event=Gtk.get_current_event()
        event_button=event.get_button()[1] #this gets the button value of gtk event.
        event_time = Gtk.get_current_event_time()
        # Status
        status_item = Gtk.MenuItem("Status: " + self.vpn_status)
        status_item.set_sensitive(False)
        status_item.show()
        menu.append(status_item)

        # Connect/Disconnect
        status_toggle_item = Gtk.MenuItem(
            'Disconnect' if self.is_connected else 'Connect to last location')
        status_toggle_item.show()
        menu.append(status_toggle_item)
        status_toggle_item.connect('activate', self.toggle_connection)

        # Update now/Updated
        update_item = Gtk.MenuItem(
            'Update now' if self.has_update else f'Latest version {self.version}')
        update_item.set_sensitive(self.has_update)
        update_item.show()
        menu.append(update_item)
        update_item.connect('activate', self.update)

        # Smart locations.
        if not self.is_connected:
            smart_submenu = Gtk.Menu()
            for location in self.locations:
                item = Gtk.MenuItem(location.title)
                item.show()
                item.connect('activate', self.connect_to, location.id)
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
                item.connect('activate', self.connect_to, location.id)
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

    def toggle_connection(self, widget):
        try:
            action = 'disconnect' if self.is_connected else 'connect'
            output = subprocess.run(
                ['expressvpn', action], check=True, stdout=subprocess.PIPE).stdout
            self.is_connected = not self.is_connected
            self.update_icon()
        except:
            self.logger.write(f'Failed to {action}.\n')

    def update(self, widget):
        try:
            if(self.has_update):
                self.utils.update_now()
        except:
            self.logger.write('Failed to update.\n')

    def connect_to(self, widget, location):
        try:
            output = subprocess.run(
                ['expressvpn', 'connect', location], check=True, stdout=subprocess.PIPE).stdout
            self.is_connected = not self.is_connected
            self.update_icon()
        except:
            self.logger.write('Failed to connect to ' + location + '.\n')

    def update_icon(self):
        if(hasattr(self,"has_update") and self.has_update):
            self.tray.set_from_file(
                self.ICONS_DIR+'/has-update.png')
        else:
            self.tray.set_from_file(
                self.ICONS_DIR+'/connected.png' if self.is_connected else self.ICONS_DIR+'/not-connected.png')

    def refresh_status(self, widget):
        try:
            # Check status.
            self.vpn_status = self.utils.status()
            self.is_connected = 'Not connected' not in self.vpn_status

            # Update tray icon
            self.update_icon()

            # Update the list of smart locations.
            self.locations = self.utils.locations()
            self.locations_all = self.utils.locations_all()

            # Schedule next refresh.
            glib.timeout_add(self.STATUS_REFRESH_INTERVAL,
                             self.refresh_status, self.tray)
        except Exception as _:
            self.logger.write('Failed to refresh status\n')
            # self.vpn_status = status

    def refresh_update(self, widget):
        try:
            # Check status.
            self.has_update = self.utils.has_update()
            self.version = self.utils.get_version()

            # Update tray icon
            self.update_icon()

            # Schedule next refresh.
            glib.timeout_add(self.UPDATE_REFRESH_INTERVAL,
                             self.refresh_update, self.tray)
        except Exception as _:
            self.logger.write('Failed to refresh update\n')
            # self.vpn_status = status


if __name__ == "__main__":
    run()
