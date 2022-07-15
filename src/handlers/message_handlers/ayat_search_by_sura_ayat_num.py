from aiogram import types

from db import db_connection
from repository.ayats.ayat import AyatRepository
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import NeighborAyatsRepository
from services.ayats.ayat_search import SearchAnswer
from services.ayats.enums import AyatPaginatorCallbackDataTemplate
from services.ayats.keyboard import AyatSearchKeyboard
from services.ayats.search_by_sura_ayat_num import AyatBySuraAyatNum, AyatSearchWithNeighbors


async def ayat_search_by_sura_ayat_num_handler(message: types.Message):
    """Поиск по аятам по номеру суры и аята.

    :param message: app_types.Message
    """
    async with db_connection() as connection:
        ayat_repository = AyatRepository(connection)
        ayat_search = AyatSearchWithNeighbors(
            AyatBySuraAyatNum(
                ayat_repository,
                message.text,
            ),
            NeighborAyatsRepository(connection),
        )
        answer = await SearchAnswer(
            ayat_search,
            AyatSearchKeyboard(
                ayat_search,
                FavoriteAyatsRepository(connection),
                message.chat.id,
                AyatPaginatorCallbackDataTemplate.ayat_search_template,
            ),
        ).to_answer()
        await answer.send(message.chat.id)