import datetime
from typing import Union

from aiogram import types
from asyncpg import Connection
from pydantic import BaseModel, parse_obj_as

from services.sql_placeholders import generate_sql_placeholders


class MessagesByIdsQueryResult(BaseModel):
    """Результат запроса с сообщениями."""

    message_id: int
    chat_id: int


class UpdatesLogRepositoryInterface(object):
    """Интерфейс для работы с хранилищем пакетов от телеграма."""

    async def save_message(self, message: types.Message):
        """Сохранить сообщение.

        :param message: types.Message
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def save_callback_query(self, callback_query: types.CallbackQuery):
        """Сохранить информацию о нажатии на кнопку.

        :param callback_query: types.CallbackQuery
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def bulk_save_messages(self, messages: list[types.Message], mailing_id: int = None):
        """Массовое сохранение сообщений.

        :param messages: list[types.Message]
        :param mailing_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def get_messages(self, message_ids: list[int]) -> list[MessagesByIdsQueryResult]:
        """Достать сообдения для последующего удаления из чата.

        :param message_ids: list[int]
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class UpdatesLogRepository(UpdatesLogRepositoryInterface):
    """Класс для работы с хранилищем пакетов от телеграма."""

    _connection: Connection

    def __init__(self, connection: Connection):
        self._connection = connection

    async def save_message(self, message: types.Message):
        """Сохранить сообщение.

        :param message: types.Message
        """
        query = """
            INSERT INTO bot_init_message
            (date, from_user_id, message_id, chat_id, text, json, is_unknown)
            VALUES
            ($1, $2, $3, $4, $5, $6, $7)
        """
        is_unknown = False
        await self._connection.execute(
            query,
            message.date,
            message.from_user.id,
            message.message_id,
            message.chat.id,
            message.text,
            message.as_json(),
            is_unknown,
        )

    async def bulk_save_messages(self, messages: list[types.Message], mailing_id: int = None):
        """Сохранить сообщения.

        :param messages: list[types.Message]
        :param mailing_id: int
        """
        query_template = """
            INSERT INTO bot_init_message
            (date, from_user_id, message_id, chat_id, text, json, is_unknown, mailing_id)
            VALUES
            {0}
        """
        query = query_template.format(generate_sql_placeholders(messages, 8))
        arguments_list: list[Union[str, datetime.datetime, int, bool]] = []
        for message in messages:
            fields = [
                message.date,
                message.from_user.id,
                message.message_id,
                message.chat.id,
                message.text,
                message.as_json(),
                False,
                mailing_id,
            ]
            arguments_list = sum([arguments_list, fields], start=[])
        await self._connection.execute(query, *arguments_list)

    async def get_messages(self, message_ids: list[int]) -> list[MessagesByIdsQueryResult]:
        """Достать сообдения для последующего удаления из чата.

        :param message_ids: list[int]
        :return: list[MessagesByIdsQueryResult]
        """
        query_template = """
            SELECT message_id, chat_id
            FROM bot_init_message
            WHERE message_id IN {0}
        """
        query = query_template.format(generate_sql_placeholders([1], len(message_ids)))
        rows = await self._connection.fetch(query, *message_ids)
        return parse_obj_as(list[MessagesByIdsQueryResult], rows)

    async def save_callback_query(self, callback_query: types.CallbackQuery):
        """Сохранить информацию о нажатии на кнопку.

        :param callback_query: types.CallbackQuery
        """
        query = """
            INSERT INTO bot_init_callbackdata
            (date, call_id, chat_id, text, json)
            VALUES
            ($1, $2, $3, $4, $5)
        """
        await self._connection.execute(
            query,
            datetime.datetime.now(),
            callback_query.id,
            callback_query.from_user.id,
            callback_query.data,
            callback_query.as_json(),
        )
