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
import os
import logging

import pmb.helpers.run
import pmb.helpers.other
import pmb.parse
import pmb.parse.arch


def is_registered(arch_debian):
    return os.path.exists("/proc/sys/fs/binfmt_misc/qemu-" + arch_debian)


def register(args, arch):
    """
    Get arch, magic, mask.
    """
    arch_debian = pmb.parse.arch.alpine_to_debian(arch)
    if is_registered(arch_debian):
        return
    pmb.helpers.other.check_binfmt_misc(args)
    pmb.chroot.apk.install(args, ["qemu-user-static-repack",
                                  "qemu-user-static-repack-binfmt"])
    info = pmb.parse.binfmt_info(args, arch_debian)

    # Build registration string
    # https://en.wikipedia.org/wiki/Binfmt_misc
    # :name:type:offset:magic:mask:interpreter:flags
    name = "qemu-" + arch_debian
    type = "M"
    offset = ""
    magic = info["magic"]
    mask = info["mask"]
    interpreter = "/usr/bin/qemu-" + arch_debian + "-static"
    flags = "C"
    code = ":".join(["", name, type, offset, magic, mask, interpreter,
                     flags])

    # Register in binfmt_misc
    logging.info("Register qemu binfmt (" + arch_debian + ")")
    register = "/proc/sys/fs/binfmt_misc/register"
    pmb.helpers.run.root(
        args, ["sh", "-c", 'echo "' + code + '" > ' + register])


def unregister(args, arch):
    arch_debian = pmb.parse.arch.alpine_to_debian(arch)
    binfmt_file = "/proc/sys/fs/binfmt_misc/qemu-" + arch_debian
    if not os.path.exists(binfmt_file):
        return
    logging.info("Unregister qemu binfmt (" + arch_debian + ")")
    pmb.helpers.run.root(args, ["sh", "-c", "echo -1 > " + binfmt_file])
