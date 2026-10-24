from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QInputDialog,
    QListWidget,
    QFileDialog
)


# класс основного окна
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # путь к текущему рабочему пространству
        # None означает, что пользователь пока не выбрал папку
        self.workspace_path = None

        self._setup_window()
        self._setup_main_layout()
        self._setup_sidebar()

    # настройки основного окна
    def _setup_window(self):
        self.setWindowTitle("StudyForge")
        self.resize(1200, 800)

    # создание центральной области и основного layout
    def _setup_main_layout(self):
        # центральный widget окна
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # layout внутри central_widget
        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        # widget'ы для двух панелей (левой и правой) внутри main_layout
        self.left_panel = QWidget()
        self.right_panel = QWidget()

        self.main_layout.addWidget(self.left_panel, 1)
        self.main_layout.addWidget(self.right_panel, 3)

        self.left_panel.setStyleSheet("background-color: white")
        self.right_panel.setStyleSheet("background-color: gray")

    # настройки sidebar (layout внутри left_panel)
    def _setup_sidebar(self):
        self.sidebar_layout = QVBoxLayout()
        self.left_panel.setLayout(self.sidebar_layout)

        # отображение текущего рабочего пространства
        self.workspace_path_label = QLabel("Пространство не выбрано")
        self.sidebar_layout.addWidget(self.workspace_path_label)

        # кнопка выбора рабочего пространства
        self.open_workspace_button = QPushButton("Открыть пространство")
        self.open_workspace_button.clicked.connect(self._open_workspace)
        self.sidebar_layout.addWidget(self.open_workspace_button)

        self.sidebar_title = QLabel("Предметы")
        self.sidebar_layout.addWidget(self.sidebar_title)

        self.subject_list = QListWidget()
        self.sidebar_layout.addWidget(self.subject_list)

        self.add_subject_button = QPushButton("Добавить предмет")
        self.add_subject_button.clicked.connect(self._add_subject)
        self.sidebar_layout.addWidget(self.add_subject_button)

    # выбор рабочего пространства
    def _open_workspace(self):
        path = QFileDialog.getExistingDirectory(
            self,
            "Выберите учебное пространство",
            ""
        )

        if path:
            self.workspace_path = Path(path)
            self.workspace_path_label.setText(path)
            self._load_subjects()

    # добавление нового предмета
    def _add_subject(self):
        name, ok = QInputDialog.getText(
            self,
            "Добавление предмета",
            "Название предмета:"
        )

        name = name.strip()

        if ok and name:
            self.subject_list.addItem(name)
        else:
            print(f':( ok = {ok}, name = "{name}"')

    # загрузка предметов из папок рабочего пространства
    def _load_subjects(self):
        self.subject_list.clear()
        for item in self.workspace_path.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                self.subject_list.addItem(item.name)
