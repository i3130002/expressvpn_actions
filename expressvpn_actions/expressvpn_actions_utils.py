import os
import collections
import re

Location = collections.namedtuple('Location', ['id', 'title'])


def locations():
    output = os.popen("expressvpn list").read().strip().split("\n")
    separator_index = _first(output, _starts_with_prefix("---"))
    if separator_index >= 0:
        output = output[separator_index + 2: len(output) - 2]
    locations = list(map(_location, output))
    return locations


def locations_all():
    output = os.popen("expressvpn list all").read().strip().split("\n")
    location_index = output[0].index("LOCATION")
    recommended_index = output[0].index("RECOMMENDED")
    all = [line[location_index: recommended_index].strip()
           for line in output[2:]]
    return list(map(_location, all))


def status():
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    status_raw = ansi_escape.sub('', os.popen(
        'expressvpn status').read().strip())

    if status_raw.startswith('A new version is available'):
        lines = status_raw.split('\n')
        status_raw = lines[2]
    elif not status_raw.startswith('Not connected'):
        m = re.search('(Connected to .*\n)', status_raw)
        if m:
            status_raw = m.group(1)
    vpn_status = status_raw

    return vpn_status


def has_update():
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    status_raw = ansi_escape.sub('', os.popen(
        'expressvpn status').read().strip())

    return status_raw.startswith('A new version is available')


def update_now():  # Based on https://www.reddit.com/r/Express_VPN/comments/us7j1y/comment/ion19vf/?utm_source=reddit&utm_medium=web2x&context=3
    from urllib.request import urlopen
    from bs4 import BeautifulSoup
    import os
    url = "https://www.expressvpn.com/latest?utm_source=linux_app"
    page = urlopen(url)
    soup = BeautifulSoup(page, "html.parser")
    linkTag = soup.find_all("option", text=_make_os_version())
    for tag in linkTag:
        latestVersionURL = tag['value']
        # print(debUrl)
        cVersion = re.split("expressvpn-(.*?)-", latestVersionURL)[1]
    iVersion = _checkVersion()
    if iVersion < cVersion:
        p = input('\n There is an update available. Install? [Y/N] > ')
        if p.lower() == ('y'):
            print('\n Downloading update ...\n')
            response = urlopen(latestVersionURL)
            fN = f"/tmp/expressvpn-{cVersion}.{os.path.splitext(response.url)[1]}"
            with open(fN, 'b+w') as f:
                f.write(response.read())
            os.system(f'sudo {_get_package_manager_install_code()} {fN}')
        else:
            quit()
    else:
        print('\n ExpressVPN is fully updated.\n')


# Private helpers

def _make_os_version():
    import platform
    machine = platform.machine()
    node = platform.node()
    # Based on http://helloraspberrypi.blogspot.com/2017/05/python-to-get-sys-info-on-raspberry-pi.html
    if "raspberry" in node:
        return "Raspberry Pi OS"
    bits = "64" if "64" in machine else "32"
    return f"{node.capitalize()} {bits}-bit"


def _checkVersion():
    import subprocess
    try:
        versionS = subprocess.check_output(['expressvpn', '--version'])
        versionL = versionS.split()
        return versionL[2].decode("utf-8")
    except:
        print('\n ExpressVPN is not installed. Please install from expressvpn.com. \n')
        quit()


def _get_package_manager_install_code():
    import platform
    node = platform.node()
    if node == "fedora":
        return "dnf install"
    elif node == "ubuntu" or node == "raspberry":
        return "apt install"
    elif node == "arch":
        return "pacman -U"
    return ""


def _starts_with_prefix(prefix):
    def func(str):
        return str.startswith(prefix)
    return func


def _first(arr, cond):
    for i in range(len(arr)):
        if cond(arr[i]):
            return i
    return -1


def _location(inp):
    splitted = inp.split('\t')
    return Location(splitted[0], splitted[len(splitted) - 1])
