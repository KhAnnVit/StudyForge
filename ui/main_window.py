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
    QTabWidget,
    QMessageBox,
    QStackedWidget,
    QTextBrowser,
)

from PySide6.QtGui import (
    QShortcut,
    QKeySequence
)

from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView



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

        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self._save_current_file)

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

        # записываем расширение
        suffix = file_path.suffix.lower()

        # Просмотр файла
        if suffix == ".md" and self.opened_files.get(file_path) is None:
            self._set_markdown_mode(file_path)
        elif suffix == ".pdf" and self.opened_files.get(file_path) is None:
            self._set_pdf_mode(file_path)
        # elif suffix == ".docx" and self.opened_files.get(file_path) is None:
        #     self._set_docx_mode(file_path)
        # elif suffix == ".odt" and self.opened_files.get(file_path) is None:
        #     self._set_odt_mode(file_path)
        elif self.opened_files.get(file_path) is not None:
            self.right_panel_tab_widget.setCurrentWidget(self.opened_files[file_path]["page"])

        else:
            return

    # закрытие вкладки
    def _close_tab(self, index):
        widget_to_close = self.right_panel_tab_widget.widget(index)
        path = None
        for key, value in self.opened_files.items():
            if value["page"] is widget_to_close:
                path = key

        if path is not None:
            if self.opened_files[path]["modified"]:
                result = self._close_edited_file(path)
                if result == "Save":
                    self._save_file(path)
                    self.opened_files.pop(path)
                    self.right_panel_tab_widget.removeTab(index)
                elif result == "Discard":
                    self.opened_files.pop(path)
                    self.right_panel_tab_widget.removeTab(index)
                else:
                    return
            else:
                self.opened_files.pop(path)
                self.right_panel_tab_widget.removeTab(index)


    def _save_current_file(self):
        active_widget = self.right_panel_tab_widget.currentWidget()
        active_index = self.right_panel_tab_widget.indexOf(active_widget)
        path = None
        for key, value in self.opened_files.items():
            if value["page"] is active_widget:
                path = key


        if path is not None and self.opened_files[path]["editor"]:
            editor = self.opened_files[path]["editor"]
            path.write_text(editor.toPlainText(), encoding="utf-8")
            self.opened_files[path]["modified"] = False
            self.right_panel_tab_widget.setTabText(active_index, path.stem)


    def _mark_file_modified(self):
        current_widget = self.right_panel_tab_widget.currentWidget()
        current_index = self.right_panel_tab_widget.indexOf(current_widget)

        path = None

        for key, value in self.opened_files.items():
            if value["page"] is current_widget:
                path = key

        if path is not None:
            self.right_panel_tab_widget.setTabText(current_index, f"{path.stem} *")
            self.opened_files[path]["modified"] = True

    def _save_file(self, path):
        index = self.right_panel_tab_widget.indexOf(self.opened_files[path]["page"])

        if path is not None:
            editor = self.opened_files[path]["editor"]
            path.write_text(editor.toPlainText(), encoding="utf-8")
            self.opened_files[path]["modified"] = False
            self.right_panel_tab_widget.setTabText(index, path.stem)



    def _close_edited_file(self, path):
        # 1. Создаем объект диалога
        close_message = QMessageBox(self)
        close_message.setWindowTitle("Закрыть вкладку")
        close_message.setText(f"Сохранить изменения «{path.name}»?")

        # 2. Добавляем кнопки с кастомным текстом
        # Роль кнопки (ButtonRole) помогает Qt правильно расположить их по стандартам ОС
        save_button = close_message.addButton("Сохранить", QMessageBox.ButtonRole.AcceptRole)
        discard_button = close_message.addButton("Не сохранять", QMessageBox.ButtonRole.RejectRole)
        cancel_button = close_message.addButton("Отмена", QMessageBox.ButtonRole.ResetRole)

        # 3. Устанавливаем кнопку по умолчанию
        close_message.setDefaultButton(save_button)

        # 4. Показываем окно и проверяем, какая кнопка была нажата
        close_message.exec()


        if close_message.clickedButton() == save_button:
            return "Save"
        if close_message.clickedButton() == discard_button:
            return "Discard"
        if close_message.clickedButton() == cancel_button:
            return "Cancel"

    def closeEvent(self, event):
        for key, value in self.opened_files.items():
            if value["modified"]:
                result = self._close_edited_file(key)
                if result == "Save":
                    self._save_file(key)
                elif result == "Discard":
                    pass
                else:
                    event.ignore()
                    return

        event.accept()

    def _set_markdown_mode(self, file_path):
        # просмотр текста
        file_view_page = QWidget()
        self.right_panel_tab_widget.addTab(file_view_page, file_path.stem)

        file_view_layout = QVBoxLayout()
        file_view_page.setLayout(file_view_layout)

        mode_change = QWidget()
        mode_change_layout = QHBoxLayout()
        mode_change.setLayout(mode_change_layout)

        edit_button = QPushButton("Режим редактирования")
        view_button = QPushButton("Режим просмотра")

        mode_change_layout.addWidget(edit_button)
        mode_change_layout.addWidget(view_button)

        text = QStackedWidget()

        text_edit_mode = QPlainTextEdit()
        text_edit_mode.setReadOnly(False)
        text_edit_mode.setPlainText(file_path.read_text(encoding="utf-8"))

        text_view_mode = QTextBrowser()
        text_view_mode.setMarkdown(text_edit_mode.toPlainText())

        text.addWidget(text_view_mode)
        text.addWidget(text_edit_mode)
        text.setCurrentWidget(text_edit_mode)

        self.right_panel_tab_widget.setCurrentWidget(file_view_page)
        self.right_panel_tab_widget.setStyleSheet("background-color: white")
        self.opened_files[file_path] = {"page": file_view_page, "type": "markdown", "editor": text_edit_mode, "modified": False}

        text_edit_mode.textChanged.connect(self._mark_file_modified)

        file_view_layout.addWidget(mode_change, 1)
        file_view_layout.addWidget(text, 24)

        edit_button.clicked.connect(lambda: text.setCurrentWidget(text_edit_mode))
        view_button.clicked.connect(lambda: self._show_markdown_preview(text_edit_mode, text_view_mode, text))

    def _show_markdown_preview(self, editor, viewer, text_widget):
        viewer.setMarkdown(editor.toPlainText())
        text_widget.setCurrentWidget(viewer)

    def _set_pdf_mode(self, file_path):
        file_view_page = QWidget()
        self.right_panel_tab_widget.addTab(file_view_page, file_path.stem)

        file_view_layout = QVBoxLayout()
        file_view_page.setLayout(file_view_layout)

        file_viewer = self._create_document_wiever(file_path, file_view_page)

        file_view_layout.addWidget(file_viewer)

        self.opened_files[file_path] = {"page": file_view_page, "type": "pdf", "editor": None,
                                        "modified": False}
        self.right_panel_tab_widget.setCurrentWidget(file_view_page)

    '''
    def _set_docx_mode(self, file_path):
        file_view_page = QWidget()
        self.right_panel_tab_widget.addTab(file_view_page, file_path.stem)
        file_view_layout = QVBoxLayout()
        file_view_page.setLayout(file_view_layout)

        mode_change = QWidget()
        mode_change_layout = QHBoxLayout()
        mode_change.setLayout(mode_change_layout)

        view_button = QPushButton("Режим просмотра")
        edit_button = QPushButton("Режим редактирования")

        mode_change_layout.addWidget(view_button)
        mode_change_layout.addWidget(edit_button)

        document = QStackedWidget()


        document.addWidget(doc_view_mode)
        document.addWidget(doc_edit_mode)
        document.setCurrentWidget(doc_edit_mode)

        self.opened_files[file_path] = {"page": file_view_page, "type": "docx", "editor": text_edit_mode,
                                        "modified": False}

    def _set_odt_mode(self, file_path):
        file_view_page = QWidget()
        self.right_panel_tab_widget.addTab(file_view_page, file_path.stem)
        file_view_layout = QVBoxLayout()
        file_view_page.setLayout(file_view_layout)

        mode_change = QWidget()
        mode_change_layout = QHBoxLayout()
        mode_change.setLayout(mode_change_layout)

        view_button = QPushButton("Режим просмотра")
        edit_button = QPushButton("Режим редактирования")

        mode_change_layout.addWidget(view_button)
        mode_change_layout.addWidget(edit_button)

        document = QStackedWidget()

        document.addWidget(doc_view_mode)
        document.addWidget(doc_edit_mode)
        document.setCurrentWidget(doc_edit_mode)

        self.opened_files[file_path] = {"page": file_view_page, "type": "odt", "editor": text_edit_mode, "modified": False}
'''

    def _create_document_wiever(self, file_path, parent):
        if file_path.suffix.lower() == ".pdf":
            pdf = QPdfDocument(parent)
            pdf.load(str(file_path))
            doc_view_mode = QPdfView()
            doc_view_mode.setDocument(pdf)
            doc_view_mode.setPageMode(QPdfView.PageMode.MultiPage)
            doc_view_mode.setZoomMode(QPdfView.ZoomMode.FitToWidth)
            return doc_view_mode





