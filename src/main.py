#! /usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:expandtab:cuc:autoindent:ignorecase:colorcolumn=99

__author__ = 'Dieter Vansteenwegen'
__project__ = 'Website_update_checker'
__project_link__ = 'https://www.vansteenwegen.org'

from checker import check_for_updates
from get_info import get_arguments, get_matrix_info, get_previous_data
from log.log import add_rotating_file, setup_logger


def main():
    log = setup_logger()
    add_rotating_file(log)
    args = get_arguments()
    if args.send_matrix_message:
        matrix_conf = get_matrix_info(conf_file=args.matrix_conf_file)
    else:
        matrix_conf = {}
    previous_data = get_previous_data(args.storage_file)
    check_for_updates(
        urls_to_check=args.urls_to_check,
        storage=args.storage_file,
        previous_data=previous_data,
        matrix_conf=matrix_conf,
    )


if __name__ == '__main__':
    main()
