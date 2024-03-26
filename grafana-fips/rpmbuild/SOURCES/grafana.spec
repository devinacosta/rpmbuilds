#
# spec file for package grafana
# Updated by Devin Acosta
# Parts from: https://src.fedoraproject.org/rpms/grafana/ 
# Parts from: https://build.opensuse.org/package/show/openSUSE:Factory/grafana
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

#

%define currentgoipath github.com/google/wire
%define goworkdir /root/rpmbuild/BUILD/go
%define debug_package %{nil}

%global selinux_variants mls targeted
%global         GRAFANA_USER %{name}
%global         GRAFANA_GROUP %{name}

%if 0%{?rhel}
%define os_suffix .el%{?rhel}
%endif

Name:           grafana
Version:        10.1.5
Release:        1%{?os_suffix}
Summary:        The open-source platform for monitoring and observability
License:        AGPL-3.0-only
Group:          System/Monitoring
URL:            http://grafana.org/
Source:         %{name}-%{version}.tar.gz
Source1:        vendor.tar.gz
Source2:        %{name}-rpmlintrc
# Instructions on the build process
Source3:        README
# Makefile to automate build process
Source4:        Makefile
Source5:        0001-Add-source-code-reference.patch

# Source6 - Source8  contain the grafana-selinux policy
Source6:         grafana.te
Source7:         grafana.fc
Source8:         grafana.if

# Source9 contains the systemd-sysusers configuration
Source9:          grafana.sysusers

BuildRequires:  fdupes
BuildRequires:  git-core
#BuildRequires:  golang-packaging
#BuildRequires:  wire
#BuildRequires:  golang(API) >= 1.20
%systemd_ordering

%description
A graph and dashboard builder for visualizing time series metrics.

Grafana provides ways to create, explore, and share
dashboards and data with teams.

# SELinux package
%package selinux
Summary:        SELinux policy module supporting grafana
BuildRequires: checkpolicy, selinux-policy-devel, selinux-policy-targeted
%if "%{_selinux_policy_version}" != ""
Requires:       selinux-policy >= %{_selinux_policy_version}
%endif
Requires:       %{name} = %{version}-%{release}
Requires:	selinux-policy-targeted
Requires(post):   /usr/sbin/semodule, /usr/sbin/semanage, /sbin/restorecon, /sbin/fixfiles, grafana
Requires(postun): /usr/sbin/semodule, /usr/sbin/semanage, /sbin/restorecon, /sbin/fixfiles, /sbin/service, grafana

%description selinux
SELinux policy module supporting grafana


%prep
%setup -q -n grafana-%{version}
%setup -q -T -D -a 1 -n grafana-%{version}

# SELinux policy
mkdir SELinux
cp -p %{SOURCE6} %{SOURCE7} %{SOURCE8} SELinux

%build
set -x
cd %{_builddir}/grafana-%{version}
# Manual build in order to inject ldflags so grafana correctly displays
# the version in the footer of each page.  Note that we're only injecting
# main.version, not main.commit or main.buildstamp as is done in the upstream
# build.go, because we don't have access to the git commit history here.
# (The %%gobuild macro can't take quoted strings; they get split up when
# expanded to $extra_flags in process_build() in /usr/lib/rpm/golang.sh.)
export IMPORTPATH=%{_builddir}/grafana-%{version}
export BUILDFLAGS="-v -p 4 -x -buildmode=pie -mod=vendor"
export GOPATH=%{_builddir}/go:%{_builddir}/contrib
export GOBIN=/usr/local/go/bin
export GOEXPERIMENT=opensslcrypto
export GOFIPS=1
wire gen -tags 'oss' ./pkg/server ./pkg/cmd/grafana-cli/runner

# see grafana-X.Y.Z/pkg/build/cmd.go
export LDFLAGS="-X main.version=%{version} -X main.buildstamp=${SOURCE_DATE_EPOCH}"
for cmd in grafana grafana-cli grafana-server; do
    %gobuild -o %{_builddir}/bin/${cmd} ./pkg/cmd/${cmd}
done

# SELinux policy
cd SELinux
for selinuxvariant in %{selinux_variants}
do
  make NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile
  mv grafana.pp grafana.pp.${selinuxvariant}
  make NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile clean
done
cd -

%install

# install binaries and service
install -Dm644 {packaging/rpm/systemd/,%{buildroot}%{_unitdir}/}%{name}-server.service
install -dm755 %{buildroot}%{_sbindir}
install -dm755 %{buildroot}/etc/sysconfig
install -m755 --target-directory=%{buildroot}%{_sbindir} packaging/wrappers/%{name}*
install -dm755 %{buildroot}%{_datadir}/%{name}/bin
cp -r %{_builddir}/bin/* %{buildroot}/usr/share/grafana/bin
cp packaging/rpm/sysconfig/grafana-server %{buildroot}/etc/sysconfig


install -d -m0750 %{buildroot}%{_localstatedir}/lib/%{name}
install -d -m0750 %{buildroot}%{_localstatedir}/log/%{name}
install -d -m0755 %{buildroot}/%{_localstatedir}/lib/%{name}/plugins
install -d -m0755 %{buildroot}/%{_localstatedir}/lib/%{name}/dashboards
install -d -m0755 %{buildroot}%{_sysconfdir}/%{name}/provisioning/dashboards

install -Dm640 conf/sample.ini %{buildroot}%{_sysconfdir}/%{name}/%{name}.ini
install -Dm640 {conf/,%{buildroot}%{_sysconfdir}/%{name}/}ldap.toml
install -Dm644 {conf/,%{buildroot}%{_datadir}/%{name}/conf/}defaults.ini
install -m644 {conf/,%{buildroot}%{_datadir}/%{name}/conf/}sample.ini
install -Dm644 {conf/provisioning/dashboards/,%{buildroot}%{_datadir}/%{name}/conf/provisioning/dashboards/}sample.yaml
install -Dm644 {conf/provisioning/datasources/,%{buildroot}%{_datadir}/%{name}/conf/provisioning/datasources/}sample.yaml
cp -pr public %{buildroot}%{_datadir}/%{name}/
install -d -m755 %{buildroot}%{_datadir}/%{name}/vendor
install -d -m755 %{buildroot}%{_datadir}/%{name}/tools

# Do not create debugsourcefiles.list if there are no debug sources
%if %{?debug_package:1}%{!?debug_package:%{1}}
rm -f %{buildroot}%{_builddir}/%{name}-%{version}/debugsourcefiles.list
%endif

# Do *not* use %%fudpes -s -- this will result in grafana failing to load
# all the plugins (something in the plugin scanner can't cope with files
# in there being symlinks).
%fdupes %{buildroot}/%{_datadir}

# SELinux policy
cd SELinux
for selinuxvariant in %{selinux_variants}
do
  install -d %{buildroot}%{_datadir}/selinux/${selinuxvariant}
  install -p -m 644 grafana.pp.${selinuxvariant} \
    %{buildroot}%{_datadir}/selinux/${selinuxvariant}/grafana.pp
done
cd -

%check
#gotest github.com/grafana/grafana/pkg...

%pre
%sysusers_create_compat %{SOURCE9}

%preun
%systemd_preun grafana-server.service

%post
%systemd_post grafana-server.service
# create grafana.db with secure permissions on new installations
# otherwise grafana-server is creating grafana.db on first start
# with world-readable permissions, which may leak encrypted datasource
# passwords to all users (if the secret_key in grafana.ini was not changed)

# https://bugzilla.redhat.com/show_bug.cgi?id=1805472
if [ "$1" = 1 ] && [ ! -f %{_sharedstatedir}/%{name}/grafana.db ]; then
    touch %{_sharedstatedir}/%{name}/grafana.db
fi

# apply secure permissions to grafana.db if it exists
# (may not exist on upgrades, because users can choose between sqlite/mysql/postgres)
if [ -f %{_sharedstatedir}/%{name}/grafana.db ]; then
    chown %{GRAFANA_USER}:%{GRAFANA_GROUP} %{_sharedstatedir}/%{name}/grafana.db
    chmod 640 %{_sharedstatedir}/%{name}/grafana.db
fi

# required for upgrades
chmod 640 %{_sysconfdir}/%{name}/grafana.ini
chmod 640 %{_sysconfdir}/%{name}/ldap.toml

%postun
%systemd_postun_with_restart grafana-server.service

# SELinux policy
%post selinux
for selinuxvariant in %{selinux_variants}
do
  /usr/sbin/semodule -s ${selinuxvariant} -i \
    %{_datadir}/selinux/${selinuxvariant}/grafana.pp &> /dev/null || :
done
/sbin/restorecon -RvF /usr/sbin/grafana* &> /dev/null || :
/sbin/restorecon -RvF /etc/grafana &> /dev/null || :
/sbin/restorecon -RvF /var/log/grafana &> /dev/null || :
/sbin/restorecon -RvF /var/lib/grafana &> /dev/null || :
/sbin/restorecon -RvF /usr/libexec/grafana-pcp &> /dev/null || :
/usr/sbin/semanage port -a -t grafana_port_t -p tcp 3000 &> /dev/null || :

%postun selinux
if [ $1 -eq 0 ] ; then
/usr/sbin/semanage port -d -p tcp 3000 &> /dev/null || :
  for selinuxvariant in %{selinux_variants}
  do
    /usr/sbin/semodule -s ${selinuxvariant} -r grafana &> /dev/null || :
  done
  /sbin/restorecon -RvF /usr/sbin/grafana* &> /dev/null || :
  /sbin/restorecon -RvF /etc/grafana &> /dev/null || :
  /sbin/restorecon -RvF /var/log/grafana &> /dev/null || :
  /sbin/restorecon -RvF /var/lib/grafana &> /dev/null || :
  /sbin/restorecon -RvF /usr/libexec/grafana-pcp &> /dev/null || :
fi

%files selinux
%defattr(-,root,root,0755)
%doc SELinux/*
%{_datadir}/selinux/*/grafana.pp

%files
%defattr(-,root,root)
%license LICENSE*
%doc CHANGELOG*
%{_sbindir}/%{name}*
%{_unitdir}/%{name}-server.service
%attr(0755,root,root) %dir %{_sysconfdir}/%{name}
%attr(0755,root,root) %dir %{_sysconfdir}/%{name}/provisioning
%attr(0755,root,root) %dir %{_sysconfdir}/%{name}/provisioning/dashboards
%attr(0640,root,grafana) %config(noreplace) %{_sysconfdir}/%{name}/%{name}.ini
%attr(0640,root,grafana) %config(noreplace) %{_sysconfdir}/%{name}/ldap.toml
%attr(0644,root,grafana) %config(noreplace) /etc/sysconfig/grafana-server
%attr(0755,root,root) /usr/share/grafana/bin/grafana
%attr(0755,root,root) /usr/share/grafana/bin/grafana-cli
%attr(0755,root,root) /usr/share/grafana/bin/grafana-server
%attr(0755,grafana,grafana) %dir %{_localstatedir}/lib/%{name}
%attr(0755,grafana,grafana) %dir %{_localstatedir}/lib/%{name}/plugins
%attr(0755,grafana,grafana) %dir %{_localstatedir}/lib/%{name}/dashboards
%attr(0750,grafana,grafana) %dir %{_localstatedir}/log/%{name}
%{_datadir}/%{name}


%changelog
* Thu Mar 21 2024 devin.acosta@ringcentral.com
- Version 10.1.5:
  Bugfixes:
  * Initial Build of 10.1.5
