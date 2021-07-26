# yaqti (Yet Another QT Installer - ya-q-ti!)
[![PyPI version](https://badge.fury.io/py/yaqti.svg)](https://badge.fury.io/py/yaqti)
[![Python Unit-Tests (pytest)](https://github.com/WillBrennan/yaqti/actions/workflows/unit_tests.yml/badge.svg)](https://github.com/WillBrennan/yaqti/actions/workflows/unit_tests.yml)
## Overview
`yaqti` is a basic unofficial CLI Qt installer; designed to keep things as stupid as possible. It lets you install different Qt5 and Qt6 versions with optional modules such as QtCharts, QtNetworkAuth ect all in a single command,

```bash
# install yaqti
pip install yaqti
# install Qt! 
python -m yaqti install --os windows --platform desktop --version 6.2.0 --modules qtcharts qtquick3d
```
, optionally the `--set-env` can be specified. This sets `Qt5_DIR`/`Qt6_DIR` so CMake can find the installation. `--install-deps` can be specified, on Linux platforms to install Qt dependencies from `apt-get`.
It can also be used as a github action,

```yml
-   name: Install Qt
    uses: WillBrennan/yaqti
    with:
        version: '6.2.0'
        host: 'linux'
        target: 'desktop'
        modules: 'qtcharts qtwebengine'
```
. By default, the github-action will set the enviroment variables for Qt and install Qt dependencies. For a real-world example visit [disk_usage](https://github.com/WillBrennan/disk_usage), the project this was made for. 

## Options
### `version`
The version of Qt to install, for example `6.2.0` or `5.15.2`. It checks the version is valid. 

### `os`
The operating system you'll be running on `linux`, `windows`, or `mac`.

### `platform`
The platform you'll be building for, `desktop`, `winrt`, `android`, or `ios`. 

### `modules`
The optional Qt modules to install such as, `qtcharts`, `qtpurchasing`, `qtwebengine`, `qtnetworkauth`, `qtscript`, `debug_info`.

### `output` - `default: ./qt`
The directory to install Qt in, it will put it in a `version` sub directory. By default if you install `--version=5.15.2` it will install qt into `./qt/5152`.

### `--set-envs`
Designed for use in CI pipelines; this sets enviromental variables such as `PATH`, `Qt5_DIR`, and `Qt6_DIR` so CMake can find Qt and you can use executables directly.

### `--install-deps`
Designed for use in CI pipelines. This installs dependencies required by Qt on Linux platforms. If this flag is provided on non-linux platforms it does nothing.

## Why Another Qt CLI Installer? 
I've had issues with other CLI installers in the past,

- They'll silently fail to download a module if you type `qcharts` instead of `qtcharts`
- This fetches module and addon configurations directly from the Qt Archive, new modules and versions will appear without the tool updating!
- It keeps module names the same between Qt5 and Qt6 despite Qt moving them around a bit.
- I like to keep things stupidly simple!

## How does it work?!
Qt provides the [Qt Archive](https://download.qt.io/online/qtsdkrepository), this script simply works out what 7zip files to fetch and unpacks them to the specified installation directory. Then if you want, it sets the enviroment variable so CMake can find the install.

