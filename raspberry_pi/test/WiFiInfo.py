'''
    Obtain Wi-Fi connection information. Requires the python-wifi package,
    and consequently is not compatible with Windows.
'''
from pythonwifi.iwlibs import Wireless


class WiFiInfo(object):
    def __init__(self, device_name='wlan0'):
        self.wifi = Wireless(device_name)
    
    def getName(self):
        return self.wifi.getEssid()

    def getSpeed(self):
        return float(self.wifi.getBitrate()[:-4].strip())  # Omit the units

    def getQuality(self):
        _, qualities, _, _ = self.wifi.getStatistics()
        return float(qualities.quality) / 70.0

    def getSignalLevel(self):
        _, qualities, _, _ = self.wifi.getStatistics()
        return qualities.signallevel - 256  # A bug in python-wifi lib
