%global project badfish
%global org     redhat-performance
%global sum     Badfish is a Redfish-based API tool for managing bare-metal systems via the Redfish API
%global desc    Badfish is a vendor-agnostic, redfish-based API tool used to consolidate \
management of IPMI and out-of-band interfaces for common server hardware \
vendors.  Badfish is also a popular song from Sublime, this may be a \
coincidence – are you a badfish too?


Name:           python3-%{project}
Version:        @VERSION@
Release:        @RELEASE@%{?dist}
Summary:        %{sum}

License:        GPLv3
URL:            https://github.com/%{org}/%{project}
Source:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  %{py3_dist setuptools}
BuildRequires:  %{py3_dist pip}
BuildRequires:  python3-devel
BuildRequires:  zlib-devel
BuildRequires:  libjpeg-turbo-devel

%description
%{desc}

%prep
%autosetup -n %{name}-%{version}

%build
%py3_build

%install
%py3_install

%files -n %{name}
%doc README.md
%license LICENSE
%{python3_sitelib}/%{project}/
%{python3_sitelib}/%{project}-%{version}-py%{python3_version}.egg-info/
%{_bindir}/%{project}

%changelog
* @DATE@ Gonzalo Rafuls <gonza@redhat.com> - @VERSION@-@RELEASE@
- built from upstream, changelog ignored
