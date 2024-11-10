import asyncio
import logging
from typing import NoReturn

import aiohttp
import aiogram
from aiogram import Bot

import pydantic_core

from config import config

from keyboards import common_keyboards as kbs

from bot_connections.sockets.endpoints import ChatWebSocketHandlersV1 as Handlers
from bot_connections.sockets.schemas import WebSocketMessage

# TODO: сделать нормальное хранилище
# Словарь для хранения WebSocket соединений
ws_connections = {}


async def websocket_listener(
    bot: Bot, chat_id: int, internal_id: str, room_id: int
) -> NoReturn:
    """Создание WebSocket подключения

    Args:
        bot (Bot): бот Telegram
        chat_id (int): ID чата
        internal_id (str): Внутренний ID пользователя
        room_id (int): ID комнаты в системе

    Returns:
        NoReturn: функция ничего не возвращает при обычный работа
    """

    # Сообщение подписки на канал в сокете
    subscribe_message = {
        "command": "subscribe",
        "identifier": '{"channel":"UserChannel"}',
    }

    # Сообщение для поиска нужной комнаты
    fetch_message = {
        "command": "message",
        "data": '{"action": "fetch_room"}',
        "identifier": '{"channel":"UserChannel"}',
    }

    # Объект для хранения текущего сообщения в режиме стриминга
    # (т.е. которое нужно дописывать)
    stream_message = None

    # Счетчик сообщений
    message_count = 0

    # Скорость обновления сообщения
    # https://core.telegram.org/bots/faq#broadcasting-to-users
    every_nth_message = 50

    session = aiohttp.ClientSession()
    while True:
        try:
            wss_url = f"{config.ws_url}{Handlers.CABLE.value}?username={internal_id}"

            async with session.ws_connect(wss_url) as ws:
                ws_connections[chat_id] = ws
                logging.debug(f"WebSocket подключён для chat_id: {chat_id}")

                await ws.send_json(subscribe_message)
                await asyncio.sleep(1)
                await ws.send_json(fetch_message)

                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        if msg.data == "close":
                            await ws.close()
                        # TODO: Костыль на отсев пинга и подписки
                        if len(msg.data) > len(
                            '{"identifier":"{\\"channel\\":\\"UserChannel\\"}","message":{"kind":"room_id","room_id":1000, "assistant_room_id":1000}}'
                        ):
                            try:
                                # Валидация полученных данных
                                result = WebSocketMessage.model_validate_json(msg.data)
                            except pydantic_core._pydantic_core.ValidationError as e:
                                logging.error(
                                    "❌ Ошибка валидации данных с сервера (WebSocket)"
                                )
                                logging.error(e)
                                logging.error(msg.data)
                                if config.level == "DEBUG":
                                    await bot.send_message(
                                        chat_id=chat_id,
                                        disable_notification=True,
                                        text="❌ Ошибка валидации данных с сервера (WebSocket):"
                                        f"\n```sh\n{e}\n```\nОтвет сервера:\n```json\n{msg.data}\n```",
                                        parse_mode="markdown",
                                    )
                                continue
                            # Если пришло сообщения для текущей комнаты и текущего пользователя
                            if (
                                result.message.obj.room_id
                                == room_id  # Проверка что нужная комната
                                and result.message.obj.user.name
                                != internal_id  # Проверка что не исходящее сообщение
                            ):
                                logging.debug(
                                    f"Получено сообщение через WebSocket для chat_id {chat_id}:\n {msg.data}\n"
                                )
                                message_count += 1
                                # Если текущее сообщение нужно редактировать
                                if stream_message is not None:
                                    # Обновляем текст сообщения с новым токеном
                                    current_message_text = result.message.obj.tg_text
                                    try:
                                        if message_count % every_nth_message == 0:
                                            await bot.edit_message_text(
                                                text=current_message_text,
                                                chat_id=chat_id,
                                                message_id=stream_message.message_id,
                                            )
                                    except aiogram.exceptions.TelegramBadRequest:
                                        logging.debug("Сообщение не изменилось")
                                    # Лимит Telegram на количество изменений в минуту минус запас
                                    if (
                                        message_count >= 18
                                        and not result.message.obj.last_message
                                    ):
                                        pass
                                    # Если токен последний для сообщения
                                    if result.message.obj.last_message:
                                        await bot.edit_message_text(
                                            text=current_message_text,
                                            chat_id=chat_id,
                                            message_id=stream_message.message_id,
                                            reply_markup=kbs.votes_keyboard_markup(),
                                        )
                                        stream_message = None
                                        message_count = 0
                                else:
                                    # Пришёл первый токен сообщения
                                    answer = result.message.obj.tg_text
                                    try:
                                        stream_message = await bot.send_message(
                                            chat_id=chat_id,
                                            disable_notification=True,
                                            text=answer,
                                            parse_mode="markdown",
                                            reply_markup=kbs.votes_keyboard_markup()
                                            if result.message.obj.last_message
                                            else None,
                                        )
                                    except aiogram.exceptions.TelegramBadRequest:
                                        logging.debug(
                                            "Пришло пустое сообщение в начале."
                                        )
                                        stream_message = await bot.send_message(
                                            chat_id=chat_id,
                                            disable_notification=True,
                                            text="Ответ:\n",
                                            parse_mode="markdown",
                                        )

                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        logging.error(
                            f"❌ Подключение по WebSocket закрыто с ошибкой {ws.exception()}"
                        )
                        break
        except aiohttp.ClientError as e:
            logging.error(f"❌ Ошибка WebSocket для chat_id {chat_id}: {e}")
            await asyncio.sleep(5)
        finally:
            if chat_id in ws_connections:
                del ws_connections[chat_id]
            if not session.closed:
                await session.close()
            logging.info("✅ Все WebSocket соединения закрыты.")
