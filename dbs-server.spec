%global  dbs_statedir  %{_sharedstatedir}/dbs
%global  dbs_confdir   %{_sysconfdir}/dbs
%global  cron_confdir  %{_sysconfdir}/cron.d
%global  httpd_confdir %{_sysconfdir}/httpd/conf.d
%global  httpd_group   apache

Name:           dbs-server
Version:        0.1
Release:        1%{?dist}

Summary:        Docker Build Service
Group:          Development Tools
License:        TODO
URL:            https://github.com/orgs/DBuildService/dashboard
Source0:        http://github.srcurl.net/DBuildService/%{name}/%{version}/%{name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python-devel
BuildRequires:  python-setuptools

Requires:       httpd
Requires:       mod_ssl
Requires:       mod_wsgi
Requires:       python-celery
Requires:       python-django >= 1.7
Requires:       python-django-celery

%description
Docker Build Service


%prep
%setup -q


%build
# prepare config file
rm dbs/site_settings-development.py
mv dbs/site_settings-production.py site_settings

# move wsgi to document root
mv dbs/wsgi.py htdocs/

# build python package
%{__python} setup.py build


%install
# install python package
%{__python} setup.py install --skip-build --root %{buildroot}

# install config file as target of site_settings.py symlink
install -p -D -m 0644 site_settings \
    %{buildroot}%{dbs_confdir}/site_settings
ln -s %{dbs_confdir}/site_settings \
    %{buildroot}%{python_sitelib}/dbs/site_settings.py

# install commandline interface with bash completion
install -p -D -m 0755 manage.py %{buildroot}%{_bindir}/dbs
install -p -D -m 0644 dbs_bash_completion \
    %{buildroot}%{_sysconfdir}/bash_completion.d/dbs_bash_completion

# install httpd config file and wsgi config file
install -p -D -m 0644 conf/httpd/dbs.conf \
    %{buildroot}%{httpd_confdir}/dbs.conf
install -p -D -m 0644 htdocs/wsgi.py \
    %{buildroot}%{dbs_statedir}/htdocs/wsgi.py

# install directories for static content and site media
install -p -d -m 0775 htdocs/static \
    %{buildroot}%{dbs_statedir}/htdocs/static
install -p -d -m 0775 htdocs/media \
    %{buildroot}%{dbs_statedir}/htdocs/media

# install separate directory for sqlite db
install -p -d -m 0775 data \
     %{buildroot}%{dbs_statedir}/data

# install crontab
#install -p -D -m 0644 conf/cron/dbs \
#    %{buildroot}%{cron_confdir}/dbs

# remove .po files
find %{buildroot} -name "*.po" | xargs rm -f


%post
# create secret key
if [ ! -e        %{dbs_statedir}/secret_key ]; then
    touch        %{dbs_statedir}/secret_key
    chown apache %{dbs_statedir}/secret_key
    chgrp apache %{dbs_statedir}/secret_key
    chmod 0400   %{dbs_statedir}/secret_key
    dd bs=1k  of=%{dbs_statedir}/secret_key if=/dev/urandom count=5
fi

# link default certificate
if [ ! -e               %{_sysconfdir}/pki/tls/certs/dbs.crt ]; then
    ln -s localhost.crt %{_sysconfdir}/pki/tls/certs/dbs.crt
fi

# link default private key
if [ ! -e               %{_sysconfdir}/pki/tls/private/dbs.key ]; then
    ln -s localhost.key %{_sysconfdir}/pki/tls/private/dbs.key
fi

# link default chain file
if [ ! -e               %{_sysconfdir}/pki/tls/certs/dbs.CA.crt ]; then
    ln -s localhost.crt %{_sysconfdir}/pki/tls/certs/dbs.CA.crt
fi

service httpd condrestart

# allow apache read from htdocs and secret_key
chcon    -t httpd_sys_content_t /var/lib/dbs/secret_key
chcon    -t httpd_sys_content_t /var/lib/dbs/htdocs
chcon    -t httpd_sys_content_t /var/lib/dbs/htdocs/wsgi.py*
chcon -R -t httpd_sys_content_t /var/lib/dbs/htdocs/static

# allow apache write to data and media
chcon -R -t httpd_sys_rw_content_t /var/lib/dbs/data
chcon -R -t httpd_sys_rw_content_t /var/lib/dbs/htdocs/media

# install / update database
dbs syncdb --noinput || :

# collect static files
dbs collectstatic --noinput || :


%files
%doc README.md
%{_bindir}/dbs
%{_sysconfdir}/bash_completion.d/dbs_bash_completion
#%config(noreplace) %{cron_confdir}/dbs
%config(noreplace) %{httpd_confdir}/dbs.conf
%config(noreplace) %{dbs_confdir}/site_settings
%{dbs_statedir}/htdocs/wsgi.py*
%attr(755,root,root)           %dir %{dbs_statedir}/htdocs/static
%attr(775,root,%{httpd_group}) %dir %{dbs_statedir}/htdocs/media
%attr(775,root,%{httpd_group}) %dir %{dbs_statedir}/data
%{python_sitelib}/dbs
%{python_sitelib}/dbs-%{version}-py2.*.egg-info


%changelog
* Wed Oct 22 2014 Jakub Dorňák <jdornak@redhat.com> - 0.1-1
- Initial package

