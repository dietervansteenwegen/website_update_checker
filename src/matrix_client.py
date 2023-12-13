#! /usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:expandtab:cuc:autoindent:ignorecase:colorcolumn=99

import logging

from nio import AsyncClient, MatrixRoom, RoomMessageText

log = logging.getLogger(__name__)


class MatrixClient:
    def __init__(
        self,
        homeserver: str,
        user: str,
        pw: str,
    ):
        self._homeserver = homeserver
        self._user = user
        self._pw = pw

    async def login(self) -> None:
        log.debug('Logging in')
        self.client = AsyncClient(homeserver=self._homeserver, user=self._user)
        self.client.add_event_callback(self._msg_callback, RoomMessageText)
        await self.client.login(self._pw)  # 'Logged in as @xxx:example.org device id: RANDOMDID'
        log.debug('Logged in.')

    async def _msg_callback(self, room: MatrixRoom, event: RoomMessageText) -> None:
        print(f'{room.room_id}| {room.user_name(event.sender)} | {event.body}')

    async def send_room_msg(self, room_id: str, msg_text: str = '') -> None:
        log.debug('Sending message')
        await self.client.room_send(
            room_id=room_id,
            message_type='m.room.message',
            content={
                'msgtype': 'm.text',
                'body': msg_text,
                'm.mentions': {},
            },
        )
        log.debug('Done sending message')
