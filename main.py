import os
import sys

import requests
from PyQt5 import QtCore, uic
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QMessageBox

SCREEN_SIZE = [450, 450]


class MainWindow(QWidget):
    content = 0
    keyPressed = QtCore.pyqtSignal(QtCore.QEvent)
    api_key = "40d1649f-0493-4b70-98ba-98533de7710b"  # взято из учебника
    layer = "map"  # изменяя этот параметр меняем слои
    coords = [37.529887, 55.702118]  # координаты
    spn = 0.002  # изменяя это значение меняем масштаб карты
    search_success = False

    def __init__(self):
        super().__init__()
        self.initUI()
        self.search_success = False

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress:
            if source is self.search_edit or source is self.search_button or source is self.btn_map or source is self.btn_sat or source is self.btn_skl:
                if event.key() == Qt.Key_Right or event.key() == Qt.Key_Left or event.key() == Qt.Key_Down or event.key() == Qt.Key_Up:
                    self.on_key(event)
        return super(MainWindow, self).eventFilter(source, event)

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
            self.search_success = False
            self.rerun()

    def rerun(self):
        self.getImage()
        self.pixmap = QPixmap()
        self.pixmap.loadFromData(self.content)
        self.repaint()

    def map(self):
        self.layer = "map"
        self.rerun()

    def sat(self):
        self.layer = "sat"
        self.rerun()

    def skl(self):
        self.layer = "sat,skl"
        self.rerun()

    def initUI(self):
        uic.loadUi('map.ui', self)  # Загружаем дизайн
        self.setWindowTitle('Отображение карты')
        self.search_button.clicked.connect(self.search)
        self.search_edit.returnPressed.connect(self.search)
        self.keyPressed.connect(self.on_key)
        self.search_edit.installEventFilter(self)
        self.btn_map.clicked.connect(self.map)
        self.btn_sat.clicked.connect(self.sat)
        self.btn_skl.clicked.connect(self.skl)

        ## Изображение
        self.getImage()
        self.pixmap = QPixmap()
        self.pixmap.loadFromData(self.content)

        # Отключаем кнопки минимизации и разворачивания
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMinimizeButtonHint)

    def paintEvent(self, event):
        # Создаем объект QPainter для рисования
        qp = QPainter(self)
        qp.drawPixmap(0, 0, SCREEN_SIZE[0], SCREEN_SIZE[1], self.pixmap)
        if self.search_success:
            qp.setBrush(QColor(255, 0, 0))
            qp.drawEllipse(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2, 5, 5)

    def search(self):
        search_string = self.search_edit.text()
        map_request = "https://geocode-maps.yandex.ru/1.x"
        map_request += f"?apikey={self.api_key}"
        map_request += f"&geocode={search_string}"
        map_request += f"&results=1"
        map_request += f"&format=json"
        response = requests.get(map_request)
        if response.status_code == 200:
            result = response.json()
            # print(result['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'])
            # print(result)
            search_count = int(result['response']['GeoObjectCollection']['metaDataProperty']['GeocoderResponseMetaData']['found'])
            if search_count != 0:
                coords_lower = result['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['boundedBy']['Envelope']['lowerCorner']
                coords_upper = result['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['boundedBy']['Envelope']['upperCorner']
                self.coords = coords_lower.split(' ')
                for i in range(len(self.coords)):
                    self.coords[i] = float(self.coords[i])
                spn0 = abs(float(coords_upper.split(' ')[0]) - self.coords[0])
                spn1 = abs(float(coords_upper.split(' ')[1]) - self.coords[1])
                self.spn = min(spn0, spn1)
                self.coords[0] += spn0 / 2 - spn1 / 2
                self.getImage()
                self.pixmap = QPixmap()
                self.pixmap.loadFromData(self.content)
                self.search_success = True
                self.repaint()
                return

        dlg = QMessageBox(self)
        dlg.setWindowTitle("Упс..")
        dlg.setText("Не найдено")
        dlg.setStandardButtons(QMessageBox.Ok)
        dlg.setIcon(QMessageBox.Warning)
        dlg.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
