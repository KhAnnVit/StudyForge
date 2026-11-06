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
    QFileSystemModel,
    QPlainTextEdit,
    QTabWidget
)


# класс основного окна
class MainWindow(QMainWindow):
    # конструктор. вызывется при создании окна
    def __init__(self):
        #инициализируется родительский QMainWindow
        super().__init__()

        # путь к текущему рабочему пространству
        # None означает, что пользователь пока не выбрал папку
        self.workspace_path = None

        self.opened_files = dict()

        # вызываются методы настройки, которые ниже в этом классе. нужны чтобы разделить логику, а не делать огромный конструктор
        self._setup_window()
        self._setup_main_layout()
        self._setup_sidebar()
        self._setup_right_panel()

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

        self.file_tree.clicked.connect(self._on_file_clicked)

        self.file_tree.hideColumn(1)
        self.file_tree.hideColumn(2)
        self.file_tree.hideColumn(3)

        self.file_tree.setHeaderHidden(True)

        self.sidebar_layout.addWidget(self.file_tree)

    # настройка правой панели
    def _setup_right_panel(self):
        self.right_layout = QVBoxLayout()
        self.right_panel.setLayout(self.right_layout)

        self.right_panel_tab_widget = QTabWidget()
        self.right_layout.addWidget(self.right_panel_tab_widget)
        self.right_panel_tab_widget.setTabsClosable(True)
        self.right_panel_tab_widget.tabCloseRequested.connect(self._close_tab)



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

    # обработка клика по дереву
    def _on_file_clicked(self, index):
        # преобразуем индекс в путь
        path = self.file_system_model.filePath(index)
        # преобразуем путь в виде строки в объект типа Path библиотеки pathlib
        file_path = Path(path)

        # проверка на то, файл ли это. return сразу завершает метод
        if not file_path.is_file():
            return

        # записываем имя и расширение
        file_name = file_path.name
        suffix = file_path.suffix.lower()

        # Просмотр файла
        if suffix == ".md" and self.opened_files.get(file_path) is None:
            # просмотр текста
            file_view_page = QWidget()
            self.right_panel_tab_widget.addTab(file_view_page, file_path.stem)

            file_view_layout = QVBoxLayout()
            file_view_page.setLayout(file_view_layout)

            text_view = QPlainTextEdit()
            file_view_layout.addWidget(text_view)
            text_view.setReadOnly(True)

            text_view.setPlainText(file_path.read_text(encoding="utf-8"))
            self.right_panel_tab_widget.setCurrentWidget(file_view_page)
            self.right_panel_tab_widget.setStyleSheet("background-color: white")
            self.opened_files[file_path] = file_view_page

        elif self.opened_files.get(file_path) is not None:
            self.right_panel_tab_widget.setCurrentWidget(self.opened_files[file_path])

        else:
            return

    # закрытие вкладки
    def _close_tab(self, index):
        widget_to_close = self.right_panel_tab_widget.widget(index)
        path = None
        for key, value in self.opened_files.items():
            if value is widget_to_close:
                path = key

        if path:
          self.opened_files.pop(path)

        self.right_panel_tab_widget.removeTab(index)



