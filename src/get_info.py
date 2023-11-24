#! /usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:expandtab:cuc:autoindent:ignorecase:colorcolumn=99

__author__ = 'Dieter Vansteenwegen'
__project__ = 'Website_update_checker'
__project_link__ = 'https://www.vansteenwegen.org'


import argparse
import logging
from configparser import ConfigParser

log = logging.getLogger(__name__)


class HelpfullArgumentParser(argparse.ArgumentParser):
    def error(self, msg):
        import sys

        print(f"This possibly isn't what you intended to do: {msg}")
        self.print_usage()
        sys.exit(2)


def get_arguments() -> argparse.Namespace:
    parser = HelpfullArgumentParser(add_help=True)

    parser.add_argument(
        '-m',
        '--matrix_config_file',
        help='Location of the file with details for the Matrix functionality.',
        action='store',
        dest='matrix_conf_file',
    )

    parser.add_argument(
        '-s',
        '--storage_file',
        help='Location of the file where to store data.',
        action='store',
        dest='storage_file',
    )

    parser.add_argument(
        '-w',
        '--send_matrix_message',
        help='Send message to matrix if updates are found.',
        action='store_true',
        default=True,
        dest='send_matrix_message',
    )

    parser.add_argument(
        '-u',
        '--url_to_check',
        help='URL to check.',
        action='append',
        default=[],
        dest='urls_to_check',
    )

    return parser.parse_args()


def get_matrix_info(conf_file: str) -> dict:
    if not conf_file:
        msg = 'Need config file for the Matrix functionality.'
        log.error(msg)
        raise ValueError(msg)
    log.debug(f'Getting matrix config from {conf_file}')
    parser = ConfigParser()
    parser.read(conf_file)
    config = {}
    for section in parser.sections():
        for field, value in parser.items(section):
            config[field] = value
    info_not_found = []
    for item in ('login', 'password', 'room', 'homeserver'):
        if item not in config:
            info_not_found.append(item)

    if info_not_found:
        msg = (
            f'Could not find all fields {info_not_found} in the [matrix] section. '
            f'Information found: {config}'
        )
        log.error(msg)
        raise ValueError(msg)
    return config


def get_previous_data(src: str) -> dict[str]:
    if not src:
        msg = 'Need storage file for data storage.'
        log.error(msg)
        raise ValueError(msg)
    log.debug(f'Getting previous data from {src}')
    parser = ConfigParser()
    parser.read(src)
    config = {}
    for section in parser.sections():
        for field, value in parser.items(section):
            config[field] = value
    return config
