# we use the upstream version from http_parser.h as the SONAME
%global somajor 2
%global sominor 7
%global sopoint 1

Name:           http-parser
Version:        %{somajor}.%{sominor}.%{sopoint}
Release:        8%{?dist}
Summary:        HTTP request/response parser for C

License:        MIT
URL:            https://github.com/nodejs/http-parser
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

# https://github.com/nodejs/http-parser/commit/335850f6b868d3411968cbf5a4d59fe619dee36f
Patch0001:      %{name}-0001-parser-HTTP_STATUS_MAP-XX-and-enum-http_status.patch
Patch0002:      CVE-2018-12121-backport.patch
Patch0003:      CVE-2018-7159-reject-interior-blanks-in-Content-Length-backport.patch
Patch0004:      CVE-2018-7159-Fix-Content-Lenght-with-obsolete-line-folding-backport.patch
Patch0005:      CVE-2018-7159-Dissallow-empty-Content-Length.patch
Patch0006:      cve-tests-backport.patch

BuildRequires:  gcc
BuildRequires:  cmake

%description
This is a parser for HTTP messages written in C. It parses both requests and
responses. The parser is designed to be used in performance HTTP applications.
It does not make any syscalls nor allocations, it does not buffer data, it can
be interrupted at anytime. Depending on your architecture, it only requires
about 40 bytes of data per message stream (in a web server that is per
connection).

%package devel
Summary:        Development headers and libraries for http-parser
Requires:       %{name}%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

%description devel
Development headers and libraries for http-parser.

%prep
%autosetup -p1
# TODO: try to send upstream?
cat > CMakeLists.txt << EOF
cmake_minimum_required (VERSION 2.8.5)
project (http-parser C)
include (GNUInstallDirs)

set (SRCS http_parser.c)
set (HDRS http_parser.h)
set (TEST_SRCS test.c)

# Non-Strict version
add_library (http_parser \${SRCS})
target_compile_definitions (http_parser
                            PUBLIC -DHTTP_PARSER_STRICT=0)
add_executable (test-nonstrict \${TEST_SRCS})
target_link_libraries (test-nonstrict http_parser)
# Strict version
add_library (http_parser_strict \${SRCS})
target_compile_definitions (http_parser_strict
                            PUBLIC -DHTTP_PARSER_STRICT=1)
add_executable (test-strict \${TEST_SRCS})
target_link_libraries (test-strict http_parser_strict)

set_target_properties (http_parser http_parser_strict
                       PROPERTIES
                           SOVERSION %{somajor}
                           VERSION %{version})

install (TARGETS http_parser http_parser_strict
         LIBRARY DESTINATION \${CMAKE_INSTALL_LIBDIR})
install (FILES \${HDRS}
         DESTINATION \${CMAKE_INSTALL_INCLUDEDIR})

enable_testing ()
add_test (NAME test-nonstrict COMMAND test-nonstrict)
add_test (NAME test-strict COMMAND test-strict)
EOF

%build
mkdir %{_target_platform}
pushd %{_target_platform}
  %cmake .. -DCMAKE_BUILD_TYPE=RelWithDebInfo
popd
%make_build -C %{_target_platform}

%install
%make_install -C %{_target_platform}

%check
make test -C %{_target_platform}

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%{_libdir}/libhttp_parser.so.*
%{_libdir}/libhttp_parser_strict.so.*
%doc AUTHORS README.md
%license LICENSE-MIT

%files devel
%{_includedir}/http_parser.h
%{_libdir}/libhttp_parser.so
%{_libdir}/libhttp_parser_strict.so

%changelog
* Mon Apr  1 2019 Jakub Hrozek <jhrozek@redhat.com> - 2.7.1-8
- Backport needed test fixes
- Related: rhbz#1666024 - CVE-2018-7159 http-parser: nodejs: HTTP parser
                          allowed for spaces inside Content-Length header
                          values [rhel-7]

* Sat Mar 23 2019 Jakub Hrozek <jhrozek@redhat.com> - 2.7.1-7
- Resolves: rhbz#1666024 - CVE-2018-7159 http-parser: nodejs: HTTP parser
                           allowed for spaces inside Content-Length header
                           values [rhel-7]

* Fri Mar 22 2019 Jakub Hrozek <jhrozek@redhat.com> - 2.7.1-6
- Resolves: rhbz#1666381 - CVE-2018-12121 http-parser: nodejs: Denial of
                           Service with large HTTP headers [rhel-7]

* Thu Aug 10 2017 Fabiano Fidêncio <fidencio@redhat.com> - 2.7.1-5
- Bump http-parser release number to avoid people pulling EPEL package instead
  of RHEL package
  Resolves: rhbz#1479471

* Wed Feb 01 2017 Fabiano Fidêncio <fidencio@redhat.com> - 2.7.1-1
- Import spec file and patches from latest fc25 package
  Resolves: rhbz#1393819
