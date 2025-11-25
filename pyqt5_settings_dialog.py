from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QCheckBox, QPushButton
from PyQt5.QtCore import Qt

class SettingsDialog(QDialog):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.setWindowTitle("환경설정")
        self.setModal(True)
        self.settings = settings or {}
        layout = QVBoxLayout(self)
        # 메일 서버 프리셋
        layout.addWidget(QLabel("메일 서버 프리셋:"))
        self.server_combo = QComboBox()
        self.server_combo.addItems(["KSD 메일", "Gmail", "Naver", "사용자 정의"])
        layout.addWidget(self.server_combo)
        # 사용자 정의 입력
        self.host_edit = QLineEdit()
        self.host_edit.setPlaceholderText("IMAP 호스트")
        self.port_edit = QLineEdit()
        self.port_edit.setPlaceholderText("포트 (예: 993)")
        self.ssl_check = QCheckBox("SSL 사용")
        # 레이아웃
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(self.host_edit)
        custom_layout.addWidget(self.port_edit)
        custom_layout.addWidget(self.ssl_check)
        layout.addLayout(custom_layout)
        # 저장/취소 버튼
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("저장")
        cancel_btn = QPushButton("취소")
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        # 이벤트
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        self.server_combo.currentTextChanged.connect(self.update_fields)
        self.update_fields(self.server_combo.currentText())
        # 기존 값 반영
        if self.settings:
            self.load_settings(self.settings)
    def update_fields(self, text):
        is_custom = (text == "사용자 정의")
        self.host_edit.setEnabled(is_custom)
        self.port_edit.setEnabled(is_custom)
        self.ssl_check.setEnabled(is_custom)
    def load_settings(self, s):
        self.server_combo.setCurrentText(s.get("mail_server", "KSD 메일"))
        self.host_edit.setText(s.get("custom_host", ""))
        self.port_edit.setText(str(s.get("custom_port", 993)))
        self.ssl_check.setChecked(s.get("custom_ssl", True))
    def get_settings(self):
        return {
            "mail_server": self.server_combo.currentText(),
            "custom_host": self.host_edit.text(),
            "custom_port": int(self.port_edit.text() or 993),
            "custom_ssl": self.ssl_check.isChecked()
        }
