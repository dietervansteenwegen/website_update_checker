#! /usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:expandtab:cuc:autoindent:ignorecase:colorcolumn=99

__author__ = 'Dieter Vansteenwegen'
__project__ = 'Website_update_checker'
__project_link__ = 'https://www.vansteenwegen.org'

import asyncio
import logging
from hashlib import sha256

import requests
from bs4 import BeautifulSoup
from config import Config
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


def check_for_updates(config: Config) -> list:
    urls_with_changes: list[str] = []

    for [url, orig_sha256] in config.urls():
        log.info(f'Checking {url}')
        data = requests.get(f'https://{url}', headers=HEADERS, timeout=1).text
        data_pretty = process_html(data)
        new_sha256 = sha256(data_pretty.encode('utf-8')).hexdigest()
        if new_sha256 != orig_sha256:
            log.debug(f'Updating SHA-256 for {url} to {new_sha256}')
            urls_with_changes.append(url)
            config.update_sha256(url=url, new_sha256=new_sha256)
        else:
            log.debug('Website has not changed.')

    return urls_with_changes


def send_changed_urls(changed_urls: list, config=Config) -> bool:
    import platform

    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(
        send_matrix(
            urls=changed_urls,
            matrix_conf=config.matrix_config(),
        ),
    )
    return True


async def send_matrix(urls: list[str], matrix_conf: dict[str]) -> None:
    client = MatrixClient(
        homeserver=matrix_conf['homeserver'],
        user=matrix_conf['login'],
        pw=matrix_conf['password'],
    )
    await client.login()
    log.debug('logged in')
    for url in urls:
        log.debug(f'sending url {url}')
        await client.send_room_msg(
            room_id=matrix_conf['room'],
            msg_text=f'New changes at URL {url}',
        )
    await client.client.logout()
    log.debug('closing')
    await client.client.close()
