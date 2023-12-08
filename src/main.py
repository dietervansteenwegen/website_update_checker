#! /usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:expandtab:cuc:autoindent:ignorecase:colorcolumn=99

__author__ = 'Dieter Vansteenwegen'
__project__ = 'Website_update_checker'
__project_link__ = 'https://www.vansteenwegen.org'


from checker import check_for_updates, send_changed_urls
from config import Config
from log.log import add_rotating_file, setup_logger


def main():
    log = setup_logger()
    add_rotating_file(log)
    config = Config()

    changed_urls = check_for_updates(config=config)
    if changed_urls:
        send_changed_urls(changed_urls=changed_urls, config=config)


if __name__ == '__main__':
    main()
