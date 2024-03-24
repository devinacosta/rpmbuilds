# RPMBuild - Grafana
## _Complete documentation._

This documentation covers what you need to know in order to successfully recompile
Grafana from the enclosed RPMBUILD package.

**Your build server will need the following in order to successfully compile.**
- **Oracle Enterprise Linux 9.3 w/sufficient disk space**
- _Build Server needs at least_ **6GB of RAM, 4 CPU**
- _**Microsoft GO Lang**_ version **1.20.8**, installed into /usr/local/go
- _**NodeJS**_ **16.20.2** (Comes with OEL9.3)
- **RPM Build Utilities and modules.** (See Installation script in Repo)
- Updated Environment reflecting the changes above.
- ✨Magic ✨

## Installation
You will need to run the install_build_env.sh script to setup the environment correctly.
```bash
./install_build_env.sh
```

Once the script has been completed, you are now ready to compile from RPM SPEC file
```bash
cd /root/rpmbuild/SOURCES
rpmbuild -bb grafana.spec
```

Upon completion you should see 2 RPM packages as follows:
```sh
.
├── grafana-10.1.5-2.1.x86_64.rpm
└── grafana-selinux-10.1.5-2.1.x86_64.rpm
```
You ae required to install BOTH RPM files for proper functioning in SELinux environment.

If you have any questions contact Devin Acosta, Monitoring Team.
Good luck! :)
