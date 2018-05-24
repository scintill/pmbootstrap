FROM gliderlabs/alpine:2.6

RUN apk update

RUN apk add \
	openssl ca-certificates curl \
	gcc binutils \
	bison flex gmp-dev mpfr-dev texinfo \
	make \
	perl sed installkernel bash gmp-dev bc linux-headers xz \
	mpc1-dev g++ zlib-dev

# download kernel
RUN curl -s -S -L https://github.com/Evervolv/android_kernel_htc_qsd8k/archive/95bdcb7cb84d97f5ff0049a4cb7a209fdf30d287.tar.gz -o /kernel.tar.gz
RUN tar xzf /kernel.tar.gz -C /

# build binutils
WORKDIR /
RUN curl -s -S -L http://ftp.gnu.org/gnu/binutils/binutils-2.23.2.tar.bz2 -O
RUN tar xjf /binutils-2.23.2.tar.bz2
WORKDIR /binutils-2.23.2
RUN ./configure --prefix=/usr \
		--mandir /usr/share/man \
		--build="x86_64-linux-gnu" \
		--host="x86_64-linux-gnu" \
		--target=armv6-alpine-linux-gnueabihf \
		--infodir /usr/share/info \
		--disable-multilib \
		--enable-shared \
		--enable-64-bit-bfd \
		--disable-werror \
		--disable-nls \
		--program-prefix=armv6-alpine-linux-gnueabihf-built-

RUN make -j8 && make install

# build gcc
ADD gcc/src /gcc
WORKDIR /gcc
RUN contrib/gcc_update --touch
RUN env \
        ./configure --prefix=/usr \
                --mandir=/usr/share/man \
                --infodir=/usr/share/info \
                --build="x86_64-linux-gnu" \
                --host="x86_64-linux-gnu" \
                --target=armv6-alpine-linux-gnueabihf \
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
				--program-prefix=armv6-alpine-linux-gnueabihf-built-

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
RUN bash -c 'make ARCH=arm CROSS_COMPILE=armv6-alpine-linux-gnueabihf-built- KBUILD_BUILD_VERSION=gcc-$(</gcc/.git/HEAD) -j16'
