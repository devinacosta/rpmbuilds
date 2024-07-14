#!/bin/bash
dnf -y install epel-release
dnf -y install neovim

dnf -y golang

# Download Microsoft GoLang Source into /usr/local/go and then compile.
# Using Microsoft Go Version 1.22, because it has all the FIPS fixes.
# Using already compiled version, no reason to rebuild
cd /usr/local/
mkdir go
wget https://aka.ms/golang/release/latest/go1.22.linux-amd64.tar.gz
tar xvfp go1.22.linux-amd64.tar.gz


# Now Update Microsoft in PATH
echo "export PATH=$PATH:/usr/local/go/bin" >> /root/.bashrc
source /root/.bashrc

# Install Python3 PIP and Packaging/Yaml
dnf -y install python3-pip 
pip3 install packaging
pip3 install pyyaml

# Now Install NodeJS with Yarn
dnf -y install nodejs
npm install --global yarn

# Install RPM Build and Tools
dnf -y install rpm-build rpmdevtools

# Install GCC C++
dnf -y install gcc-c++

# Install Final SPEC requirements
dnf -y install fdupes git-core selinux-policy-devel

# Install Wire
# Ensure Wire compiled with systemcrypto and GOFIPS=1
export GOEXPERIMENT=systemcrypto
export GOFIPS=1
go install github.com/google/wire/cmd/wire@latest
cp go/bin/wire /usr/local/go/bin

# Display you are now ready to compile
echo "You are now ready to compile the grafana.spec in /root/rpmbuild/SOURCES/grafana.spec"
echo "Good Luck!"
