import qrcode
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                              QHBoxLayout)
from PyQt6.QtGui import QPixmap, QPainter, QColor, QImage
from PyQt6.QtCore import Qt


class QRCodeDialog(QDialog):
    """Диалоговое окно для отображения QR-кода"""
    
    # Ссылка на форму оценки качества работы по умолчанию
    DEFAULT_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdhZcExx6LSIXxk0ub55mSu-WIh23WYdGG9HY5EZhLDo7P8eA/viewform"
    
    def __init__(self, request_id=None, parent=None, url=None):
        super().__init__(parent)
        self.request_id = request_id
        self.qr_pixmap = None
        self.current_text = url if url else self.DEFAULT_URL
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle('Генератор QR-кода')
        self.setFixedSize(550, 600)
        
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel('Генератор QR-кода')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
                color: #4CAF50;
            }
        """)
        layout.addWidget(title)
        
        # Описание
        description = QLabel(
            'QR-код для формы оценки качества работы.\n'
            'Отсканируйте его камерой телефона.'
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666;
                padding: 10px;
            }
        """)
        layout.addWidget(description)
        
        # Область для отображения QR-кода
        self.qr_image_label = QLabel()
        self.qr_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_image_label.setMinimumHeight(400)
        self.qr_image_label.setStyleSheet("""
            QLabel {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
        
        # Генерация QR-кода
        self.qr_pixmap = self.generate_qr_code(self.current_text)
        self.qr_image_label.setPixmap(self.qr_pixmap)
        
        layout.addWidget(self.qr_image_label)
        
        # Информация о заявке (если есть)
        if self.request_id:
            info = QLabel(f'Заявка № {self.request_id}')
            info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            info.setStyleSheet("""
                QLabel {
                    font-size: 10px;
                    color: #999;
                    padding: 5px;
                }
            """)
            layout.addWidget(info)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton('Сохранить QR-код')
        save_btn.clicked.connect(self.save_qr_code)
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        
        close_btn = QPushButton('Закрыть')
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #9E9E9E;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def generate_qr_code(self, data: str) -> QPixmap:
        """
        Генерация QR-кода из переданного текста
        Использует ручную отрисовку через QPainter без PIL
        
        Args:
            data: текст или ссылка для кодирования
        
        Returns:
            QPixmap с изображением QR-кода
        """
        # Создаем QR-код
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Получаем матрицу модулей QR-кода
        matrix = qr.get_matrix()
        
        # Размеры
        module_count = len(matrix)
        box_size = 10
        border = 4
        image_size = (module_count + border * 2) * box_size
        
        # Создаем изображение через Qt
        image = QImage(image_size, image_size, QImage.Format.Format_RGB32)
        image.fill(QColor(255, 255, 255))  # Белый фон
        
        painter = QPainter(image)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0))  # Черный цвет для модулей
        
        # Рисуем каждый модуль QR-кода
        for row_idx, row in enumerate(matrix):
            for col_idx, module in enumerate(row):
                if module:  # Если модуль черный
                    x = (col_idx + border) * box_size
                    y = (row_idx + border) * box_size
                    painter.drawRect(x, y, box_size, box_size)
        
        painter.end()
        
        # Масштабируем до нужного размера
        pixmap = QPixmap.fromImage(image)
        return pixmap.scaled(380, 380, Qt.AspectRatioMode.KeepAspectRatio, 
                            Qt.TransformationMode.SmoothTransformation)
    
    def save_qr_code(self):
        """Сохранение QR-кода в файл"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        
        if not self.current_text:
            QMessageBox.warning(self, 'Предупреждение', 'QR-код не найден')
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить QR-код",
            f"qr_code_{self.request_id if self.request_id else 'quality_form'}.png",
            "PNG файлы (*.png);;Все файлы (*.*)"
        )
        
        if filename:
            try:
                # Генерируем QR-код заново для сохранения в высоком качестве
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_H,
                    box_size=10,
                    border=4,
                )
                qr.add_data(self.current_text)
                qr.make(fit=True)
                
                matrix = qr.get_matrix()
                module_count = len(matrix)
                box_size = 10
                border = 4
                image_size = (module_count + border * 2) * box_size
                
                image = QImage(image_size, image_size, QImage.Format.Format_RGB32)
                image.fill(QColor(255, 255, 255))
                
                painter = QPainter(image)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(0, 0, 0))
                
                for row_idx, row in enumerate(matrix):
                    for col_idx, module in enumerate(row):
                        if module:
                            x = (col_idx + border) * box_size
                            y = (row_idx + border) * box_size
                            painter.drawRect(x, y, box_size, box_size)
                
                painter.end()
                
                # Сохраняем в файл
                if image.save(filename, "PNG"):
                    QMessageBox.information(
                        self,
                        'Успешно',
                        f'QR-код сохранён в файл:\n{filename}'
                    )
                else:
                    raise Exception("Не удалось сохранить изображение")
                    
            except Exception as e:
                QMessageBox.critical(
                    self,
                    'Ошибка',
                    f'Не удалось сохранить QR-код:\n{str(e)}'
                )


def generate_qr_code_file(text: str, filename: str = 'qr_code.png') -> bool:
    """
    Генерация QR-кода и сохранение в файл (без GUI)
    
    Args:
        text: текст или ссылка для кодирования
        filename: имя файла для сохранения
    
    Returns:
        bool: True если успешно, False при ошибке
    """
    try:
        from PyQt6.QtGui import QPainter, QColor, QImage
        from PyQt6.QtCore import Qt
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        
        matrix = qr.get_matrix()
        module_count = len(matrix)
        box_size = 10
        border = 4
        image_size = (module_count + border * 2) * box_size
        
        image = QImage(image_size, image_size, QImage.Format.Format_RGB32)
        image.fill(QColor(255, 255, 255))
        
        painter = QPainter(image)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0))
        
        for row_idx, row in enumerate(matrix):
            for col_idx, module in enumerate(row):
                if module:
                    x = (col_idx + border) * box_size
                    y = (row_idx + border) * box_size
                    painter.drawRect(x, y, box_size, box_size)
        
        painter.end()
        
        if image.save(filename, "PNG"):
            print(f"QR-код успешно сохранён в файл: {filename}")
            return True
        else:
            print("Не удалось сохранить QR-код")
            return False
        
    except Exception as e:
        print(f"Ошибка при генерации QR-кода: {e}")
        return False


# Пример использования
if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Показываем диалог с QR-кодом
    dialog = QRCodeDialog(request_id=123)
    dialog.exec()
    
    sys.exit()