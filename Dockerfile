FROM gliderlabs/alpine:3.5

# install pmOS repos
RUN apk add --no-cache \
	openssl wget ca-certificates
RUN wget --quiet https://raw.githubusercontent.com/postmarketOS/pmbootstrap/master/keys/pmos-5a03a13a.rsa.pub -P /etc/apk/keys
RUN echo http://postmarketos.brixit.nl >> /etc/apk/repositories

RUN apk add --no-cache \
	gcc binutils musl-dev gcc-armhf binutils-armhf \
	bison flex gmp-dev mpfr-dev texinfo musl-dev-armhf \
	make \
	perl sed installkernel bash gmp-dev bc linux-headers xz

# download kernel
RUN wget --quiet https://github.com/Evervolv/android_kernel_htc_qsd8k/archive/95bdcb7cb84d97f5ff0049a4cb7a209fdf30d287.tar.gz -O /kernel.tar.gz
RUN tar xf /kernel.tar.gz -C /

RUN apk add --no-cache mpc1-dev g++ zlib-dev

# download gcc
ENV gccver=4.8.0
RUN wget --quiet https://gcc.gnu.org/pub/gcc/releases/gcc-$gccver/gcc-$gccver.tar.bz2 -P /
RUN tar xf /gcc-$gccver.tar.bz2 -C /

# patch gcc
WORKDIR /gcc-$gccver
#ADD gcc/*.patch ./
#RUN for f in *.patch; do patch -p1 < $f; done

# build gcc
RUN env \
	CFLAGS="-fgnu89-inline" CXXFLAGS="-fgnu89-inline" \
        ./configure --prefix=/usr \
                --mandir=/usr/share/man \
                --infodir=/usr/share/info \
                --build="x86_64-linux-gnu" \
                --host="x86_64-linux-gnu" \
                --target=armv6-alpine-linux-muslgnueabihf \
                --with-arch=armv6zk --with-tune=arm1176jzf-s --with-fpu=vfp --with-float=soft --with-abi=aapcs-linux \
                --disable-altivec \
                --disable-checking \
                --disable-fixed-point \
                --disable-libssp \
                --disable-libstdcxx-pch \
                --disable-multilib \
                --disable-nls \
                --disable-werror \
                --enable-__cxa_atexit \
                --enable-cld \
                --enable-espf \
                --enable-languages=c \
                --enable-shared \
                --enable-target-optspace \
                --disable-tls \
                --disable-threads \
                --with-dynamic-linker= \
                --with-dynamic-linker-prefix=/lib \
                --with-system-zlib \
                --without-system-libunwind \
                --disable-libmudflap \
                --disable-libgomp \
				--disable-libgcc \
				--disable-libatomic \
				--disable-libquadmath \
				--program-prefix=armv6-alpine-linux-muslgnueabihf-$gccver-

# buggy/old texinfo code workaround - don't build docs
RUN echo MAKEINFO:= >> Makefile

RUN make -j8 && make install

# patch kernel
WORKDIR /android_kernel_htc_qsd8k-95bdcb7cb84d97f5ff0049a4cb7a209fdf30d287
ADD kernel/*.patch ./
RUN for f in *.patch; do patch -p1 < $f; done

# build kernel
ADD config-htc-passion.armhf ./.config
RUN yes "" | make ARCH=arm oldconfig
RUN make ARCH=arm CROSS_COMPILE=armv6-alpine-linux-muslgnueabihf- CC=armv6-alpine-linux-muslgnueabihf-$gccver-gcc KBUILD_BUILD_VERSION=gcc$gccver -j16
