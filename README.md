# ExpressVPN Actions

Tray icon for displaying status of ExpressVPN client/daemon on Linux desktops.

Icons are modefied using ExpressVPN log.

## Requirements

Requires Gtk3 for building and running since it's using Gtk3's StatusIcon for controlling system tray.

The logic relies on the `expressvpn` CLI utility output, so there's a chance it could break with the next released version of ExpressVPN. In that case, feel free to file an issue here, so I can update the code.

## Building

It's just a python script, duh.

## Packaging

```
python3 setup.py sdist
```

## Installing

```
sudo pip3 install .
```

or

```
sudo python3 setup.py install
```

## Running

Can be as simple as
```
expressvpn_actions_gui &
```


# Based on
[ExpresssVPN tray](https://github.com/cog1to/expressvpn-tray)
