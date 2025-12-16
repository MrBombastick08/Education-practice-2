import qrcode
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from io import BytesIO

class QRCodeDialog(QDialog):
    """Диалоговое окно для отображения QR-кода"""
    
    # Ссылка на форму оценки качества работы
    FEEDBACK_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdhZcExx6LSIXxk0ub55mSu-WIh23WYdGG9HY5EZhLDo7P8eA/viewform"
    
    def __init__(self, request_id=None, parent=None):
        super().__init__(parent)
        self.request_id = request_id
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle('QR-код для оценки качества работы')
        self.setFixedSize(500, 600)
        
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel('📱 Отсканируйте QR-код для оценки качества')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                color: #4CAF50;
            }
        """)
        layout.addWidget(title)
        
        # Описание
        description = QLabel(
            'Пожалуйста, отсканируйте QR-код с помощью камеры телефона\n'
            'и оставьте отзыв о качестве выполненных работ.'
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
        
        # Генерация и отображение QR-кода
        qr_image_label = QLabel()
        qr_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        qr_pixmap = self.generate_qr_code()
        qr_image_label.setPixmap(qr_pixmap)
        
        layout.addWidget(qr_image_label)
        
        # Ссылка текстом (на случай, если QR-код не работает)
        link_label = QLabel(f'<a href="{self.FEEDBACK_URL}">Открыть форму напрямую</a>')
        link_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        link_label.setOpenExternalLinks(True)
        link_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                padding: 10px;
            }
        """)
        layout.addWidget(link_label)
        
        # Информация о заявке
        if self.request_id:
            info = QLabel(f'Заявка №{self.request_id}')
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
        
        save_btn = QPushButton('💾 Сохранить QR-код')
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
    
    def generate_qr_code(self) -> QPixmap:
        """
        Генерация QR-кода с ссылкой на форму оценки
        
        Returns:
            QPixmap с изображением QR-кода
        """
        # Создаём URL с параметром заявки (если есть)
        url = self.FEEDBACK_URL
        if self.request_id:
            url += f"?entry.request_id={self.request_id}"
        
        # Генерация QR-кода
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        # Создание изображения
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Конвертация в QPixmap для отображения в PyQt6
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        qimage = QImage()
        qimage.loadFromData(buffer.read())
        
        pixmap = QPixmap.fromImage(qimage)
        
        # Масштабирование для удобного отображения
        scaled_pixmap = pixmap.scaled(
            350, 350, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        
        return scaled_pixmap
    
    def save_qr_code(self):
        """Сохранение QR-кода в файл"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить QR-код",
            f"qr_feedback_{self.request_id if self.request_id else 'general'}.png",
            "PNG файлы (*.png);;Все файлы (*.*)"
        )
        
        if filename:
            # Создаём URL
            url = self.FEEDBACK_URL
            if self.request_id:
                url += f"?entry.request_id={self.request_id}"
            
            # Генерируем QR-код
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            try:
                img.save(filename)
                QMessageBox.information(
                    self,
                    'Успешно',
                    f'QR-код сохранён в файл:\n{filename}'
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    'Ошибка',
                    f'Не удалось сохранить QR-код:\n{str(e)}'
                )


def generate_qr_code_file(request_id=None, filename='qr_feedback.png'):
    """
    Генерация QR-кода и сохранение в файл (без GUI)
    
    Args:
        request_id: ID заявки (опционально)
        filename: имя файла для сохранения
    
    Returns:
        bool: True если успешно, False при ошибке
    """
    try:
        url = QRCodeDialog.FEEDBACK_URL
        if request_id:
            url += f"?entry.request_id={request_id}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filename)
        
        print(f"✅ QR-код успешно сохранён в файл: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при генерации QR-кода: {e}")
        return False


# Пример использования
if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Показываем диалог с QR-кодом
    dialog = QRCodeDialog(request_id=123)
    dialog.exec()
    
    # Или генерируем файл напрямую
    generate_qr_code_file(request_id=456, filename='feedback_qr.png')
    
    sys.exit()