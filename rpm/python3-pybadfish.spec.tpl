%global project badfish
%global org     redhat-performance
%global sum     Badfish is a Redfish-based API tool for managing bare-metal systems via the Redfish API
%global desc    Badfish is a vendor-agnostic, redfish-based API tool used to consolidate \
management of IPMI and out-of-band interfaces for common server hardware \
vendors.  Badfish is also a popular song from Sublime, this may be a \
coincidence – are you a badfish too?


Name:           python3-py%{project}
Version:        @VERSION@
Release:        @RELEASE@%{?dist}
Summary:        %{sum}

License:        GPL-3.0-or-later and MIT
URL:            https://github.com/%{org}/%{project}
Source:         %{url}/releases/download/v%{version}/python3-pybadfish-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  %{py3_dist setuptools}
BuildRequires:  %{py3_dist pip}
BuildRequires:  python3-devel
BuildRequires:  zlib-devel
BuildRequires:  python3-coverage
Provides:       badfish = %{version}-%{release}
%generate_buildrequires
%pyproject_buildrequires -t

%description
%{desc}

%prep
%autosetup -n %{name}-%{version}

%build
%pyproject_wheel

%install
%pyproject_install

%check
%tox

%files -n %{name}
%doc README.md
%license LICENSE
%{python3_sitelib}/py%{project}-%{version}.dist-info/
%{python3_sitelib}/%{project}/
%{_bindir}/%{project}

%changelog
* @DATE@ Gonzalo Rafuls <gonza@redhat.com> - @VERSION@-@RELEASE@
- built from upstream, changelog ignored
