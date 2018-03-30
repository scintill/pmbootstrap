"""
Copyright 2018 Oliver Smith

This file is part of pmbootstrap.

pmbootstrap is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pmbootstrap is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pmbootstrap.  If not, see <http://www.gnu.org/licenses/>.
"""
import logging
import os
import pmb.config


def deviceinfo(args, device=None):
    """
    :param device: defaults to args.device
    """
    if not device:
        device = args.device

    if not os.path.exists(args.aports):
        logging.fatal("Aports directory is missing")
        logging.fatal("Please provide a path to the aports directory using the -p flag")
        raise RuntimeError("Aports directory missing")

    aport = args.aports + "/device/device-" + device
    if not os.path.exists(aport) or not os.path.exists(aport + "/deviceinfo"):
        logging.fatal("You will need to create a device-specific package")
        logging.fatal("before you can continue. Please create at least the")
        logging.fatal("following files:")
        logging.fatal(aport + "/APKBUILD")
        logging.fatal(aport + "/deviceinfo")
        raise RuntimeError("Incomplete device information")

    ret = {}
    path = aport + "/deviceinfo"
    with open(path) as handle:
        for line in handle:
            if not line.startswith("deviceinfo_"):
                continue
            if "=" not in line:
                raise SyntaxError(path + ": No '=' found:\n\t" + line)
            split = line.split("=", 1)
            key = split[0][len("deviceinfo_"):]
            value = split[1].replace("\"", "").replace("\n", "")
            ret[key] = value

    # Assign empty string as default
    for key in pmb.config.deviceinfo_attributes:
        if key not in ret:
            ret[key] = ""

    # Sanity check: "flash_methods" is legacy
    if "flash_methods" in ret:
        raise RuntimeError("deviceinfo_flash_methods has been renamed to"
                           " deviceinfo_flash_method. Please adjust your"
                           " deviceinfo file: " + path)

    # Sanity check: "external_disk*" is legacy
    if "external_disk" in ret or "external_disk_install" in ret:
        raise RuntimeError("Instead of deviceinfo_external_disk and"
                           " deviceinfo_external_disk_install, please use the"
                           " new variable deviceinfo_external_storage in your"
                           " deviceinfo file: " + path)

    return ret
