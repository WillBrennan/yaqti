from click.testing import CliRunner
import pytest
from pytest import mark

from yaqti.__main__ import install

def test_install_bad_args():
    result = CliRunner().invoke(install, ["install"])
    print(result.output)
    assert result.exit_code != 0

def test_install_bad_os():
    result = CliRunner().invoke(install, ['--os=ios', '--version=5.15.2', '--platform=desktop'])
    print(result.output)
    assert result.exit_code  != 0

def test_install_bad_platform():
    result = CliRunner().invoke(install, ['--os=linux', '--version=5.15.2', '--platform=dektop'])
    print(result.output)
    assert result.exit_code  != 0

def test_install_bad_version():
    result = CliRunner().invoke(install, ['--os=linux', '--version=5.15.3', '--platform=desktop'])
    print(result.output)
    assert result.exit_code != 0


def test_install_bad_modules():
    print('here')
    result = CliRunner().invoke(install, ['--os=linux', '--version=6.2.0', '--platform=desktop', '--modules', 'qcharts'])
    print(result.output)
    assert result.exit_code != 0


@mark.skip()
def test_install():
    runner = CliRunner()
    # run yaqti to install CMake (only run if the OS matches our current OS...)
    result = runner.invoke(install, ['--os=linux'])
    assert result.exit_code == 0

    # check cmake version is 3.20 (with fix for Qt bug)
    # save off templated CMakeLists for Qt 5 vs Qt6...
    # run cmake, check it finds everything!
