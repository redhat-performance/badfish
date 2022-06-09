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
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-setuptools
BuildRequires:  python3-devel
BuildRequires:  python3-pip
BuildRequires:  zlib-devel

%description
%{desc}

%prep
%autosetup -n %{name}-%{version}

%build
%py3_build

%install
%{__python3} -m pip install . --prefix ~/.local

%files -n %{name}
%doc README.md
%license LICENSE

%changelog
* @DATE@ Gonzalo Rafuls <gonza@redhat.com> - @VERSION@-@RELEASE@
- built from upstream, changelog ignored
