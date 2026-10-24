from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('StudyForge')
        self.resize(1200, 800)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        self.left_panel = QWidget()
        self.right_panel = QWidget()
        self.main_layout.addWidget(self.left_panel, 1)
        self.main_layout.addWidget(self.right_panel, 3)
        self.left_panel.setStyleSheet('background-color: black')
        self.right_panel.setStyleSheet('background-color: white')



