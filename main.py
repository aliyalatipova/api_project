import os
import sys

import requests
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel

SCREEN_SIZE = [650, 450]


class MainWindow(QWidget):
    content = 0

    def __init__(self):
        super().__init__()
        self.getImage()
        self.initUI()

    def getImage(self):
        api_key = "40d1649f-0493-4b70-98ba-98533de7710b"  # взято из учебника
        layer = "map"  # изменяя этот параметр меняем слои
        coords = [37.530887, 55.703118]  # координаты
        spn = 0.002  # изменяя это значение меняем масштаб карты
        map_request = "http://static-maps.yandex.ru/1.x/"
        map_request += f"?apikey={api_key}"
        map_request += f"&ll={coords[0]},{coords[1]}"
        map_request += f"&spn={spn},{spn}"
        map_request += f"&l={layer}"
        map_request += f"&size={SCREEN_SIZE[0]},{SCREEN_SIZE[1]}"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        self.content = response.content

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        ## Изображение
        self.pixmap = QPixmap()
        self.pixmap.loadFromData(self.content)

        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(SCREEN_SIZE[0], SCREEN_SIZE[1])
        self.image.setPixmap(self.pixmap)

        # Отключаем кнопки минимизации и разворачивания
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowMaximizeButtonHint)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowMinimizeButtonHint)

    def closeEvent(self, event):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
