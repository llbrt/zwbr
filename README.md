# DISCLAIMER

This project was created thanks to documentations and tools (such as OpenZWave)
freely available on the Internet.
It is NOT certified in any way, use it at your own risks.
If the manufacturer of your controller provides a tool to save and
restore a controller, you should use it.

## Why?

My controller lost its configuration. I had to include again all the
modules (some were not really easy to reach) and reconfigure the home automation
software.

But I didn't find any tool for my controller to prevent this from happening again, so
I created this project.

With this command, I saved the controller and restored the network on a more recent
controller and now the home automation software works better.

I will now backup the controller whenever the network is modified.

# zwbr

This tool allows you to backup and restore a part of the NVM of a Z-Wave controller.
This part of the NVM contains the home-id and the nodes included in the network. So you
may restore your network after a crash of your controller without the need to include
again all the nodes.

It has been successfully tested with an `AEOTEC Z-Stick GEN5` and a `ZWave.me` controller as primary
controllers. It should work with most of the USB Z-Wave 500 controllers.

No test was done with a secondary controller.

It works on Windows and Linux (and probably MacOS).

## Requirements

This tool needs Python 3.6 or upper; the module `pyserial` must be installed.
The other required modules should be installed by default.

```
pip3 install -r requirements.txt
````

# Usage

Launch `python3 zwbr.py -h` to display the help message.

You may redirect the output of the command to a file: `python3 zwbr.py COM5 -n > nodes.txt`

# Features

## Display controller informations

The home-id and some informations about the controller are displayed (manufacturer, chip, version).

## Nodes

The option `-n` lists the nodes and display information about them.

## Backup

Writes the NVM to the destination file. The destination file must not exist and
is deleted on failure.

A new backup should be done whenever the Z-Wave network is modified (inclusion or exclusion of nodes).

## Restore

Reads the file and replaces the NVM of the controller. The source file must be
a backup of your controller.

If you restore the NVM from one controller to another, make sure that the backed-up
controller is out of reach of the Z-Wave network.

```diff
- This option is the dangerous one, use it with caution and at your own risks -
```

## Verbose mode

This option displays the Z-Wave messages exchanged between the host and the controller.
