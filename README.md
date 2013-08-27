# matterQ

**matterQ** is a simple *Raspberry Pi* based 3D print server based on the
*lprng* spooler and the *austerusG* serial gcode host.

Jobs can be submitted to **matterQ** from any computer on the local network
and **matterQ** will store and print the gcode.

**This guide is about building matterQ from source. If you just want to use
the prepared SD card image see the [matterQ website](http://matterq.org).**

## How to Build the matterQ SD Card Image

This guide explains how the matterQ SD card image is built.

### Installing the Standard Raspbian Image

The matterQ image is currently based on the "2013-02-09-wheezy-raspbian" image.

We start with the standard image and apply several customisations to turn it
into a function 3D print server.

1.  Go to the
    [Raspberry Pi downloads page](http://www.raspberrypi.org/downloads)
    and download the following image:

        2013-07-26-wheezy-raspbian.zip

3.  Write the image to an SD card following the
    [Raspberry Pi guide](http://elinux.org/RPi_Easy_SD_Card_Setup)

4.  Place the SD card in your Raspberry Pi and power it up.

    If you have not already configured WiFi then you must connect the
    Raspberry Pi to an Ethernet network.


### Customising the Raspbian Image
Steps 1 to 5 are performed on the Raspberry Pi board after connecting by SSH.

1.  Install Git

        $ sudo apt-get update
        $ sudo apt-get install git

2.  Install matterQ

        $ cd ~
        $ git clone https://github.com/greenarrow/matterQ.git
        $ cd matterQ
        $ sudo make packages
        $ sudo make install

    This step can be skipped if WiFi is not requied.

        $ sudo make wifi

3.  Install austerusG (latest stable version)

        $ git submodule init
        $ git submodule update
        $ cd austerusG
        $ make SETUID=1
        $ sudo make SETUID=1 install

    **If just want to use matterQ on your device and do not wish to create an
    SD card image then you can stop here.**

4.  Remove Packages and Clean Image

        $ cd ~/matterQ
        $ sudo make imageprune
        $ sudo make imageclean

5.  Shutdown

        $ sudo poweroff && exit

6.  Creating Image & Clearing Free Space

    To perform this step the SD card is removed from the Raspberry Pi and
    inserted into a Linux computer.

    **/dev/sdxx** is the device of the SD card.

        $ umount /dev/sdxx1
        $ umount /dev/sdxx2
        $ sudo dd if=/dev/sdxx of=FILENAME.img count=3788800
        $ sudo mkdir -p /mnt/tmp
        $ sudo sync
        $ sudo mount -o loop,offset=$((512*122880)) FILENAME.img /mnt/tmp
        $ sudo sfill -z -l -l -f /mnt/tmp
        $ sudo sync
        $ sudo umount /mnt/tmp
        $ zip FILENAME.zip FILENAME.img

