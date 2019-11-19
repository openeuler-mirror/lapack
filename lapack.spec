%global debug_package %{nil}
%global shortver	3
%global mediumver	%{shortver}.8

%if %{?__isa_bits:%{__isa_bits}}%{!?__isa_bits:32} == 64
%global arch64 1
%else
%global arch64 0
%endif

Name:		lapack
Version:	%{mediumver}.0
Release:	11
Summary:	The LAPACK libraries for numerical linear algebra.
License:	BSD
URL:		http://www.netlib.org/lapack/
Source0:	http://www.netlib.org/lapack/%{name}-%{version}.tar.gz
Source1:	http://www.netlib.org/lapack/manpages.tgz
Source2:	http://www.netlib.org/lapack/lapackqref.ps
Source3:	http://www.netlib.org/blas/blasqr.ps
# These Makefiles are from fedora: https://src.fedoraproject.org/rpms/lapack/tree/f29
Source4:	Makefile.blas
Source5:	Makefile.lapack
Source6:	Makefile.cblas

# These patches are from fedora: https://src.fedoraproject.org/rpms/lapack/tree/f29
# These patches are used for modifying Makefile, we use fedora's Makefile, so we also keep these patches
Patch1: lapack-3.7.1-make.inc.patch
Patch2: lapack-3.7.1-lapacke-shared.patch
Patch3: lapack-3.7.1-lapacke-tmglib.patch
Patch4: lapack-3.8.0-missing-aawork.patch

BuildRequires:	git gcc-gfortran
Provides:	blas = %{version}-%{release}
Obsoletes:	blas

%global _description\
LAPACK (Linear Algebra PACKage) is a standard library for numerical\
linear algebra. LAPACK provides routines for solving systems of\
simultaneous linear equations, least-squares solutions of linear\
systems of equations, eigenvalue problems, and singular value\
problems. Associated matrix factorizations (LU, Cholesky, QR, SVD,\
Schur, and generalized Schur) and related computations (i.e.,\
reordering of Schur factorizations and estimating condition numbers)\
are also included. LAPACK can handle dense and banded matrices, but\
not general sparse matrices. Similar functionality is provided for\
real and complex matrices in both single and double precision. LAPACK\
is coded in Fortran90 and built with gcc.\

%description %_description

%package devel
Summary:	LAPACK development libraries
Requires:	%{name} = %{version}-%{release}
Provides:	%{name}-static = %{version}-%{release}
Obsoletes:	%{name}-static
Provides:	blas-devel = %{version}-%{release}
Obsoletes:	blas-devel
Provides:	blas-static = %{version}-%{release}
Obsoletes:	blas-static

%description devel
LAPACK development libraries (shared).

%package        help
Summary:        Help manual for %{name}

%description    help
The %{name}-help package conatins man manual etc

%if 0%{?arch64}
%package -n lapack64
Summary: Numerical linear algebra package libraries
Provides:	blas64
Obsoletes:	blas64

%description -n lapack64
%_description
This build has 64bit INTEGER support.\

%package -n lapack64-devel
Summary:	LAPACK development libraries (64bit INTEGER)
Requires:	%{name}64 = %{version}-%{release}
Requires:	%{name}-devel = %{version}-%{release}
Provides:	%{name}64-static = %{version}-%{release}
Obsoletes:	%{name}64-static
Provides:	blas64-devel = %{version}-%{release}
Obsoletes:	blas64-devel
Provides:	blas64-static = %{version}-%{release}
Obsoletes:	blas64-static

%description -n lapack64-devel
LAPACK development libraries (shared, 64bit INTEGER).
%endif

%prep
%autosetup -a 0 -a 1 -p1 -Sgit

cp -f INSTALL/make.inc.gfortran make.inc
cp -f %{SOURCE4} BLAS/SRC/Makefile
cp -f %{SOURCE5} SRC/Makefile
cp -f %{SOURCE6} CBLAS/src/Makefile

# Replace with a specific version number
sed -i "s|@SHORTVER@|%{shortver}|g" BLAS/SRC/Makefile
sed -i "s|@SHORTVER@|%{shortver}|g" SRC/Makefile
sed -i "s|@SHORTVER@|%{shortver}|g" LAPACKE/Makefile
sed -i "s|@SHORTVER@|%{shortver}|g" CBLAS/src/Makefile
sed -i "s|@LONGVER@|%{version}|g" BLAS/SRC/Makefile
sed -i "s|@LONGVER@|%{version}|g" SRC/Makefile
sed -i "s|@LONGVER@|%{version}|g" LAPACKE/Makefile
sed -i "s|@LONGVER@|%{version}|g" CBLAS/src/Makefile

%build
RPM_OPT_FLAGS="$RPM_OPT_FLAGS -frecursive"
RPM_OPT_O_FLAGS=$(echo $RPM_OPT_FLAGS | sed 's|-O2|-O0|')
export FC=gfortran

# These Makefiles are from fedora, so we follow fedora's build method
# param1: BUILD dir
# param2: whether to specify the include directory
# param3: lib name
# param4: object name
build() {
	pushd $1
	pwd
	if [ $# -eq 4 ]; then
		FFLAGS="$RPM_OPT_O_FLAGS" make $4.o
	fi
	if [ $2 -eq 1 ]; then
		FFLAGS="$RPM_OPT_FLAGS" CFLAGS="$RPM_OPT_FLAGS -I../include" make static
	else
		FFLAGS="$RPM_OPT_FLAGS" CFLAGS="$RPM_OPT_FLAGS" make static
	fi
	cp $3.a ${RPM_BUILD_DIR}/%{name}-%{version}/
	make clean

	if [ $# -eq 4 ]; then
		FFLAGS="$RPM_OPT_O_FLAGS -fPIC" make $4.o
	fi
	if [ $2 -eq 1 ]; then
		FFLAGS="$RPM_OPT_FLAGS -fPIC" CFLAGS="$RPM_OPT_FLAGS -fPIC -I../include" LDFLAGS="%{build_ldflags}" make shared
	else
		FFLAGS="$RPM_OPT_FLAGS -fPIC" CFLAGS="$RPM_OPT_FLAGS -fPIC" LDFLAGS="%{build_ldflags}" make shared
	fi
	cp $3.so.%{version} ${RPM_BUILD_DIR}/%{name}-%{version}/

	%if 0%{?arch64}
		make clean
		if [ $# -eq 4 ]; then
			FFLAGS="$RPM_OPT_O_FLAGS -fdefault-integer-8" make $4.o
		fi
		if [ $2 -eq 1 ]; then
			SYMBOLPREFIX="64_" FFLAGS="$RPM_OPT_FLAGS -fdefault-integer-8" CFLAGS="$RPM_OPT_FLAGS -I../include" make static
		else
			SYMBOLPREFIX="64_" FFLAGS="$RPM_OPT_FLAGS -fdefault-integer-8" CFLAGS="$RPM_OPT_FLAGS" make static
		fi
		cp $364_.a ${RPM_BUILD_DIR}/%{name}-%{version}/$364_.a
		make clean
		if [ $# -eq 4 ]; then
			FFLAGS="$RPM_OPT_O_FLAGS -fPIC -fdefault-integer-8" make $4.o
		fi
		if [ $2 -eq 1 ]; then
			SYMBOLPREFIX="64_" FFLAGS="$RPM_OPT_FLAGS -fPIC -fdefault-integer-8" CFLAGS="$RPM_OPT_FLAGS -fPIC -I../include" LDFLAGS="%{build_ldflags}" make shared
		else
			SYMBOLPREFIX="64_" FFLAGS="$RPM_OPT_FLAGS -fPIC -fdefault-integer-8" CFLAGS="$RPM_OPT_FLAGS -fPIC" LDFLAGS="%{build_ldflags}" make shared
		fi
		cp $364_.so.%{version} ${RPM_BUILD_DIR}/%{name}-%{version}/$364_.so.%{version}
	%endif
	popd

	ln -s $3.so.%{version} $3.so
	%if 0%{?arch64}
		ln -s $364_.so.%{version} $364_.so
    %endif
}

# Build BLAS
build "BLAS/SRC" 0 "libblas" "dcabs1"

# Build CBLAS
cp CBLAS/include/cblas_mangling_with_flags.h.in CBLAS/include/cblas_mangling.h
build "CBLAS/src" 1 "libcblas"

# Build the static dlamch, dsecnd, lsame, second, slamch bits
pushd INSTALL
make NOOPT="$RPM_OPT_O_FLAGS" OPTS="$RPM_OPT_FLAGS"
popd

# Build the static lapack library
pushd SRC
make FFLAGS="$RPM_OPT_FLAGS" CFLAGS="$RPM_OPT_FLAGS" static
cp liblapack.a ${RPM_BUILD_DIR}/%{name}-%{version}/
popd

# Build the static with pic dlamch, dsecnd, lsame, second, slamch bits
pushd INSTALL
make clean
make NOOPT="$RPM_OPT_O_FLAGS -fPIC" OPTS="$RPM_OPT_FLAGS -fPIC"
popd

# Build the static with pic lapack library
pushd SRC
make clean
make FFLAGS="$RPM_OPT_FLAGS -fPIC" CFLAGS="$RPM_OPT_FLAGS -fPIC" static
cp liblapack.a ${RPM_BUILD_DIR}/%{name}-%{version}/liblapack_pic.a
popd

%if 0%{?arch64}
# Build the static dlamch, dsecnd, lsame, second, slamch bits
pushd INSTALL
make NOOPT="$RPM_OPT_O_FLAGS -fdefault-integer-8" OPTS="$RPM_OPT_FLAGS -fdefault-integer-8"
popd

# Build the static lapack library
pushd SRC
make SYMBOLPREFIX="64_" FFLAGS="$RPM_OPT_FLAGS -fdefault-integer-8" CFLAGS="$RPM_OPT_FLAGS" static
cp liblapack64_.a ${RPM_BUILD_DIR}/%{name}-%{version}/liblapack64_.a
popd

# Build the static with pic dlamch, dsecnd, lsame, second, slamch bits (64bit INTEGER)
pushd INSTALL
make clean
make NOOPT="$RPM_OPT_O_FLAGS -fPIC -fdefault-integer-8" OPTS="$RPM_OPT_FLAGS -fPIC -fdefault-integer-8"
popd

# Build the static with pic lapack library (64bit INTEGER)
pushd SRC
make clean
make SYMBOLPREFIX="64_" FFLAGS="$RPM_OPT_FLAGS -fPIC -fdefault-integer-8" CFLAGS="$RPM_OPT_FLAGS -fPIC" static
cp liblapack64_.a ${RPM_BUILD_DIR}/%{name}-%{version}/liblapack64_pic.a
popd
%endif

# Build the shared dlamch, dsecnd, lsame, second, slamch bits
pushd INSTALL
make clean
make NOOPT="$RPM_OPT_O_FLAGS -fPIC" OPTS="$RPM_OPT_FLAGS -fPIC"
popd

# Build the shared lapack library
pushd SRC
make clean
make FFLAGS="$RPM_OPT_FLAGS -fPIC" CFLAGS="$RPM_OPT_FLAGS -fPIC" LDFLAGS="%{build_ldflags}" shared
cp liblapack.so.%{version} ${RPM_BUILD_DIR}/%{name}-%{version}/
popd

%if 0%{?arch64}
# Build the shared dlamch, dsecnd, lsame, second, slamch bits
pushd INSTALL
make clean
make NOOPT="$RPM_OPT_O_FLAGS -fPIC -fdefault-integer-8" OPTS="$RPM_OPT_FLAGS -fPIC -fdefault-integer-8"
popd

# Build the shared lapack library
pushd SRC
make clean
make SYMBOLPREFIX="64_" FFLAGS="$RPM_OPT_FLAGS -fPIC -fdefault-integer-8" CFLAGS="$RPM_OPT_FLAGS -fPIC -fdefault-integer-8" LDFLAGS="%{build_ldflags}" shared
cp liblapack64_.so.%{version} ${RPM_BUILD_DIR}/%{name}-%{version}/liblapack64_.so.%{version}
popd
%endif

ln -s liblapack.so.%{version} liblapack.so

%if 0%{?arch64}
ln -s liblapack64_.so.%{version} liblapack64_.so
%endif

# Build the lapacke libraries
make OPTS="$RPM_OPT_FLAGS -fPIC" NOOPT="$RPM_OPT_O_FLAGS -fPIC" tmglib
pushd LAPACKE
make clean
make CFLAGS="$RPM_OPT_FLAGS" BUILD_DEPRECATED="true" lapacke
make clean
make CFLAGS="$RPM_OPT_FLAGS -fPIC" BUILD_DEPRECATED="true" LDFLAGS="%{build_ldflags}" shlib
cp liblapacke.so.%{version} ${RPM_BUILD_DIR}/%{name}-%{version}/
popd

cp -p %{SOURCE2} lapackqref.ps
cp -p %{SOURCE3} blasqr.ps

%install
mkdir -p ${RPM_BUILD_ROOT}%{_libdir}
mkdir -p ${RPM_BUILD_ROOT}%{_mandir}/man3
chmod 755 ${RPM_BUILD_ROOT}%{_mandir}/man3

for f in liblapack.so.%{version} libblas.so.%{version} libcblas.so.%{version} liblapacke.so.%{version} libblas.a libcblas.a liblapack.a liblapack_pic.a liblapacke.a; do
  cp -f $f ${RPM_BUILD_ROOT}%{_libdir}/$f
done

%if 0%{?arch64}
for f in liblapack64_.so.%{version} libblas64_.so.%{version} libcblas64_.so.%{version} libblas64_.a libcblas64_.a liblapack64_.a liblapack64_pic.a; do
  cp -f $f ${RPM_BUILD_ROOT}%{_libdir}/$f
done
%endif

# remove weird man pages
pushd man/man3
rm -rf _Users_julie*
popd

find man/man3 -type f -printf "%{_mandir}/man3/%f*\n" > manfiles
cp -f man/man3/* ${RPM_BUILD_ROOT}%{_mandir}/man3

# Cblas headers
mkdir -p %{buildroot}%{_includedir}/cblas/
cp -a CBLAS/include/*.h %{buildroot}%{_includedir}/cblas/

# Lapacke headers
mkdir -p %{buildroot}%{_includedir}/lapacke/
cp -a LAPACKE/include/*.h %{buildroot}%{_includedir}/lapacke/

pushd ${RPM_BUILD_ROOT}%{_libdir}
ln -sf liblapack.so.%{version} liblapack.so
ln -sf liblapack.so.%{version} liblapack.so.%{shortver}
ln -sf liblapack.so.%{version} liblapack.so.%{mediumver}
ln -sf libblas.so.%{version} libblas.so
ln -sf libblas.so.%{version} libblas.so.%{shortver}
ln -sf libblas.so.%{version} libblas.so.%{mediumver}
ln -sf libcblas.so.%{version} libcblas.so
ln -sf libcblas.so.%{version} libcblas.so.%{shortver}
ln -sf libcblas.so.%{version} libcblas.so.%{mediumver}
ln -sf liblapacke.so.%{version} liblapacke.so
ln -sf liblapacke.so.%{version} liblapacke.so.%{shortver}
ln -sf liblapacke.so.%{version} liblapacke.so.%{mediumver}
%if 0%{?arch64}
ln -sf liblapack64_.so.%{version} liblapack64_.so
ln -sf liblapack64_.so.%{version} liblapack64_.so.%{shortver}
ln -sf liblapack64_.so.%{version} liblapack64_.so.%{mediumver}
ln -sf libblas64_.so.%{version} libblas64_.so
ln -sf libblas64_.so.%{version} libblas64_.so.%{shortver}
ln -sf libblas64_.so.%{version} libblas64_.so.%{mediumver}
ln -sf libcblas64_.so.%{version} libcblas64_.so
ln -sf libcblas64_.so.%{version} libcblas64_.so.%{shortver}
ln -sf libcblas64_.so.%{version} libcblas64_.so.%{mediumver}
%endif
popd

# pkgconfig
mkdir -p %{buildroot}%{_libdir}/pkgconfig/
cp -a lapack.pc.in %{buildroot}%{_libdir}/pkgconfig/lapack.pc
sed -i 's|@CMAKE_INSTALL_FULL_LIBDIR@|%{_libdir}|g' %{buildroot}%{_libdir}/pkgconfig/lapack.pc
sed -i 's|@CMAKE_INSTALL_FULL_INCLUDEDIR@|%{_includedir}|g' %{buildroot}%{_libdir}/pkgconfig/lapack.pc
sed -i 's|@LAPACK_VERSION@|%{version}|g' %{buildroot}%{_libdir}/pkgconfig/lapack.pc
%if 0%{?arch64}
cp -a %{buildroot}%{_libdir}/pkgconfig/lapack.pc %{buildroot}%{_libdir}/pkgconfig/lapack64.pc
sed -i 's|-llapack|-llapack64_|g' %{buildroot}%{_libdir}/pkgconfig/lapack64.pc
sed -i 's|blas|blas64|g' %{buildroot}%{_libdir}/pkgconfig/lapack64.pc
%endif
cp -a BLAS/blas.pc.in %{buildroot}%{_libdir}/pkgconfig/blas.pc
sed -i 's|@CMAKE_INSTALL_FULL_LIBDIR@|%{_libdir}|g' %{buildroot}%{_libdir}/pkgconfig/blas.pc
sed -i 's|@CMAKE_INSTALL_FULL_INCLUDEDIR@|%{_includedir}|g' %{buildroot}%{_libdir}/pkgconfig/blas.pc
sed -i 's|@LAPACK_VERSION@|%{version}|g' %{buildroot}%{_libdir}/pkgconfig/blas.pc
%if 0%{?arch64}
cp -a %{buildroot}%{_libdir}/pkgconfig/blas.pc %{buildroot}%{_libdir}/pkgconfig/blas64.pc
sed -i 's|-lblas|-lblas64_|g' %{buildroot}%{_libdir}/pkgconfig/blas64.pc
%endif
cp -a LAPACKE/lapacke.pc.in %{buildroot}%{_libdir}/pkgconfig/lapacke.pc
sed -i 's|@CMAKE_INSTALL_FULL_LIBDIR@|%{_libdir}|g' %{buildroot}%{_libdir}/pkgconfig/lapacke.pc
sed -i 's|@CMAKE_INSTALL_FULL_INCLUDEDIR@|%{_includedir}/lapacke|g' %{buildroot}%{_libdir}/pkgconfig/lapacke.pc
sed -i 's|@LAPACK_VERSION@|%{version}|g' %{buildroot}%{_libdir}/pkgconfig/lapacke.pc
cp -a CBLAS/cblas.pc.in %{buildroot}%{_libdir}/pkgconfig/cblas.pc
sed -i 's|@CMAKE_INSTALL_FULL_LIBDIR@|%{_libdir}|g' %{buildroot}%{_libdir}/pkgconfig/cblas.pc
sed -i 's|@CMAKE_INSTALL_FULL_INCLUDEDIR@|%{_includedir}/cblas|g' %{buildroot}%{_libdir}/pkgconfig/cblas.pc
sed -i 's|@LAPACK_VERSION@|%{version}|g' %{buildroot}%{_libdir}/pkgconfig/cblas.pc
%if 0%{?arch64}
cp -a %{buildroot}%{_libdir}/pkgconfig/cblas.pc %{buildroot}%{_libdir}/pkgconfig/cblas64.pc
sed -i 's|-lcblas|-lcblas64_|g' %{buildroot}%{_libdir}/pkgconfig/cblas64.pc
sed -i 's|Requires.private: blas|Requires.private: blas64|g' %{buildroot}%{_libdir}/pkgconfig/cblas64.pc
%endif

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%if 0%{?arch64}
%post -n lapack64 -p /sbin/ldconfig
%postun -n lapack64 -p /sbin/ldconfig
%endif

%files
%doc lapackqref.ps blasqr.ps
%license LICENSE
%{_libdir}/liblapack.so.*
%{_libdir}/liblapacke.so.*
%{_libdir}/libblas.so.*
%{_libdir}/libcblas.so.*

%files help -f manfiles
%doc README.md

%files devel
%{_includedir}/lapacke/
%{_libdir}/liblapack.so
%{_libdir}/liblapacke.so
%{_libdir}/pkgconfig/lapack.pc
%{_libdir}/pkgconfig/lapacke.pc
%{_libdir}/liblapack.a
%{_libdir}/liblapack_pic.a
%{_libdir}/liblapacke.a
%{_includedir}/cblas/
%{_libdir}/libblas.so
%{_libdir}/libcblas.so
%{_libdir}/pkgconfig/blas.pc
%{_libdir}/pkgconfig/cblas.pc
%{_libdir}/libblas.a
%{_libdir}/libcblas.a

%if 0%{?arch64}
%files -n lapack64
%doc README.md
%license LICENSE
%{_libdir}/liblapack64_.so.*
%{_libdir}/libblas64_.so.*
%{_libdir}/libcblas64_.so.*

%files -n lapack64-devel
%{_libdir}/liblapack64_.so
%{_libdir}/pkgconfig/lapack64.pc
%{_libdir}/liblapack64_.a
%{_libdir}/liblapack64_pic.a
%{_libdir}/libblas64_.so
%{_libdir}/libcblas64_.so
%{_libdir}/pkgconfig/blas64.pc
%{_libdir}/pkgconfig/cblas64.pc
%{_libdir}/libblas64_.a
%{_libdir}/libcblas64_.a
%endif

%changelog
* Thu Nov 14 2019 openEuler Buildteam <buildteam@openeuler.org> - 3.8.0-11
- Package init
