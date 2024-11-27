from __future__ import annotations

import sqlite3

from PyQt5 import QtWidgets

from core.db import DataBase
from core.weather import WEATHER_INTERPRETATION_CODES, Weather
from ui.ui_compiled.ui_weather import Ui_MainWindow
from windows.messages import MessageBox
from windows.show_models import DataTableViewModel


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, database: DataBase):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.__database = database
        self.base_current_weather_params = [
            'temperature_2m',
            'apparent_temperature',
            'weather_code',
            ]
        self.__weather: Weather | None = None
        self.__favourite_weather_description: str | None = None
        self.__favourite_weather_phrase: str | None = None

        self.ui.city_combo.currentIndexChanged.connect(
                self.on_city_combo_change)

        self.ui.save_city_button.clicked.connect(self.on_save_city)
        self.ui.show_button.clicked.connect(self.on_show_forecast)
        self.ui.save_favourite_weather_button.clicked.connect(
                self.on_save_favourite_weather)

        self.__init_data()

    def __init_data(self) -> None:
        self.on_favourite_cities_update()
        self.on_favourite_weather_update()
        self.show_last_used_city_forecast()

    def on_city_combo_change(self) -> None:
        self.ui.city_text.setText(self.ui.city_combo.currentText())

    def show_last_used_city_forecast(self) -> None:
        last_used_city = self.__database.get_last_used_city()

        if last_used_city is None:
            return

        self.ui.city_text.setText(last_used_city)
        self.on_show_forecast()

    def on_save_city(self) -> None:
        favourite_city = self.ui.city_text.text().strip()

        try:
            _ = Weather(favourite_city)
        except Weather.ArgumentError as ex:
            MessageBox.show_warning_message(
                    title='Не удалось добавить город в любимые',
                    text=str(ex),
                    )
            return

        try:
            self.__database.add_favourite_city(favourite_city)
        except sqlite3.IntegrityError:
            MessageBox.show_warning_message(
                    title='Не удалось добавить город в любимые',
                    text=f'Город <<{favourite_city}>> уже добавлен в любимые',
                    )
            return

        MessageBox.show_information_message(
                title='Сохранено',
                text=f'Город <<{favourite_city}>> добавлен в любимые',
                )
        self.on_favourite_cities_update()

    def on_favourite_cities_update(self) -> None:
        favourite_cities = self.__database.get_all_favourite_cities()
        self.ui.city_combo.clear()
        self.ui.city_combo.addItems(favourite_cities)
        self.ui.city_combo.setCurrentIndex(0)

    def on_show_forecast(self) -> None:
        city = self.ui.city_text.text().strip()
        try:
            self.__weather = Weather(city)
        except Weather.ArgumentError as ex:
            MessageBox.show_warning_message(
                    title='Ошибка',
                    text=str(ex),
                    )
            return

        params = self.__get_weather_params()
        self.__weather.set_current_params(params)

        try:
            self.__weather.request_weather()
        except Weather.ServerError as ex:
            MessageBox.show_warning_message(
                    title='Ошибка',
                    text=str(ex),
                    )
            return

        self.show_weather()

        if (self.__weather.get_description() ==
                self.__favourite_weather_description):
            MessageBox.show_information_message(
                    title='Сообщение',
                    text=self.__favourite_weather_phrase,
                    )
            return

    def __get_weather_params(self) -> list[str]:
        params = []
        params += self.base_current_weather_params

        if self.ui.humidity_check.isChecked():
            params.append('relative_humidity_2m')

        if self.ui.precipitation_check.isChecked():
            params.append('precipitation')

        if self.ui.pressure_check.isChecked():
            params.append('pressure_msl')

        if self.ui.wind_speed_check.isChecked():
            params.append('wind_speed_10m')

        if self.ui.wind_direction_check.isChecked():
            params.append('wind_direction_10m')

        return params

    def show_weather(self) -> None:
        self.show_current_weather()
        self.show_weather_forecast()

    def show_current_weather(self) -> None:
        headers = [
            'Время',
            'Координаты',
            'Температура',
            'Ощущается как',
            'Описание',
            ]
        data = [
            self.__weather.get_day(),
            f'{self.__weather.get_coordinates()}',
            self.__weather.get_temperature(),
            self.__weather.get_apparent_temperature(),
            self.__weather.get_description(),
            ]

        if self.ui.wind_speed_check.isChecked():
            headers.append('Скорость ветра')
            data.append(self.__weather.get_wind_speed())

        if self.ui.wind_direction_check.isChecked():
            headers.append('Направление ветра')
            data.append(self.__weather.get_wind_direction())

        if self.ui.precipitation_check.isChecked():
            headers.append('Количество осадков')
            data.append(self.__weather.get_precipitation())

        if self.ui.humidity_check.isChecked():
            headers.append('Влажность')
            data.append(self.__weather.get_relative_humidity())

        if self.ui.pressure_check.isChecked():
            headers.append('Атмосферное давление')
            data.append(self.__weather.get_pressure())

        model = DataTableViewModel(data=data, headers=headers)
        self.ui.current_weather_table.setModel(model)
        self.ui.current_weather_table.setColumnWidth(0, 400)
        self.ui.current_weather_table.show()

    def show_weather_forecast(self) -> None:
        tables = [
            self.ui.next_weather_table_1,
            self.ui.next_weather_table_2,
            self.ui.next_weather_table_3,
            ]
        headers = [
            'Дата',
            'Минимальная температура',
            'Максимальная температура',
            'Описание',
            ]
        forecast = self.__weather.get_forecast()

        for table, data in zip(tables, forecast):
            model = DataTableViewModel(data=data, headers=headers)
            table.setModel(model)
            table.setColumnWidth(0, 400)
            table.show()

    def on_save_favourite_weather(self) -> None:
        if not self.ui.favourite_weather_message.text().strip():
            MessageBox.show_warning_message(
                    title='Ошибка',
                    text='Установите фразу при любимой погоде!',
                    )
            return

        self.__database.delete_favourite_weather()
        self.__database.add_favourite_weather(
                self.ui.favourite_weather_combo.currentText(),
                self.ui.favourite_weather_message.text().strip(),
                )
        MessageBox.show_information_message(
                title='Сохранено',
                text='Фраза на любимую погоду сохранена',
                )

        self.on_favourite_weather_update()

    def on_favourite_weather_update(self) -> None:
        weather_descriptions = list(WEATHER_INTERPRETATION_CODES.values())
        self.ui.favourite_weather_combo.clear()
        self.ui.favourite_weather_combo.addItems(weather_descriptions)
        self.ui.favourite_weather_combo.setCurrentIndex(0)

        favourite_weather = self.__database.get_favourite_weather()

        if favourite_weather is None:
            return

        self.__favourite_weather_description = favourite_weather[0]
        self.__favourite_weather_phrase = favourite_weather[1]

        index = weather_descriptions.index(
                self.__favourite_weather_description)
        self.ui.favourite_weather_combo.setCurrentIndex(index)
        self.ui.favourite_weather_message.setText(
                self.__favourite_weather_phrase)

    def closeEvent(self, a0):
        if not self.__weather:
            return

        last_used_city = self.__weather.get_city()
        self.__database.delete_last_used_city()
        self.__database.add_last_used_city(last_used_city)
