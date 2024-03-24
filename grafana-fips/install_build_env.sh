#!/bin/bash
dnf -y install epel-release
dnf -y install neovim

dnf -y golang

# Download Microsoft GoLang Source into /usr/local/go and then compile.
cd /usr/local/
mkdir go
wget https://github.com/microsoft/go/releases/download/v1.20.8-1/go.20230906.3.src.tar.gz
tar xvfp go.20230906.3.src.tar.gz

# Compile GoLang Now using local go
cd /usr/local/go/src
./all.bash

# Now disable local go
cd /usr/bin
mv go go.hold

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
go install github.com/google/wire/cmd/wire@latest

# Display you are now ready to compile
echo "You are now ready to compile the grafana.spec in /root/rpmbuild/SOURCES/grafana.spec"
echo "Good Luck!"
