#! /usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:expandtab:cuc:autoindent:ignorecase:colorcolumn=99

__author__ = 'Dieter Vansteenwegen'
__project__ = 'Website_update_checker'
__project_link__ = 'https://www.vansteenwegen.org'

import logging
import pathlib
from configparser import ConfigParser
from hashlib import sha256
from pathlib import Path
from typing import Union

import requests

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
}

log = logging.getLogger(__name__)


def add_sha_256(data_file: str, url: str, sha_256: str) -> None:
    parser = ConfigParser()
    parser.read(data_file)
    # parser.add_section('sha_256')
    parser.set('sha_256', url.replace(':', ''), sha_256)
    with Path.open(pathlib.Path(data_file), 'w+') as outp:
        parser.write(outp)


def check_for_updates(
    urls_to_check: list,
    storage: str,
    previous_data: dict,
    matrix_conf: Union[dict, None] = None,
) -> None:
    urls_with_changes: list[str] = []

    for url in urls_to_check:
        if not url.startswith('http'):
            url = f'http://{url}'
        log.info(f'Checking {url}')
        data = requests.get(url, headers=HEADERS, timeout=1).text
        new_sha_256 = sha256(data.encode('utf-8')).hexdigest()
        if new_sha_256 != previous_data.get(url.replace(':', ''), ''):
            log.debug(f'Updating SHA-256 for {url} to {new_sha_256}')
            urls_with_changes.append(url)
            add_sha_256(data_file=storage, url=url, sha_256=new_sha_256)
        else:
            log.debug('Website has not changed.')

    if urls_with_changes:
        # TODO: Send Matrix message
        pass
