%global commit0 b5969f9311c07a80250c3ab5e1174a792195e8e3
%global date 20240514
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

# Build only the akmod package and no kernel module packages:
%define buildforkernels akmod

%global debug_package %{nil}

Name:           ivsc-kmod
Version:        0
Release:        2.%{date}git%{shortcommit0}%{?dist}
Summary:        Driver for Intel Vision Sensing Controller(IVSC)
License:        GPL-3.0-only
URL:            https://github.com/intel/ivsc-driver

Source0:        %{url}/archive/%{commit0}.tar.gz#/ivsc-driver-%{shortcommit0}.tar.gz
Patch0:         firmware-path.patch

# Get the needed BuildRequires (in parts depending on what we build for):
BuildRequires:  kmodtool

# kmodtool does its magic here:
%{expand:%(kmodtool --target %{_target_cpu} --repo negativo17.org --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%description
Driver for Intel Vision Sensing Controller(IVSC).

%prep
# Error out if there was something wrong with kmodtool:
%{?kmodtool_check}
# Print kmodtool output for debugging purposes:
kmodtool  --target %{_target_cpu}  --repo negativo17.org --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

%autosetup -p1 -n ivsc-driver-%{commit0}

for kernel_version in %{?kernel_versions}; do
    mkdir _kmod_build_${kernel_version%%___*}
    cp -fr backport-include drivers include Makefile _kmod_build_${kernel_version%%___*}
done

%build
for kernel_version in %{?kernel_versions}; do
    pushd _kmod_build_${kernel_version%%___*}/
        %make_build -C "${kernel_version##*___}" M=$(pwd) VERSION="v%{version}" modules
    popd
done

%install
for kernel_version in %{?kernel_versions}; do
    mkdir -p %{buildroot}/%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
    install -p -m 0755 _kmod_build_${kernel_version%%___*}/*.ko \
        %{buildroot}/%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
done
%{?akmod_install}

%changelog
* Fri Jun 21 2024 Simone Caronni <negativo17@gmail.com> - 0-2.20240514gitb5969f9
- Add patch to load upstreamed firmware.

* Mon May 06 2024 Simone Caronni <negativo17@gmail.com> - 0-1.20240416gita6dccbb
- First build.
