from __future__ import annotations

import sqlite3


class DataBase:
    def __init__(self) -> None:
        self.__connection = sqlite3.connect('db.sql')
        self.__cursor = self.__connection.cursor()

        self._create_favourite_city_table()
        self._create_last_used_city_table()
        self._create_favourite_weather_table()

    def _create_favourite_city_table(self) -> None:
        self.__cursor.execute("""
        CREATE TABLE IF NOT EXISTS favourite_city (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
        """)
        self.__connection.commit()

    def _create_last_used_city_table(self) -> None:
        self.__cursor.execute("""
        CREATE TABLE IF NOT EXISTS last_used_city (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
        """)
        self.__connection.commit()

    def _create_favourite_weather_table(self) -> None:
        self.__cursor.execute("""
        CREATE TABLE IF NOT EXISTS favourite_weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            weather TEXT NOT NULL UNIQUE,
            phrase TEXT NOT NULL
        )
        """)
        self.__connection.commit()

    def get_all_favourite_cities(self) -> list[str]:
        self.__cursor.execute('SELECT * FROM favourite_city')
        favourite_cities = self.__cursor.fetchall()

        if not favourite_cities:
            return []

        favourite_city_names = [city[1] for city in favourite_cities]
        return favourite_city_names

    def get_last_used_city(self) -> str | None:
        self.__cursor.execute('SELECT * FROM last_used_city')
        last_used_city = self.__cursor.fetchone()

        if not last_used_city:
            return None

        return last_used_city[1]

    def get_favourite_weather(self) -> tuple[str, str] | None:
        self.__cursor.execute('SELECT * FROM favourite_weather')
        favourite_weather = self.__cursor.fetchone()

        if not favourite_weather:
            return None

        return favourite_weather[1], favourite_weather[2]

    def add_favourite_city(self, city: str) -> None:
        self.__cursor.execute('INSERT INTO favourite_city(name) VALUES (?)',
                              (city,))
        self.__connection.commit()

    def add_last_used_city(self, city: str) -> None:
        self.__cursor.execute('INSERT INTO last_used_city(name) VALUES (?)',
                              (city,))
        self.__connection.commit()

    def delete_last_used_city(self) -> None:
        self.__cursor.execute('DELETE FROM last_used_city')
        self.__connection.commit()

    def add_favourite_weather(self, weather: str, phrase: str) -> None:
        self.__cursor.execute(
                'INSERT INTO favourite_weather(weather, phrase) VALUES (?, ?)',
                (weather, phrase),
                )
        self.__connection.commit()

    def delete_favourite_weather(self) -> None:
        self.__cursor.execute('DELETE FROM favourite_weather')
        self.__connection.commit()
