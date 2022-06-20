"""
winWifi.py

Retrieve WiFi information on Windows
"""
import subprocess as sp


def get_info():
    """Get WiFi information from the windows interface
    """
    # Run command in subprocess
    interfaces = sp.Popen("netsh wlan show interfaces", stdout=sp.PIPE)
    # Retrieve stdout text
    output = interfaces.stdout.read()
    # print output

    state = get_value(output, "State")
    # print state
    if state == "connected":
        transmit_rate = get_value(output, "Transmit rate")
        signal = get_value(output, "Signal")
        return transmit_rate, signal
    else:
        return None


def get_value(data, name):
    """Get the value corresponding to name in a newline-separate list
    of colon-separated name-value pairs.
    """
    name_pos = data.find(name)
    # print name_pos
    # print data[name_pos:]

    # Search for the nearest semi-colon after name.
    # After that should be the value. So index the data from the start
    # position of the value to the end of the line.
    value_start = name_pos + data[name_pos:].find(":") + 1
    value_end = name_pos + data[name_pos:].find("\n")
    value = data[value_start : value_end].strip()
    return value


if __name__ == '__main__':
    print get_info()

