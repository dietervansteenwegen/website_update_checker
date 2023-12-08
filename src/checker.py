#! /usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:expandtab:cuc:autoindent:ignorecase:colorcolumn=99

__author__ = 'Dieter Vansteenwegen'
__project__ = 'Website_update_checker'
__project_link__ = 'https://www.vansteenwegen.org'

import asyncio
import logging
import pathlib
from configparser import ConfigParser
from hashlib import sha256
from pathlib import Path
from typing import Union

import requests
from bs4 import BeautifulSoup
from matrix_client import MatrixClient

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) '
    'Gecko/20100101 Firefox/120.0',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
}

log = logging.getLogger(__name__)


def process_html(string) -> str:
    soup = BeautifulSoup(string, features='html.parser')
    soup.prettify()  # make the html look good
    for script in soup.select('script'):  # remove script tags
        script.extract()
    for s in soup.select('meta'):
        s.extract()
    return str(soup)  # convert to a string, remove '\r', and return


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
        data_pretty = process_html(data)
        new_sha_256 = sha256(data_pretty.encode('utf-8')).hexdigest()
        if new_sha_256 != previous_data.get(url.replace(':', ''), ''):
            log.debug(f'Updating SHA-256 for {url} to {new_sha_256}')
            urls_with_changes.append(url)
            add_sha_256(data_file=storage, url=url, sha_256=new_sha_256)
        else:
            log.debug('Website has not changed.')

    if urls_with_changes:
        import platform

        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(
            send_matrix(
                urls=urls_with_changes,
                matrix_conf=matrix_conf,
            ),
        )


async def send_matrix(urls: list[str], matrix_conf: dict[str]) -> None:
    client = MatrixClient(
        homeserver=matrix_conf['homeserver'],
        user=matrix_conf['login'],
        pw=matrix_conf['password'],
    )
    log.debug('logging in')
    await client.login()
    log.debug('logged in')
    for url in urls:
        log.debug(f'sending url {url}')
        await client.send_room_msg(
            room_id=matrix_conf['room'],
            msg_text=f'New changes at URL {url}',
        )
    log.debug('logging out')
    await client.client.logout()
    log.debug('closing')
    await client.client.close()
