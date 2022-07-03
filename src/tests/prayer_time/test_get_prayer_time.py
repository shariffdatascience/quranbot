import re

import pytest

from constants import GET_PRAYER_TIMES_REGEXP
from repository.user import User
from services.prayer_time import PrayerTimes
from tests.mocks import PrayerTimeRepositoryMock, UserRepositoryMock


@pytest.fixture()
def user_repository_mock():
    return UserRepositoryMock()


@pytest.fixture(autouse=True)
def user(user_repository_mock):
    user_repository_mock.storage = [
        User(
            id=1,
            is_active=True,
            day=2,
            chat_id=444,
            city_id=1,
        ),
    ]


@pytest.mark.parametrize('input_,expect', [
    ('Время намаза', True),
    ('время намаза', True),
])
def test_regex(input_, expect):
    got = re.search(GET_PRAYER_TIMES_REGEXP, input_)

    assert bool(got) is expect


async def test(user_repository_mock):
    prayers = await PrayerTimes(
        prayer_times_repository=PrayerTimeRepositoryMock(),
        user_repository=user_repository_mock,
        chat_id=444,
    ).get()
    answer = str(prayers)

    assert isinstance(prayers, PrayerTimes)
    assert '03.01.2020' in answer.message
    assert 'Иртәнге: 01:01\n' in answer.message


# async def test_user_with_other_timezone():
#     assert False


# async def test_for_user_without_city():
#     assert False
