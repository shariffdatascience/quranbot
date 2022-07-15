from aiogram import types

from db import db_connection
from repository.ayats.ayat import AyatRepository
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import FavoriteAyatsNeighborRepository, NeighborAyatsRepository
from services.ayats.ayat_by_id import AyatById
from services.ayats.ayat_search import AyatFavoriteStatus, FavoriteAyats, SearchAnswer
from services.ayats.enums import AyatPaginatorCallbackDataTemplate
from services.ayats.keyboard import AyatSearchKeyboard
from services.ayats.search_by_sura_ayat_num import AyatSearchWithNeighbors
from services.regular_expression import IntableRegularExpression
from utlls import get_bot_instance

bot = get_bot_instance()


async def add_to_favorite(callback_query: types.CallbackQuery):
    """Обработчик кнопки добавления аята в избранное.

    :param callback_query: app_types.CallbackQuery
    """
    async with db_connection() as connection:
        ayat_repository = AyatRepository(connection)
        intable_ayat_id = IntableRegularExpression(r'\d+', callback_query.data)
        await AyatFavoriteStatus(
            FavoriteAyatsRepository(connection),
            intable_ayat_id,
            callback_query.from_user.id,
        ).change(is_favorite=True)
        keyboard = await AyatSearchKeyboard(
            AyatSearchWithNeighbors(
                AyatById(
                    ayat_repository,
                    intable_ayat_id,
                ),
                NeighborAyatsRepository(connection),
            ),
            FavoriteAyatsRepository(connection),
            callback_query.from_user.id,
            AyatPaginatorCallbackDataTemplate.ayat_search_template,
        ).generate()

    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=keyboard,
    )


async def remove_from_favorite(callback_query: types.CallbackQuery):
    """Обработчик кнопки удаления аята из избранного.

    :param callback_query: app_types.CallbackQuery
    """
    async with db_connection() as connection:
        ayat_repository = AyatRepository(connection)
        intable_ayat_id = IntableRegularExpression(r'\d+', callback_query.data)
        await AyatFavoriteStatus(
            FavoriteAyatsRepository(connection),
            intable_ayat_id,
            callback_query.from_user.id,
        ).change(is_favorite=False)
        keyboard = await AyatSearchKeyboard(
            AyatSearchWithNeighbors(
                AyatById(
                    ayat_repository,
                    intable_ayat_id,
                ),
                NeighborAyatsRepository(connection),
            ),
            FavoriteAyatsRepository(connection),
            callback_query.from_user.id,
            AyatPaginatorCallbackDataTemplate.ayat_search_template,
        ).generate()

    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=keyboard,
    )


async def favorite_ayat(callback_query: types.CallbackQuery):
    """Получить аят из избранного по кнопке.

    :param callback_query: app_types.CallbackQuery
    """
    async with db_connection() as connection:
        ayat_search = AyatSearchWithNeighbors(
            FavoriteAyats(
                FavoriteAyatsRepository(connection),
                callback_query.from_user.id,
                IntableRegularExpression(r'\d+', callback_query.data),
            ),
            FavoriteAyatsNeighborRepository(connection, callback_query.from_user.id),
        )
        answer = await SearchAnswer(
            ayat_search,
            AyatSearchKeyboard(
                ayat_search,
                FavoriteAyatsRepository(connection),
                callback_query.from_user.id,
                AyatPaginatorCallbackDataTemplate.favorite_ayat_template,
            ),
        ).to_answer()

    await answer.send(callback_query.from_user.id)