# .spec file to package QuickNX in RPM.
# Author: Alexander Todorov <alexx.todorov@no_spam.gmail.com>

%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%global nx_homedir /home/.nxhome

Summary: An Open Source NX server
Name: quicknx
Version: 0.1
Release: 1%{?dist}
Source: %{name}-%{version}.tar.gz
License: GPLv2
Group: User Interface/X
URL: http://quicknx.com

BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildArch: %{_arch}

BuildRequires: autoconf
BuildRequires: automake
BuildRequires: gcc
BuildRequires: make
BuildRequires: python-devel
BuildRequires: python-docutils

Requires: nc
Requires: nx
Requires: openssh
#FIXME
Requires: pygobject2 >= 2.14
Requires: pygtk2 >= 2.10
Requires: python >= 3.2
Requires: python-simplejson
Requires: xauth
Requires: xorg-x11-fonts-misc
Requires: xorg-x11-xkb-utils
Requires: xrdb
Requires: xterm
Requires(pre): shadow-utils
Requires(post): %__install

%description
QuickNX is an updated fork of Neatx, An Open Source NX server, similar to the commercial NX server from 
NoMachine.

%prep
%setup -cq

%build
# fixup paths
sed -ri 's@^(XSESSION\s+=).*@\1 "/etc/X11/xinit/Xsession"@' lib/constants.py
sed -ri 's@^(NETCAT\s+=).*@\1 "/usr/bin/nc"@' lib/constants.py
sed -ri 's@^(#xsession-path\s+=).*@\1 /etc/X11/xinit/Xsession@' doc/quicknx.conf.example
sed -ri 's@^(#netcat-path\s+=).*@\1 /usr/bin/nc@' doc/quicknx.conf.example
./autogen.sh
%configure
make

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install
# provide a meaningfull config file
%__install -D -m 644 %{buildroot}/%_docdir/%{name}/quicknx.conf.example %{buildroot}/etc/quicknx.conf
%__install -D -m 755 extras/rpm/quicknx.initscript %{buildroot}/etc/init.d/quicknx

%clean
rm -rf %{buildroot}

%pre
# create the nx user account
getent group nx >/dev/null || groupadd -r nx
getent passwd nx >/dev/null || \
       useradd -r -g nx -m -d %nx_homedir -s %_libdir/%{name}/nxserver-login-wrapper \
      -c "System account for the %{name} package" nx
chown -R nx: %nx_homedir
exit 0

%post
if [ $1 -eq 1 ]; then
    # install authorized keys
    %__install -d -m 700 -o nx -g nx %nx_homedir/.ssh/
    %__install -D -m 600 -o nx -g nx %_datadir/%{name}/authorized_keys.nomachine %nx_homedir/.ssh/authorized_keys
fi
/sbin/chkconfig --add quicknx
/sbin/service quicknx start > /dev/null 2>&1

%files
%defattr(-,root,root)
%config(noreplace) /etc/quicknx.conf
/etc/init.d/quicknx
%_libdir/%{name}
%python_sitelib/%{name}/*
%doc %_docdir/%{name}
%_datadir/%{name}
%_var/lib/%{name}

# not sure how to handle these. rpmlint doesn't report errors on -debuginfo package
#/usr/lib/debug/.build-id/bb/3398f400d7a44a6e0b8842c051dc378215bae8
#/usr/lib/debug/.build-id/bb/3398f400d7a44a6e0b8842c051dc378215bae8.debug
#/usr/lib/debug/usr/local/lib/quicknx/fdcopy.debug
#/usr/src/debug/quicknx/src/fdcopy.c


%changelog

* Tue Aug 1 2009 Alexander Todorov <alexx.todorov@NO_SPAM.gmail.com>  - 0.1-1
- initial version of spec file
