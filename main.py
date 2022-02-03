import os
import sys

import requests
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel

SCREEN_SIZE = [450, 450]


class MainWindow(QWidget):
    content = 0
    keyPressed = QtCore.pyqtSignal(QtCore.QEvent)
    api_key = "40d1649f-0493-4b70-98ba-98533de7710b"  # взято из учебника
    layer = "map"  # изменяя этот параметр меняем слои
    coords = [37.529887, 55.702118]  # координаты
    spn = 0.002  # изменяя это значение меняем масштаб карты

    def __init__(self):
        super().__init__()
        self.initUI()
        self.keyPressed.connect(self.on_key)

    def getImage(self):
        map_request = "http://static-maps.yandex.ru/1.x/"
        map_request += f"?apikey={self.api_key}"
        # map_request += f"&ll={self.coords[0]},{self.coords[1]}"
        # map_request += f"&spn={self.spn},{self.spn}"
        map_request += f"&bbox={self.coords[0]},{self.coords[1]}~{self.coords[0] + self.spn},{self.coords[1] + self.spn}"
        map_request += f"&l={self.layer}"
        map_request += f"&size={SCREEN_SIZE[0]},{SCREEN_SIZE[1]}"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        self.content = response.content

    def keyPressEvent(self, event):
        super(MainWindow, self).keyPressEvent(event)
        self.keyPressed.emit(event)

    def on_key(self, event):
        print(event.key())
        pressed = False
        if event.key() == Qt.Key_Up:
            pressed = True
            self.coords[1] += self.spn * 2
        elif event.key() == Qt.Key_Down:
            pressed = True
            self.coords[1] -= self.spn * 2
        elif event.key() == Qt.Key_Left:
            pressed = True
            self.coords[0] -= self.spn * 2
        elif event.key() == Qt.Key_Right:
            pressed = True
            self.coords[0] += self.spn * 2
        # перезагрузим картинку и перерисуем
        if pressed:
            self.getImage()
            self.pixmap = QPixmap()
            self.pixmap.loadFromData(self.content)
            self.image.setPixmap(self.pixmap)

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        ## Изображение
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(SCREEN_SIZE[0], SCREEN_SIZE[1])
        self.getImage()
        self.pixmap = QPixmap()
        self.pixmap.loadFromData(self.content)
        self.image.setPixmap(self.pixmap)

        # Отключаем кнопки минимизации и разворачивания
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMinimizeButtonHint)

    def closeEvent(self, event):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
