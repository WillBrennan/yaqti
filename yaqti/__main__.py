import logging
import pathlib
from typing import List

import click

cli = click.Group()

from .fetchers import fetch_versions
from .fetchers import fetch_archive_xml
from .fetchers import fetch_package_infos
from .packages import fetch_packages
from .helpers import check
from .helpers import configure_logging


@cli.command()
@click.option('--version', type=str, required=True, help='a Qt version format like "6.2.0"')
@click.option('--os', required=True, type=click.Choice(['linux', 'mac', 'windows']))
@click.option('--platform', required=True, type=click.Choice(['desktop', 'winrt', 'android', 'ios']))
@click.option('--output', type=str, default='./qt')
@click.option('--modules', type=str, multiple=True)
def install(os: str, platform: str, version: str, output: str, modules: List[str]):
    versions = fetch_versions()
    assert version in versions, f'{version} is unsupported; available Qt modules are {versions}'

    logging.info(f'fetching Qt {version} for {os}/{platform}')

    base_url, xml = fetch_archive_xml(os, platform, version)
    check(xml is not None, f'Qt {version} does not support {os}/{platform} arguments')

    packages = fetch_package_infos(base_url, xml, modules)

    output = pathlib.Path(output) / version
    fetch_packages(output, packages)


if __name__ == '__main__':
    configure_logging()
    cli()
