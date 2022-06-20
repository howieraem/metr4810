# Useful information and instructions for wireless communication

## Using WiFi Direct on Windows
- Currently not preferred
- Check for support:
    `> ipconfig /all | findstr Description`
  Look in output for:
    `Description: Microsoft Wi-Fi Direct Virtual Adaptor`

## Using a Wireless Access Point (WAP) on Windows
- Check for support:
    `> netsh wlan show drivers`
  Look in output for:
    `Hosted network supported: Yes`
- Set up the access point:
    `> netsh wlan set hostednetwork mode=allow ssid=<MyName> key=<MyPassword>`
  Expected output:
    `The hosted network mode has been set to allow.
The SSID of the hosted network has been successfully changed.
The user key passphrase of the hosted network has been successfully changed.`
- Start the access point:
    `> netsh wlan start hostednetwork`
  Expected output:
    `The hosted network started.`

## Using a WAP on Raspberry Pi
- Currently not preferred

## Connecting to WiFi programmatically using Python
### The `wifi` package
`https://wifi.readthedocs.io/en/latest/index.html`
- CLI and Python API that uses `iwlist` output and modifies `/etc/network/interfaces`
- `etc/wpa_supplicant/wpa_supplicant.conf` and `/etc/dhcpcd.conf` are the preferred interfaces for WiFi now on Raspberry Pi, rather than `/etc/network/interfaces`
- There was an issue which may not have been caused directly by this package, but happened at the time of testing it, where all WiFi interfaces were lost somehow, and a connection was no longer possible. There are several possible causes and possible fixes, but the most common advice for this problem online was to reimage the Pi. Be sure to backup wifi-related files.

