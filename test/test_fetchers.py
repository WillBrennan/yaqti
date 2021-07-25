from typing import List
import functools
import json

from yaqti.fetchers import fetch_archive_xml
from yaqti.fetchers import fetch_package_infos
from yaqti.helpers import is_valid_url

import pytest
from pytest import mark


@functools.lru_cache(maxsize=None)
def cached_fetch_archive_xml(os: str, platform: str, version: str):
    # note(will.brennan) - want to limit calls to Qt...
    return fetch_archive_xml(os, platform, version)


all_versions = ('5.9.0', '5.9.1', '5.9.2', '5.9.3', '5.9.4', '5.9.5', '5.9.6', '5.9.7', '5.9.8', '5.9.9', '5.10.0',
                '5.10.1', '5.11.0', '5.11.1', '5.11.2', '5.11.3', '5.12.0', '5.12.1', '5.12.2', '5.12.3', '5.12.4',
                '5.12.5', '5.12.6', '5.12.7', '5.12.8', '5.12.9', '5.12.10', '5.12.11', '5.13.0', '5.13.1', '5.13.2',
                '5.14.0', '5.14.1', '5.14.2', '5.15.0', '5.15.1', '5.15.2', '6.0.0', '6.0.1', '6.0.2', '6.0.3', '6.0.4',
                '6.1.0', '6.1.1', '6.1.2', '6.2.0')

all_oss = ('windows', 'linux', 'mac')
all_platforms = ('desktop', 'winrt', 'android', 'ios')


@mark.parametrize('os', all_oss)
@mark.parametrize('platform', all_platforms)
@mark.parametrize('version', all_versions)
def test_fetch_archive_xml(os: str, platform: str, version: str) -> None:
    is_unsupported = False
    is_unsupported |= platform == 'ios' and os != 'mac'
    is_unsupported |= platform == 'winrt' and os != 'windows'
    is_unsupported |= platform == 'winrt' and os == 'windows' and int(version[0]) >= 6

    _, xml = cached_fetch_archive_xml(os, platform, version)

    if is_unsupported:
        assert xml is None
        return

    assert xml is not None

    def check_keys(entry, keys: List[str]) -> bool:
        return all(key in entry for key in keys)

    check_keys(xml, ('Updates', ))
    check_keys(xml['Updates'],
               ('ApplicationName', 'ApplicationVersion', 'Checksum', 'PackageUpdate', 'MetadataName', 'SHA1'))

    assert xml['Updates']['ApplicationName'] == '{AnyApplication}'
    assert xml['Updates']['ApplicationVersion'] == '1.0.0'
    assert xml['Updates']['Checksum'] == 'true'

    for package in xml['Updates']['PackageUpdate']:
        check_keys(package, ('Name', 'DisplayName', 'Description', 'Version', 'ReleaseDate', 'Default', 'AutoDependOn',
                             'Script', 'DownloadableArchives', 'SHA1'))


@pytest.fixture
def fetch_package_infos_explicit():
    params = {}
    yield params

    assert len(params['names']) == params['num_names']
    assert len(params['archive_urls']) == params['num_archive_urls']

    base_url, xml = cached_fetch_archive_xml(params['os'], params['platform'], params['version'])
    packages = fetch_package_infos(base_url, xml, params['modules'])

    names = [package.name for package in packages]
    archive_urls = [archive_url for package in packages for archive_url in package.archive_urls]

    names = sorted(names)
    archive_urls = sorted(archive_urls)

    assert len(names) == params['num_names']
    assert len(archive_urls) == params['num_archive_urls']

    expt_names = sorted(params['names'])
    expt_archive_urls = sorted(params['archive_urls'])

    assert names == expt_names

    print('extra urls', [i for i in archive_urls if i not in expt_archive_urls])
    print('missing urls', [i for i in expt_archive_urls if i not in archive_urls])

    assert archive_urls == expt_archive_urls

    for archive_url in archive_urls:
        assert is_valid_url(archive_url), archive_url


def test_fetch_package_infos_explicit_qt5(fetch_package_infos_explicit):
    params = fetch_package_infos_explicit
    params['os'] = 'linux'
    params['platform'] = 'desktop'
    params['version'] = '5.15.2'
    params['modules'] = ['qtcharts', 'qtnetworkauth', 'qtquick3d']
    params['num_names'] = 7
    params['names'] = [
        'qt.qt5.5152.qtcharts', 'qt.qt5.5152.qtcharts.gcc_64', 'qt.qt5.5152.qtnetworkauth',
        'qt.qt5.5152.qtnetworkauth.gcc_64', 'qt.qt5.5152.qtquick3d', 'qt.qt5.5152.qtquick3d.gcc_64',
        'qt.qt5.5152.gcc_64'
    ]
    params['num_archive_urls'] = 30
    params['archive_urls'] = [
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.gcc_64/5.15.2-0-202011130601qtbase-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.gcc_64/5.15.2-0-202011130601qtconnectivity-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.gcc_64/5.15.2-0-202011130601qtx11extras-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.gcc_64/5.15.2-0-202011130601qtwebchannel-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.gcc_64/5.15.2-0-202011130601qtmultimedia-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.gcc_64/5.15.2-0-202011130601qttranslations-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.gcc_64/5.15.2-0-202011130601qtgraphicaleffects-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.gcc_64/5.15.2-0-202011130601qtsvg-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.gcc_64/5.15.2-0-202011130601qtdeclarative-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.gcc_64/5.15.2-0-202011130601qtwebsockets-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.gcc_64/5.15.2-0-202011130601qtimageformats-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.gcc_64/5.15.2-0-202011130601qttools-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.gcc_64/5.15.2-0-202011130601qtxmlpatterns-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.gcc_64/5.15.2-0-202011130601qtsensors-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.gcc_64/5.15.2-0-202011130601qtserialport-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.gcc_64/5.15.2-0-202011130601qtlocation-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.gcc_64/5.15.2-0-202011130601qtquickcontrols-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.gcc_64/5.15.2-0-202011130601qtquickcontrols2-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.gcc_64/5.15.2-0-202011130601qt3d-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.gcc_64/5.15.2-0-202011130601qtwebview-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.gcc_64/5.15.2-0-202011130601qtserialbus-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.gcc_64/5.15.2-0-202011130601qtscxml-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.gcc_64/5.15.2-0-202011130601qtgamepad-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.gcc_64/5.15.2-0-202011130601qtspeech-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.gcc_64/5.15.2-0-202011130601qtwayland-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.gcc_64/5.15.2-0-202011130601qtremoteobjects-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.gcc_64/5.15.2-0-202011130601icu-linux-Rhel7.2-x64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.qtcharts.gcc_64/5.15.2-0-202011130601qtcharts-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.qtquick3d.gcc_64/5.15.2-0-202011130601qtquick3d-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt5_5152/qt.qt5.5152.qtnetworkauth.gcc_64/5.15.2-0-202011130601qtnetworkauth-Linux-RHEL_7_6-GCC-Linux-RHEL_7_6-X86_64.7z'
    ]


def test_fetch_package_infos_explicit_qt6(fetch_package_infos_explicit):
    params = fetch_package_infos_explicit
    params['os'] = 'linux'
    params['platform'] = 'desktop'
    params['version'] = '6.2.0'
    params['modules'] = ['qtcharts', 'qtnetworkauth', 'qtquick3d']
    params['num_names'] = 9
    params['names'] = [
        'qt.qt6.620.addons.qtcharts', 'qt.qt6.620.addons.qtcharts.gcc_64', 'qt.qt6.620.addons.qtnetworkauth',
        'qt.qt6.620.addons.qtnetworkauth.gcc_64', 'qt.qt6.620.qtquick3d', 'qt.qt6.620.qtquick3d.gcc_64',
        'qt.qt6.620.gcc_64', 'qt.qt6.620.qtshadertools', 'qt.qt6.620.qtquicktimeline'
    ]
    params['num_archive_urls'] = 11
    params['archive_urls'] = [
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt6_620/qt.qt6.620.addons.qtcharts.gcc_64/6.2.0-0-202107051001qtcharts-Linux-RHEL_8_2-GCC-Linux-RHEL_8_2-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt6_620/qt.qt6.620.addons.qtnetworkauth.gcc_64/6.2.0-0-202107051001qtnetworkauth-Linux-RHEL_8_2-GCC-Linux-RHEL_8_2-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt6_620/qt.qt6.620.gcc_64/6.2.0-0-202107051001icu-linux-Rhel7.2-x64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt6_620/qt.qt6.620.gcc_64/6.2.0-0-202107051001qtbase-Linux-RHEL_8_2-GCC-Linux-RHEL_8_2-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt6_620/qt.qt6.620.gcc_64/6.2.0-0-202107051001qtdeclarative-Linux-RHEL_8_2-GCC-Linux-RHEL_8_2-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt6_620/qt.qt6.620.gcc_64/6.2.0-0-202107051001qtquickcontrols2-Linux-RHEL_8_2-GCC-Linux-RHEL_8_2-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt6_620/qt.qt6.620.gcc_64/6.2.0-0-202107051001qtsvg-Linux-RHEL_8_2-GCC-Linux-RHEL_8_2-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt6_620/qt.qt6.620.gcc_64/6.2.0-0-202107051001qttools-Linux-RHEL_8_2-GCC-Linux-RHEL_8_2-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt6_620/qt.qt6.620.gcc_64/6.2.0-0-202107051001qttranslations-Linux-RHEL_8_2-GCC-Linux-RHEL_8_2-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt6_620/qt.qt6.620.gcc_64/6.2.0-0-202107051001qtwayland-Linux-RHEL_8_2-GCC-Linux-RHEL_8_2-X86_64.7z',
        'https://download.qt.io/online/qtsdkrepository/linux_x64/desktop/qt6_620/qt.qt6.620.qtquick3d.gcc_64/6.2.0-0-202107051001qtquick3d-Linux-RHEL_8_2-GCC-Linux-RHEL_8_2-X86_64.7z'
    ]