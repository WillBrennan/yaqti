import logging
import pathlib
from typing import List
from os import environ
from platform import system
import subprocess

import click

cli = click.Group()

from .fetchers import fetch_versions
from .fetchers import fetch_archive_xml
from .fetchers import fetch_package_infos
from .packages import fetch_packages
from .helpers import check
from .helpers import configure_logging
from .helpers import split_version


@cli.command()
@click.option('--version', type=str, required=True, help='a Qt version format like "6.2.0"')
@click.option('--os', required=True, type=click.Choice(['linux', 'mac', 'windows']))
@click.option('--platform', required=True, type=click.Choice(['desktop', 'winrt', 'android', 'ios']))
@click.option('--output', type=str, default='./qt')
@click.option('--modules', type=str, multiple=True)
@click.option('--set-envs', type=bool, is_flag=True)
@click.option('--install-deps', type=bool, is_flag=True)
def install(os: str, platform: str, version: str, output: str, modules: List[str], set_envs: bool, install_deps: bool):
    versions = fetch_versions()
    assert version in versions, f'{version} is unsupported; available Qt modules are {versions}'

    logging.info(f'fetching Qt {version} for {os}/{platform}')

    base_url, xml = fetch_archive_xml(os, platform, version)
    check(xml is not None, f'Qt {version} does not support {os}/{platform} arguments')

    packages = fetch_package_infos(base_url, xml, modules)

    output = pathlib.Path(output)
    output = output.absolute()

    fetch_packages(output, packages)

    if set_envs:
        output = output / version
        major, _, _ = split_version(version)
        env = f'Qt{major}_DIR'
        logging.info(f'setting enviroment variable: {env}={output}')
        environ[env] = str(output)

    if install_deps and system() == 'Linux':
        logging.info('installing Qt dependencies')
        run = lambda cmd: subprocess.run(cmd, shell=True, check=True)

        run('sudo apt-get -yq update')
        run('sudo apt-get -yq install build-essential libgl1-mesa-dev libxkbcommon-x11-0 libpulse-dev -y')
        logging.info('finished installing Qt dependencies')


if __name__ == '__main__':
    configure_logging()
    cli()
