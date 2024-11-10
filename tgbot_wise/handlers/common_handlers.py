import asyncio
from datetime import datetime
import logging

from aiogram import F, Router, html
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender
from aiogram.utils.formatting import Text, as_list, as_marked_section
from sqlmodel import Session, select
from database.schemas import User

from bot_connections.api.requests import create_message
from bot_connections.sockets.sockets import websocket_listener, ws_connections
from keyboards import common_keyboards as kbs

from config import config

router = Router()


@router.message(
    CommandStart(deep_link=True),
)
async def command_start_chat_from_web(
    message: Message, command: CommandObject, db_engine
) -> None:
    """
    Хэндлер для обработки перехода с сайта.

    Args:
        message (Message): сообщение пользователя
        command (CommandObject): уникальный ID пользователя в системе
        chat_info (dict): словарь для хранения ID пользователя в системе и Telegram
    """
    answer = f"Здравствуйте, {html.bold(message.from_user.full_name)}!\n"
    user_id = command.args
    answer += f"Ваш ID: {html.code(user_id)}\n"
    answer += "Вы можете продолжить общение в чате, история ваших сообщений сохранена."
    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        with Session(db_engine) as session:
            await message.answer(answer)

            db_user = session.exec(select(User).where(User.tg_id == user_id)).first()

            # Если пользователь первый раз зашёл в бота
            if db_user is None:
                logging.debug("Пользователя нет в БД. Создаём...")

                api_message = await create_message(
                    user_id=None,
                    room_id=None,
                    message_text=None,
                    is_admin=config.default_admin_view,
                )
                # Если пришло сообщение об ошибке
                if isinstance(api_message, str):
                    await message.answer(api_message)
                # Иначе пишем в чат ID комнаты при дебаг режиме
                else:
                    if config.level in ["DEBUG", "INFO"]:
                        mode_info = (
                            f"{html.bold("Вы находитесь в режиме оператора-админа")} (для теста).\n"
                            + "Ваш запрос будет обработан ИИ без участия человека."
                            + "Если хотите переключиться на режим обычного пользователя, "
                            + "воспользуйтесь меню бота и выберете «Пользователь».\n"
                        )
                        room_str = f"ID Вашей комнаты: {api_message.room_id}"
                        await message.answer(
                            mode_info + room_str,
                            reply_markup=kbs.start_keyboard_markup(
                                config.default_admin_view
                            ),
                        )
                room_id = api_message.room_id
                internal_id = api_message.user.name

                session.add(
                    User(
                        tg_id=message.from_user.id,
                        tg_chat_id=message.chat.id,
                        tg_username=message.from_user.username,
                        tg_fullname=message.from_user.full_name,
                        tg_is_user_admin=config.default_admin_view,
                        internal_room_id=room_id,
                        internal_username=internal_id,
                    )
                )
                session.commit()
            else:
                logging.debug(f"Пользователь с ID {db_user.tg_id} есть в базе")
                room_id = db_user.internal_room_id
                internal_id = db_user.internal_username
                if config.level == "DEBUG":
                    await message.answer(
                        f"ID Вашей комнаты: {db_user.internal_room_id}",
                        reply_markup=kbs.start_keyboard_markup(
                            db_user.tg_is_user_admin
                        ),
                    )

            await asyncio.sleep(1)
            # Поднимаем WebSocket для общения с беком
            if message.chat.id not in ws_connections:
                # Запуск нового WebSocket для этого chat_id
                asyncio.create_task(
                    websocket_listener(
                        message.bot,
                        message.chat.id,
                        internal_id,
                        room_id,
                    )
                )


@router.message(CommandStart())
async def command_start_handler(message: Message, db_engine) -> None:
    """
    Хэндлер для обработки стандартной команды /start.

    Args:
        message (Message): сообщение пользователя с командой
    """
    answer = f"Здравствуйте, {html.bold(message.from_user.full_name)}!\n"
    answer += "Напишите в чат свой запрос, я постараюсь на него ответить."
    # Состояние бота, что он печатает в чат
    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        with Session(db_engine) as session:
            await message.answer(answer)

            db_user = session.exec(
                select(User).where(User.tg_id == message.from_user.id)
            ).first()

            # Если пользователь первый раз зашёл в бота
            if db_user is None:
                logging.debug("Пользователя нет в БД. Создаём...")

                api_message = await create_message(
                    user_id=None,
                    room_id=None,
                    message_text=None,
                    is_admin=config.default_admin_view,
                )
                # Если пришло сообщение об ошибке
                if isinstance(api_message, str):
                    await message.answer(api_message)
                # Иначе пишем в чат ID комнаты при дебаг режиме
                else:
                    if config.level in ["DEBUG", "INFO"]:
                        mode_info = (
                            f"{html.bold("Вы находитесь в режиме оператора-админа")} (для теста).\n"
                            + "Ваш запрос будет обработан ИИ без участия человека."
                            + "Если хотите переключиться на режим обычного пользователя, "
                            + "воспользуйтесь меню бота и выберете «Пользователь».\n"
                        )
                        room_str = f"ID Вашей комнаты: {api_message.room_id}"
                        await message.answer(
                            mode_info + room_str,
                            reply_markup=kbs.start_keyboard_markup(
                                config.default_admin_view
                            ),
                        )
                room_id = api_message.room_id
                internal_id = api_message.user.name

                session.add(
                    User(
                        tg_id=message.from_user.id,
                        tg_chat_id=message.chat.id,
                        tg_username=message.from_user.username,
                        tg_fullname=message.from_user.full_name,
                        tg_is_user_admin=config.default_admin_view,
                        internal_room_id=room_id,
                        internal_username=internal_id,
                    )
                )
                session.commit()
            else:
                logging.debug(f"Пользователь с ID {db_user.tg_id} есть в базе")
                room_id = db_user.internal_room_id
                internal_id = db_user.internal_username
                if config.level == "DEBUG":
                    await message.answer(
                        f"ID Вашей комнаты: {db_user.internal_room_id}",
                        reply_markup=kbs.start_keyboard_markup(
                            db_user.tg_is_user_admin
                        ),
                    )

            await asyncio.sleep(1)
            # Поднимаем WebSocket для общения с беком
            if message.chat.id not in ws_connections:
                # Запуск нового WebSocket для этого chat_id
                asyncio.create_task(
                    websocket_listener(
                        message.bot,
                        message.chat.id,
                        internal_id,
                        room_id,
                    )
                )


@router.message(F.text == "🌍 Перейти на сайт")
async def go_to_web_btn_handler(message: Message) -> None:
    """
    Хэндлер для отправки ссылки на web чат.

    Args:
        message (Message): сообщения пользователя
    """
    await message.reply(
        "Хорошо! Нажмите на кнопку ниже👇\nЧат автоматически перенесётся",
        reply_markup=kbs.go_to_web_keyboard_markup(),
    )


@router.message(F.text == "🤖 О боте")
async def about_bot_btn_handler(message: Message) -> None:
    """
    Хэндлер для вывода справки о боте.

    Args:
        message (Message): сообщения пользователя
    """
    await message.reply(
        "Я бот для поиска информации и источников в агентской библиотеке материалов!"
    )


@router.message(F.text.in_({"👤 Режим пользователя", "⚠️ Режим админа"}))
async def enable_user_mode_btn_handler(message: Message, db_engine) -> None:
    """
    Хэндлер для включения режима пользователя.

    Args:
        message (Message): сообщения пользователя
    """
    with Session(db_engine) as session:
        db_user = session.exec(
            select(User).where(User.tg_id == message.from_user.id)
        ).first()

        if db_user is None:
            await message.answer(
                f"{html.bold("❌ Что-то пошло не так.")}\n"
                + "Отправьте /start для переподключения к системе."
            )

        if db_user.tg_is_user_admin:
            await message.reply(
                "Теперь Вы обычный пользователь!",
                reply_markup=kbs.keyboard_remove(),
            )
            await message.reply(
                "Вы можете изменить режим в любое время.",
                reply_markup=kbs.start_keyboard_markup(is_admin=False),
            )
        else:
            await message.reply(
                "Теперь Вы админ!",
                reply_markup=kbs.keyboard_remove(),
            )
            await message.reply(
                "Вы можете изменить режим в любое время.",
                reply_markup=kbs.start_keyboard_markup(is_admin=True),
            )

        db_user.tg_is_user_admin = not db_user.tg_is_user_admin
        session.add(db_user)
        session.commit()


@router.callback_query(F.data == "voted_up")
async def thumb_up_btn_handler(message: Message) -> None:
    """
    Callback для обработки нажатия лайка.

    Args:
        message (Message): сообщения пользователя
    """
    # TODO: отправка на бек
    await message.answer("Спасибо за оценку!")


@router.callback_query(F.data == "voted_down")
async def thumb_down_btn_handler(message: Message) -> None:
    """
    Callback для обработки нажатия дизлайка.

    Args:
        message (Message): сообщения пользователя
    """
    # TODO: отправка на бек
    await message.answer("Спасибо за оценку! Будем улучшать качество ответов!")


@router.message(Command("info", prefix="!"))
async def info_handler(message: Message, system_info: dict) -> None:
    """
    Системный хэндлер для вывода технической информации о боте.

    Args:
        message (Message): сообщение с командой
        system_info (dict): информация о боте
    """
    content = as_list(
        as_marked_section(
            Text(html.bold("Общая информация")),
            f"🚀 Запуск: {system_info["started_at"]}",
            marker=" ",
        ),
        Text(f"Информация на {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}"),
        sep="\n\n",
    )
    await message.answer(**content.as_kwargs(parse_mode_key="html"))


@router.message(
    F.content_type.in_(
        {
            "photo",
            "sticker",
            "animation",
            "document",
            "story",
            "audio",
            "video",
            "voice",
        }
    )
)
async def message_with_another_type_content_handler(message: Message) -> None:
    """
    Хэндлер для обработки присланных изображений.

    Args:
        message (Message): сообщения пользователя
    """
    answer = f"{html.bold('K P A C U B O !')}✨\n"
    answer += "Но я умею обрабатывать только текстовые вопросы 👉👈😬"
    await message.answer(answer)


@router.message(F.text)
async def message_handler(message: Message, db_engine) -> None:
    """
    Хэндлер для обработки присланных текстовых сообщений.

    Args:
        message (Message): сообщения пользователя
    """
    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        if message.chat.id in ws_connections:
            # Отправка сообщения через WebSocket
            await ws_connections[message.chat.id].send_str(message.text)
            logging.debug(
                f"Сообщение от пользователя {message.from_user.id} "
                '(@{message.from_user.username}): "{message.text}".'
            )
            with Session(db_engine) as session:
                db_user = session.exec(
                    select(User).where(User.tg_id == message.from_user.id)
                ).first()

                if db_user is None:
                    await message.answer(
                        f"{html.bold("❌ Что-то пошло не так.")}\n"
                        + "Отправьте /start для переподключения к системе."
                    )
        else:
            with Session(db_engine) as session:
                db_user = session.exec(
                    select(User).where(User.tg_id == message.from_user.id)
                ).first()

                if db_user is None:
                    await message.answer(
                        f"{html.bold("❌ Соединение с системой не установлено.")}\n"
                        + "Отправьте /start для переподключения."
                    )
                else:
                    # Запуск нового WebSocket для этого chat_id
                    asyncio.create_task(
                        websocket_listener(
                            message.bot,
                            db_user.tg_id,
                            db_user.internal_username,
                            db_user.internal_room_id,
                        )
                    )
                    room_str = (
                        "Сессия восстановлена.\n"
                        + f"ID Вашей комнаты: {db_user.internal_room_id}"
                    )
                    await message.answer(room_str)

                    asyncio.sleep(1)

        await create_message(
            user_id=db_user.internal_username,
            room_id=db_user.internal_room_id,
            message_text=message.text,
            is_admin=db_user.tg_is_user_admin,
        )
