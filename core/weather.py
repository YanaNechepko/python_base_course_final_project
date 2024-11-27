import requests

from fake_useragent import UserAgent
from geopy.geocoders import Nominatim

WEATHER_INTERPRETATION_CODES = {
    0: 'Ясно',
    1: 'В основном ясно',
    2: 'Переменная облачность',
    3: 'Облачно',
    45: 'Туман',
    48: 'Туман с изморозью',
    51: 'Слабая морось',
    53: 'Умеренная морось',
    55: 'Сильная морось',
    56: 'Слабая ледяная морось',
    57: 'Сильная ледяная морось',
    61: 'Слабый дождь',
    63: 'Умеренный дождь',
    65: 'Сильный дождь',
    66: 'Слабый ледяной дождь',
    67: 'Сильный ледяной дождь',
    71: 'Слабый снегопад',
    73: 'Умеренный снегопад',
    75: 'Сильный снегопад',
    77: 'Град',
    80: 'Слабый ливень',
    81: 'Умеренный ливень',
    83: 'Сильный ливень',
    85: 'Слабый дождь со снегом',
    86: 'Сильный дождь со снегом',
    95: 'Гроза',
    96: 'Гроза с небольшим градом',
    99: 'Гроза с сильным градом',
    }

MONTH_INTERPRETATION_CODES = {
    '01': 'Янв',
    '02': 'Фев',
    '03': 'Мар',
    '04': 'Апр',
    '05': 'Мая',
    '06': 'Июн',
    '07': 'Июл',
    '08': 'Авг',
    '09': 'Сен',
    '11': 'Ноя',
    '12': 'Дек',
    }


class Weather:
    """Класс, описывающий погоду."""

    class ServerError(Exception):
        """Класс, описывающий ошибку при получении ответа от сервера."""
        pass

    class ArgumentError(Exception):
        """Класс, описывающий ошибку при получении координат города."""
        pass

    URL = 'https://api.open-meteo.com/v1/forecast'

    def __init__(self, city: str) -> None:
        """Устанавливает атрибуты для объекта Weather.

        Args:
            city: Название города.
        """

        self.__city = city

        latitude, longitude = self.__get_geolocation()
        self.__params = {
            'latitude': latitude,
            'longitude': longitude,
            'timezone': 'auto',
            'forecast_days': 4,
            'wind_speed_unit': 'ms',
            'daily': [
                'weather_code',
                'temperature_2m_max',
                'temperature_2m_min',
                ],
            'current': [],
            }

        self.__current_params = []
        self.__last_result = None

    def get_city(self) -> str:
        """Получает текущий город.

        Returns:
            Возвращает текущий город.
        """
        return self.__city

    @staticmethod
    def __get_fake_user_agent() -> str:
        """Имитирует запрос от браузера.

        Returns:
            Возвращает сымитированного юзер агента.
        """
        user_agent = UserAgent()
        random_user_agent = user_agent.random
        return random_user_agent

    def __get_geolocation(self) -> tuple[float, float]:
        """Получает координаты города.

        Returns:
            Возвращает широту и долготу.
        """
        geolocator = Nominatim(user_agent=self.__get_fake_user_agent())
        location = geolocator.geocode(self.__city)

        if location is None:
            error_message = 'Такого города не найдено!'
            raise self.ArgumentError(error_message)

        return location.latitude, location.longitude

    def set_current_params(self, params: list[str]) -> None:
        """Устанавливает требуемые параметры текущей погоды.

        Args:
            params: Параметры.
        """
        self.__current_params = params

    def request_weather(self) -> None:
        """Получает и сохраняет ответ от сервера."""
        for param in self.__current_params:
            self.__params['current'].append(param)

        response = requests.get(self.URL, params=self.__params)

        if response.status_code != 200:
            error_message = 'Не удалось получить ответ от сервера'
            raise self.ServerError(error_message)

        self.__last_result = response.json()

    def get_forecast(self) -> list[tuple[str, str, str, str]]:
        """Получает прогноз погоды.

        Returns:
            Возвращает прогноз погоды на ближайшие 3 дня.
        """
        forecast = []
        for date, temperature_2m_min, temperature_2m_max, weather_code in zip(
                self.__last_result['daily']['time'],
                self.__last_result['daily']['temperature_2m_min'],
                self.__last_result['daily']['temperature_2m_max'],
                self.__last_result['daily']['weather_code'],
                ):
            day = self.__get_day(date)
            min_temp = str(round(temperature_2m_min))
            max_temp = str(round(temperature_2m_max))
            description = WEATHER_INTERPRETATION_CODES[weather_code]
            forecast.append((day, min_temp, max_temp, description))

        return forecast[1:]

    def get_day(self) -> str:
        """Получает текущую дату.

        Returns:
            Возвращает текущую дату.
        """
        datetime = self.__last_result['current']['time']
        datetime = datetime.split('T')

        day = self.__get_day(datetime[0])
        time = datetime[1]
        return f'{day} {time}'

    @staticmethod
    def __get_day(date: str) -> str:
        """Форматирует вывод текущей даты.

        Args:
            date: Дата.

        Returns:
            Возвращает дату в формате: 25 Ноя.
        """
        parts = date.split('-')
        return f'{parts[2]} {MONTH_INTERPRETATION_CODES[parts[1]]}'

    def get_coordinates(self) -> tuple[str, str]:
        """Получает координаты города.

        Returns:
            Возвращет координаты города.
        """
        latitude, longitude = (str(self.__last_result['latitude']),
                               str(self.__last_result['longitude']))
        return latitude, longitude

    def get_temperature(self) -> str:
        """Получает текущую температуру.

        Returns:
            Возвращет текущую температуру.
        """
        temperature = round(self.__last_result['current']['temperature_2m'])
        return f'{temperature}°C'

    def get_relative_humidity(self) -> str:
        """Получает текущую влажность.

        Returns:
            Возвращет текущую влажность.
        """
        relative_humidity = (
            self.__last_result['current']['relative_humidity_2m'])
        return f'{relative_humidity}%'

    def get_apparent_temperature(self) -> str:
        """Получает ощущаемую температуру.

        Returns:
            Возвращает ощущаемую температуру.
        """
        apparent_temperature = round(self.__last_result['current']
                                     ['apparent_temperature'])
        return f'{apparent_temperature}°C'

    def get_precipitation(self) -> str:
        """Получает текущую влажность.

        Returns:
            Возвращает текущую влажность.
        """
        precipitation = round(self.__last_result['current']['precipitation'])
        return f'{precipitation} мм'

    def get_description(self) -> str:
        """Переводит кодировку погодных условий в текст.

        Returns:
            Возвращает погодные условия.
        """
        weather_code = round(self.__last_result['current']['weather_code'])
        description = WEATHER_INTERPRETATION_CODES[weather_code]
        return f'{description}'

    def get_pressure(self) -> str:
        """Получает текущее давление.

        Returns:
            Возвращает текущее давление.
        """
        pressure_in_hpa = self.__last_result['current']['pressure_msl']
        pressure_in_mm = round(pressure_in_hpa * 0.7501)
        return f'{pressure_in_mm} мм рт. ст.'

    def get_wind_speed(self) -> str:
        """Получает текущую скорость ветра.

        Returns:
            Возвращает текущую скорость ветра.
        """
        wind_speed = self.__last_result['current']['wind_speed_10m']
        return f'{wind_speed} м/с'

    def get_wind_direction(self) -> str:
        """Получает направление ветра.

        Returns:
            Возвращает направление ветра.
        """
        wind_direction = self.__last_result['current']['wind_direction_10m']

        if wind_direction >= 337.5 or wind_direction <= 22.5:
            return 'С'

        if 22.5 < wind_direction < 67.5:
            return 'СВ'

        if 67.5 <= wind_direction <= 112.5:
            return 'В'

        if 112.5 < wind_direction < 157.5:
            return 'ЮВ'

        if 157.5 <= wind_direction <= 202.5:
            return 'Ю'

        if 202.5 < wind_direction < 247.5:
            return 'ЮЗ'

        if 247.5 <= wind_direction <= 292.5:
            return 'З'

        if 292.5 < wind_direction < 337.5:
            return 'СЗ'
