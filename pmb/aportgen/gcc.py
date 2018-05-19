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
import pmb.aportgen.core
import pmb.helpers.git
import pmb.helpers.run


def generate(args, pkgname):
    # Copy original aport
    arch = pkgname.split("-")[1]
    upstream = pmb.aportgen.core.get_upstream_aport(args, "main/gcc")
    pmb.helpers.run.user(args, ["cp", "-r", upstream, args.work + "/aportgen"])

    # Architectures to build this package for
    arches = list(pmb.config.build_device_architectures)
    arches.remove(arch)

    # Rewrite APKBUILD
    fields = {
        "pkgname": pkgname,
        "pkgdesc": "Stage2 cross-compiler for " + arch,
        "arch": " ".join(arches),
        "depends": "isl binutils-" + arch,
        "makedepends_build": "gcc g++ paxmark bison flex texinfo gawk zip gmp-dev mpfr-dev mpc1-dev zlib-dev",
        "makedepends_host": "linux-headers gmp-dev mpfr-dev mpc1-dev isl-dev zlib-dev musl-dev-" + arch + " binutils-" + arch,
        "subpackages": "g++-" + arch + ":gpp",

        "LIBGOMP": "false",
        "LIBGCC": "false",
        "LIBATOMIC": "false",
        "LIBITM": "false",
    }

    below_header = "CTARGET_ARCH=" + arch + """
        CTARGET="$(arch_to_hostspec ${CTARGET_ARCH})"
        LANG_OBJC=false
        LANG_JAVA=false
        LANG_GO=false
        LANG_FORTRAN=false
        LANG_ADA=false
        options="!strip !tracedeps"

        # abuild doesn't try to tries to install "build-base-$CTARGET_ARCH"
        # when this variable matches "no*"
        BOOTSTRAP="nobuildbase"

        # abuild will only cross compile when this variable is set, but it
        # needs to find a valid package database in there for dependency
        # resolving, so we set it to /.
        CBUILDROOT="/"

        _cross_configure="--disable-bootstrap --with-sysroot=/usr/$CTARGET"
    """

    replace_simple = {
        # Do not package libstdc++, do not add "g++-$ARCH" here (already
        # did that explicitly in the subpackages variable above, so
        # pmbootstrap picks it up properly).
        '*subpackages="$subpackages libstdc++:libcxx:*': None,

        # We set the cross_configure variable at the beginning, so it does not
        # use CBUILDROOT as sysroot. In the original APKBUILD this is a local
        # variable, but we make it a global one.
        '*_cross_configure=*': None,
    }

    pmb.aportgen.core.rewrite(args, pkgname, "main/gcc", fields,
                              replace_simple=replace_simple,
                              below_header=below_header)
