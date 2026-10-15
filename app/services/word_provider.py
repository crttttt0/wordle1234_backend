from __future__ import annotations

import random
from abc import ABC, abstractmethod
from functools import lru_cache
from pathlib import Path

from app.core.config import settings

WORDS_PATH = Path(__file__).resolve().parent.parent / "data" / "words_5.txt"


@lru_cache
def load_words() -> tuple[frozenset[str], tuple[str, ...]]:
    """Загрузить словарь допустимых слов из файла."""

    words: list[str] = []

    for line in WORDS_PATH.read_text(encoding="utf-8").splitlines():
        word = line.strip().lower()
        if len(word) == settings.game.WORD_LENGTH and word.isalpha():
            words.append(word)

    unique = tuple(sorted(set(words)))

    return frozenset(unique), unique


def is_valid_word(word: str) -> bool:
    """Проверить, что слово есть в словаре."""

    valid, _ = load_words()

    return word in valid


def is_valid_answer(word: str) -> bool:
    """Проверить, что слово годится в качестве ответа."""

    return (
        len(word) == settings.game.WORD_LENGTH
        and word.isalpha()
        and is_valid_word(word)
    )


class WordProvider(ABC):
    """Источник загаданного слова."""

    @abstractmethod
    async def generate_answer(self) -> str:
        """Сгенерировать слово-ответ."""

        raise NotImplementedError


class StubWordProvider(WordProvider):
    """Заглушка: берёт случайное слово из локального словаря."""

    async def generate_answer(self) -> str:
        _, answers = load_words()

        return random.choice(answers)


async def generate_valid_answer(provider: WordProvider) -> str:
    """Получить ответ от провайдера с откатом на словарь при ошибке."""

    try:
        answer = (await provider.generate_answer()).strip().lower()
    except Exception:
        answer = ""

    if is_valid_answer(answer):
        return answer

    _, answers = load_words()

    return random.choice(answers)


def create_word_provider() -> WordProvider:
    """Собрать провайдер слов согласно настройкам."""

    return StubWordProvider()
