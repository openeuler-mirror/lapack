%global debug_package %{nil}
%global shortver	3
%global mediumver	%{shortver}.9


Name:		lapack
Version:	%{mediumver}.0
Release:	2
Summary:	The LAPACK libraries for numerical linear algebra.
License:	BSD
URL:		http://www.netlib.org/lapack/
Source0:	https://github.com/Reference-LAPACK/lapack/archive/v%{version}.tar.gz
Source1:	http://www.netlib.org/lapack/manpages.tgz

BuildRequires:	git gcc-gfortran
Provides:	blas = %{version}-%{release}
Obsoletes:	blas < %{version}-%{release}

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
Obsoletes:	%{name}-static < %{version}-%{release}
Provides:	blas-devel = %{version}-%{release}
Obsoletes:	blas-devel < %{version}-%{release}
Provides:	blas-static = %{version}-%{release}
Obsoletes:	blas-static < %{version}-%{release}

%description devel
LAPACK development libraries (shared).

%package        help
Summary:        Help manual for %{name}

%description    help
The %{name}-help package conatins man manual etc


%prep
%autosetup -a 0 -a 1 -p1 -Sgit

cp -f make.inc.example make.inc
sed -i "s|librefblas.a|libblas.a|g" make.inc
sed -i '36iCFLAGS+= -fstack-protector-strong -fPIC' LAPACKE/utils/Makefile
sed -i '40iCFLAGS+= -fstack-protector-strong -fPIC' LAPACKE/src/Makefile

%build
RPM_OPT_FLAGS="$RPM_OPT_FLAGS -frecursive"
RPM_OPT_O_FLAGS=$(echo $RPM_OPT_FLAGS | sed 's|-O2|-O0|')
export FC=gfortran

# make method
# param1: model name
# param2: lib name
# param3: path
lapack_make()
{
    %make_build cleanlib
    %make_build $1 \
      FFLAGS="%{optflags} -fPIC" \
      FFLAGS_NOOPT="%{optflags} -O0 -fPIC"
    mv $3$2.a $2_pic.a
    cp $2_pic.a tmp
    mkdir shared
    cd shared
    ar x ../$2_pic.a
    cd ..
    gfortran -shared -Wl,-z,now,-soname=$2.so.3 -o $2.so.%{version} shared/*.o
    ln -s $2.so.%{version} $2.so
    rm -rf shared
    %make_build cleanlib
    %make_build  $1 \
      FFLAGS="%{optflags}" \
      FFLAGS_NOOPT="%{optflags} -O0"
}


mkdir tmp
#build blas
lapack_make blaslib libblas
mv libblas.a BLAS/
lapack_make lapacklib liblapack

cd LAPACKE
lapack_make lapacke liblapacke ../
mv ../liblapacke.a liblapacke.a
cd ..
mv LAPACKE/liblapacke* ./
mv BLAS/libblas.a ./

%install
mkdir -p ${RPM_BUILD_ROOT}%{_libdir}
mkdir -p ${RPM_BUILD_ROOT}%{_mandir}/man3
chmod 755 ${RPM_BUILD_ROOT}%{_mandir}/man3

for f in liblapack.so.%{version} libblas.so.%{version} liblapacke.so.%{version} libblas.a liblapack.a liblapacke.a; do
  cp -f $f ${RPM_BUILD_ROOT}%{_libdir}/$f
done
cp -f tmp/liblapack_pic.a ${RPM_BUILD_ROOT}%{_libdir}/liblapack_pic.a
rm -rf tmp


# remove weird man pages
pushd man/man3
rm -rf _Users_julie*
popd

find man/man3 -type f -printf "%{_mandir}/man3/%f*\n" > manfiles
cp -f man/man3/* ${RPM_BUILD_ROOT}%{_mandir}/man3

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
ln -sf liblapacke.so.%{version} liblapacke.so
ln -sf liblapacke.so.%{version} liblapacke.so.%{shortver}
ln -sf liblapacke.so.%{version} liblapacke.so.%{mediumver}

popd

# pkgconfig
mkdir -p %{buildroot}%{_libdir}/pkgconfig/
cp -a lapack.pc.in %{buildroot}%{_libdir}/pkgconfig/lapack.pc
sed -i 's|@CMAKE_INSTALL_FULL_LIBDIR@|%{_libdir}|g' %{buildroot}%{_libdir}/pkgconfig/lapack.pc
sed -i 's|@CMAKE_INSTALL_FULL_INCLUDEDIR@|%{_includedir}|g' %{buildroot}%{_libdir}/pkgconfig/lapack.pc
sed -i 's|@LAPACK_VERSION@|%{version}|g' %{buildroot}%{_libdir}/pkgconfig/lapack.pc


cp -a BLAS/blas.pc.in %{buildroot}%{_libdir}/pkgconfig/blas.pc
sed -i 's|@CMAKE_INSTALL_FULL_LIBDIR@|%{_libdir}|g' %{buildroot}%{_libdir}/pkgconfig/blas.pc
sed -i 's|@CMAKE_INSTALL_FULL_INCLUDEDIR@|%{_includedir}|g' %{buildroot}%{_libdir}/pkgconfig/blas.pc
sed -i 's|@LAPACK_VERSION@|%{version}|g' %{buildroot}%{_libdir}/pkgconfig/blas.pc


cp -a LAPACKE/lapacke.pc.in %{buildroot}%{_libdir}/pkgconfig/lapacke.pc
sed -i 's|@CMAKE_INSTALL_FULL_LIBDIR@|%{_libdir}|g' %{buildroot}%{_libdir}/pkgconfig/lapacke.pc
sed -i 's|@CMAKE_INSTALL_FULL_INCLUDEDIR@|%{_includedir}/lapacke|g' %{buildroot}%{_libdir}/pkgconfig/lapacke.pc
sed -i 's|@LAPACK_VERSION@|%{version}|g' %{buildroot}%{_libdir}/pkgconfig/lapacke.pc

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig


%files
%license LICENSE
%{_libdir}/liblapack.so.*
%{_libdir}/liblapacke.so.*
%{_libdir}/libblas.so.*

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
%{_libdir}/libblas.so
%{_libdir}/pkgconfig/blas.pc
%{_libdir}/libblas.a

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
%{_libdir}/pkgconfig/blas64.pc
%{_libdir}/libblas64_.a
%endif

%changelog
* Tue Sep 15 2020 liuweibo <liuweibo10@huawei.com> - 3.9.0-2
- Fix Source0

* Sat Aug 08 2020 xinghe <xinghe1@huawei.com> - 3.9.0-1
- update verion to 3.9.0

* Fri Apr 03 2020 Jiangping Hu <hujp1985@foxmail.com> - 3.8.0-17
- Fix method annotations of lapack_make

* Thu Mar 19 2020 gulining1 <gulining1@huawei.com> - 3.8.0-16
- add build option to fix selfbuild error

* Thu Mar 19 2020 gulining1 <gulining1@huawei.com> - 3.8.0-15
- Add version for obsoletes packages

* Wed Mar 18 2020 zhujunhao <zhujunhao5@huawei.com> - 3.8.0-14
- Add safe compilation options

* Thu Feb 13 2020 likexin <likexin4@huawei.com> - 3.8.0-13
- Add liblapack_pic.a

* Mon Jan 20 2020 openEuler Buildteam <buildteam@openeuler.org> - 3.8.0-12
- Optimize spec

* Thu Nov 14 2019 openEuler Buildteam <buildteam@openeuler.org> - 3.8.0-11
- Package init
