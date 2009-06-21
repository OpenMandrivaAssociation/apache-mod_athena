#Module-Specific definitions
%define apache_version 2.2.8
%define mod_name mod_athena
%define mod_conf B33_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	Full-featured reverse-proxying and/or stand-alone load balancer
Name:		apache-%{mod_name}
Version:	2.2.4
Release:	%mkrel 1
Group:		System/Servers
License:	Apache License
URL:		http://code.google.com/p/ath/
Source0:	http://ath.googlecode.com/files/ath-%{version}.tgz
Source1:	%{mod_conf}
Patch0:		ath-mod_name_fix.diff
Patch1:		ath-perl_vendor.diff
Patch2:		ath-perl_build_fix.diff
Patch3:		ath-perl_provides_fix.diff
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):  apache-conf >= %{apache_version}
Requires(pre):  apache >= %{apache_version}
Requires:	apache-conf >= %{apache_version}
Requires:	apache >= %{apache_version}
BuildRequires:  apache-devel >= %{apache_version}
BuildRequires:  perl-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
This module is designed to allow httpd to act as a load balancer, either
internally to apache's own mod_proxy (for reverse proxying), or externally to
machines querying it. Arbitrary statistics are sent to the engine via a simple
GET plus query-string interface, from which it will then make decisions based
on chosen algorithms. You are able to manage farms of servers, mark them in
different states, and forward disabled or down systems or farms to new targets,
among other administrative features. In version 2.x (requires httpd-2.2.x), you
can manipulate loadbalancing decisions with your back-end application by
setting a secret key secured cookie that the load balancer will intercept and
use to modify the algorithm. This feature allows you to maintain stick sessions
to a specific server, or prioritize farms using business rules (QoS).

%package -n	perl-Athena
Summary:	Interface to Athena
Group:		Development/Perl
License:	GPL or Artistic

%description -n	perl-Athena
Interface to Athena.

%prep

%setup -q -n ath-%{version}
%patch0 -p0
%patch1 -p0
%patch2 -p0
%patch3 -p1

cp %{SOURCE1} %{mod_conf}

%build
rm -rf autom4*cache
libtoolize --copy --force; aclocal-1.7; automake-1.7 --add-missing --copy --foreign; autoheader; autoconf

export CPPFLAGS="`apr-1-config --cppflags` `apr-1-config --includes` -I`%{_sbindir}/apxs -q INCLUDEDIR`"

%configure2_5x --localstatedir=/var/lib \
    --with-apache2=%{_prefix} \
    --with-cgi-bin=/var/www/cgi-bin \
    INSTALLDIRS=vendor

# hack...
perl -pi -e "s|/usr/local/bin|%{_bindir}|g" src/perl/package/Athena/Makefile
perl -pi -e "s|/usr/local/share/man/man3|%{_mandir}/man3|g" src/perl/package/Athena/Makefile

%make

# fix docs
make -C doc ATH_DOC_DIR=../mod_athena_doc install
find mod_athena_doc -type f -exec chmod 644 {} \;

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

install -m0755 src/c/module/.libs/%{mod_so} %{buildroot}%{_libdir}/apache-extramodules/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

%makeinstall_std -C src/perl/package/Athena

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
        %{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc AUTHORS COPYING ChangeLog LICENSE.TXT mod_athena_doc/*
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}

%files -n perl-Athena
%defattr(-,root,root)
%dir %{perl_vendorarch}/Athena
%dir %{perl_vendorarch}/Athena/Engine
%dir %{perl_vendorarch}/Athena/WebAPI
%{perl_vendorarch}/Athena.pm
%{perl_vendorarch}/athena.pl
%{perl_vendorarch}/Athena/*.pm
%{perl_vendorarch}/Athena/Engine/*.pm
%{perl_vendorarch}/Athena/WebAPI/*.pm
%dir %{perl_vendorarch}/auto/Athena
%{perl_vendorarch}/auto/Athena/Athena.so
%{perl_vendorarch}/auto/Athena/autosplit.ix
%{_bindir}/athena.pl
%{_mandir}/man3/Athena.3pm*
