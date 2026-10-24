from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QTreeView,
    QFileSystemModel
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


        self.file_system_model = QFileSystemModel()
        self.file_tree = QTreeView()
        self.file_tree.setModel(self.file_system_model)
        self.file_tree.hideColumn(1)
        self.file_tree.hideColumn(2)
        self.file_tree.hideColumn(3)

        self.file_tree.setHeaderHidden(True)

        self.sidebar_layout.addWidget(self.file_tree)


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

            self.file_system_model.setRootPath(path)

            root_index = self.file_system_model.index(path)
            self.file_tree.setRootIndex(root_index)

