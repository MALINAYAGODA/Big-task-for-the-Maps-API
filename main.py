import sys
from io import BytesIO

import requests as requests
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5 import uic  # Импортируем uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import *
from functions import find_name


# 47.152165, 56.131877
class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.map_file = "map.png"
        self.coords = (47.247691, 56.147098)
        self.points = [(47.247691, 56.147098)]
        self.delta = 0.006
        uic.loadUi('untitled.ui', self)  # Загружаем дизайн
        self.map_layer = 'map'
        self.pushButton.clicked.connect(self.run)
        self.pushButton_2.clicked.connect(self.run_2)
        self.button_group = QButtonGroup()
        self.button_group.setExclusive(False)
        self.button_group.addButton(self.radioButton)
        self.button_group.buttonClicked.connect(self.stop_ever)
        self.setImage()

    def stop_ever(self, button):
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.radioButton.setEnabled(False)

    def run_2(self):
        name, ok_pressed = QInputDialog.getText(self, "Выбор точек",
                                                "Введите название объекта")
        if ok_pressed:
            name = find_name(name).split()
            self.coords = (float(name[0]), float(name[1]))
            self.points.append(self.coords)
            self.setImage()

    def run(self):
        country, ok_pressed = QInputDialog.getItem(
            self, "Выберите слой карты", "Слой карты?",
            ('map', 'sat', 'skl'), 1, False)
        if ok_pressed:
            if country == 'map':
                self.map_layer = 'map'
            elif country == 'sat':  # не работает
                self.map_layer = 'sat'
            else:
                self.map_layer = 'skl'
            self.setImage()

    def getImage(self):

        # Собираем параметры для запроса к StaticMapsAPI:
        map_params = {
            "ll": ",".join(map(str, self.coords)),  # почему то не центр
            "spn": ",".join([str(self.delta), str(self.delta)]),
            "l": self.map_layer,
            'size': '641,441',
            'pt': "~".join([f'{i[0]},{i[1]}' for i in self.points]),
        }

        map_api_server = "http://static-maps.yandex.ru/1.x/"
        # ... и выполняем запрос
        response = requests.get(map_api_server, params=map_params)

        with open(self.map_file, "wb") as file:
            file.write(response.content)
        # return Image.open(BytesIO(
        #     response.content))

    def setImage(self):  # вызываем фото и показываем
        self.getImage()
        self.pixmap = QPixmap(self.map_file)
        self.label.setPixmap(self.pixmap)

    def keyPressEvent(self, key):
        if key.key() == Qt.Key_Space:
            for button in self.button_group.buttons():
                button.setChecked(False)
            self.pushButton.setEnabled(True)
            self.pushButton_2.setEnabled(True)
            self.radioButton.setEnabled(True)
        if key.key() == Qt.Key_Escape:
            self.close()
        if key.key() == Qt.Key_Up:  # увеличиваем размер
            self.delta += 0.01
            self.delta = round(self.delta, 3)
            self.setImage()
            print("UP", f'{self.delta=}')
        if key.key() == Qt.Key_Down:  # уменьшаем размер
            self.delta -= 0.01
            self.delta = round(max(0.001, self.delta), 3)
            self.setImage()
            print("Down", f'{self.delta=}')
            # if key.key() in (Qt.Key_W, Qt.Key_S, Qt.Key_A, Qt.Key_D):
        d = 0.0005
        if key.key() == Qt.Key_W:
            self.coords = (self.coords[0], round(self.coords[1] + d, 6))
            self.setImage()
        if key.key() == Qt.Key_S:
            self.coords = (self.coords[0], round(self.coords[1] - d, 6))
            self.setImage()
        if key.key() == Qt.Key_A:
            self.coords = (round(self.coords[0] - d, 6), self.coords[1])
            self.setImage()
        if key.key() == Qt.Key_D:
            self.coords = (round(self.coords[0] + d, 6), self.coords[1])
            self.setImage()
        print(f'{self.coords=}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
