# Picker - A GUI application using PyQt6
# Copyright (C) 2025 kkachiverse
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import os
import sys
import shutil
import traceback
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, QMenu,
    QPushButton, QLineEdit, QTextEdit, QLabel, QDialog, QFileDialog
)
from PyQt6.QtGui import QRegularExpressionValidator, QAction
from PyQt6.QtCore import QRegularExpression, Qt


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Picker")
        self.setFixedSize(360, 220)

        layout = QVBoxLayout()

        label = QLabel(
            "<div style=\"text-align: center\">"
            "<h1>Picker</h1>"
            "<p><a href=\"https://github.com/kkachiverse/picker.git\">Github 소스코드</a></p>"
            "<p>GNU General Public License v3.0 <a href=\"https://www.gnu.org/licenses/gpl-3.0.en.html\">링크</a></p>"
            "<p>&copy; 2025 kkachiverse</p>"
            "</div>"
        )
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        label.setOpenExternalLinks(True)

        layout.addWidget(label)

        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Picker")
        central_widget = QWidget()
        layout = QVBoxLayout()
        menu_bar = self.menuBar()

        app_menu = QMenu(self)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)

        app_menu.addAction(about_action)
        menu_bar.addMenu(app_menu)

        test_menu = QMenu("Test", self)
        menu_bar.addMenu(test_menu)

        # 폴더 선택 영역 및 경로 표시
        grid_folder = QGridLayout()
        self.btn_reference_dir = QPushButton("기준 폴더 선택")
        self.label_reference_dir_path = QLabel("경로: ")
        self.btn_target_dir = QPushButton("찾는 폴더 선택")
        self.label_target_dir_path = QLabel("경로: ")

        grid_folder.addWidget(self.btn_reference_dir, 0, 0)
        grid_folder.addWidget(self.label_reference_dir_path, 0, 1)
        grid_folder.addWidget(self.btn_target_dir, 1, 0)
        grid_folder.addWidget(self.label_target_dir_path, 1, 1)
        layout.addLayout(grid_folder)

        # 확장자 입력 필드
        grid_ext = QGridLayout()
        label_reference_ext = QLabel("기준 파일 확장자")
        self.line_edit_reference_ext = QLineEdit()
        self.line_edit_reference_ext.setPlaceholderText("영대소문자, 숫자 최대 10자리")
        label_target_ext = QLabel("찾는 파일 확장자")
        self.line_edit_target_ext = QLineEdit()
        self.line_edit_target_ext.setPlaceholderText("영대소문자, 숫자 최대 10자리")

        regex = QRegularExpression("[a-zA-Z0-9]{1,10}")
        validator = QRegularExpressionValidator(regex, self)
        self.line_edit_reference_ext.setValidator(validator)
        self.line_edit_target_ext.setValidator(validator)

        grid_ext.addWidget(label_reference_ext, 0, 0)
        grid_ext.addWidget(self.line_edit_reference_ext, 0, 1)
        grid_ext.addWidget(label_target_ext, 1, 0)
        grid_ext.addWidget(self.line_edit_target_ext, 1, 1)
        layout.addLayout(grid_ext)

        # 실행 버튼
        self.btn_run = QPushButton("실행")
        layout.addWidget(self.btn_run)

        # 결과 출력 영역
        self.text_edit_log = QTextEdit()
        self.text_edit_log.setReadOnly(True)
        layout.addWidget(self.text_edit_log)

        # 시그널 연결
        self.btn_reference_dir.clicked.connect(self.select_reference_dir)
        self.btn_target_dir.clicked.connect(self.select_target_dir)
        self.btn_run.clicked.connect(self.run_process)

        # 변수 초기화
        self.reference_dir = None
        self.target_dir = None

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def log(self, message):
        self.text_edit_log.append(message)

    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.exec()

    def select_reference_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "기준 폴더 선택")
        if directory:
            self.reference_dir = directory
            self.label_reference_dir_path.setText(f"경로: {directory}")
            self.log(f"[INFO] 기준 폴더 선택: {directory}")

    def select_target_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "찾는 폴더 선택")
        if directory:
            self.target_dir = directory
            self.label_target_dir_path.setText(f"경로: {directory}")
            self.log(f"[INFO] 찾는 폴더 선택: {directory}")

    def run_process(self):
        # 폴더 지정 확인
        if not self.reference_dir or not self.target_dir:
            self.log("[ERROR] 두 개의 폴더를 모두 지정해야 합니다")
            return

        reference_ext = self.line_edit_reference_ext.text().strip().lower()
        target_ext = self.line_edit_target_ext.text().strip().lower()

        if not reference_ext or not target_ext:
            self.log("[ERROR] 두 확장자 모두 입력해야 합니다")
            return

        try:
            # 기준 폴더에서 파일 목록 추출
            self.log("----------")
            self.log(f"[INFO] 기준 폴더에서 .{reference_ext} 파일 검색 중...")

            reference_files = [f for f in os.listdir(self.reference_dir) if f.lower().endswith(f".{reference_ext}")]
            base_names = [os.path.splitext(f)[0] for f in reference_files]

            self.log(f"[INFO] 발견된 .{reference_ext} 파일 수: {len(reference_files)}")

            # 찾는 폴더에서 파일 매칭
            self.log(f"[INFO] 찾는 폴더에서 .{target_ext} 파일 매칭 중...")
            matched_paths = []

            for name in base_names:
                candidate = os.path.join(self.target_dir, f"{name}.{target_ext}")
                if os.path.isfile(candidate):
                    matched_paths.append(candidate)

            self.log(f"[INFO] 매칭된 .{target_ext} 파일 수: {len(matched_paths)}")

            # 파일 이동
            if not matched_paths:
                self.log("[WARN] 일치하는 파일이 없습니다")
                return

            self.log("[INFO] 작업 시작")

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            dest_dir = os.path.join(self.target_dir, f"selected_{timestamp}")
            os.makedirs(dest_dir, exist_ok=False)

            for src in matched_paths:
                shutil.move(src, dest_dir)
                # self.log(f"[MOVE] {os.path.basename(src)}")

            self.log(f"[SUCCESS] 총 {len(matched_paths)}개의 파일이 매칭되어 {dest_dir}로 이동하였습니다")
        except FileExistsError:
            self.log("[ERROR] 찾는 폴더에 동일한 이름의 폴더가 존재합니다")
        except Exception as e:
            self.log("[ERROR] 오류가 발생했습니다")
            self.log(traceback.format_exc())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Picker")
    app.setApplicationDisplayName("Picker")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
