import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QLabel, QDialog, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# --- 로그인 카드형 위젯 ---
class LoginWidget(QWidget):
    def __init__(self, on_login):
        super().__init__()
        self.on_login = on_login
        self.setStyleSheet("background: #F7F7F7;")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        card = QWidget()
        card.setStyleSheet("background: #fff; border-radius: 18px; border: 1px solid #eee;")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(16)
        font = QFont("Malgun Gothic", 12)
        self.username = QLineEdit()
        self.username.setPlaceholderText("사용자명")
        self.username.setFont(font)
        self.username.setStyleSheet("background: #f7f7f7; border-radius: 8px; padding: 10px;")
        self.password = QLineEdit()
        self.password.setPlaceholderText("비밀번호")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setFont(font)
        self.password.setStyleSheet("background: #f7f7f7; border-radius: 8px; padding: 10px;")
        self.login_btn = QPushButton("이메일 가져오기")
        self.login_btn.setFont(QFont("Malgun Gothic", 12, QFont.Bold))
        self.login_btn.setStyleSheet("background: #FFEB3B; color: #222; border-radius: 8px; padding: 12px;")
        self.login_btn.clicked.connect(self.try_login)
        card_layout.addWidget(self.username)
        card_layout.addWidget(self.password)
        card_layout.addWidget(self.login_btn)
        layout.addWidget(card, alignment=Qt.AlignCenter)
    def try_login(self):
        # 실제 인증 로직은 별도 구현
        self.on_login()

# --- 메인 탭/리스트 위젯 ---
class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabBar::tab { height: 36px; width: 120px; font: bold 12pt 'Malgun Gothic'; } QTabWidget::pane { border: none; }")
        # 할일 목록 탭
        self.todo_table = QTableWidget(0, 6)
        self.todo_table.setHorizontalHeaderLabels(["상태", "분류", "마감일", "데드라인", "제목", "발신자"])
        self.tabs.addTab(self.todo_table, "📋 할일 목록")
        # 전체 메일 탭
        self.mail_table = QTableWidget(0, 6)
        self.mail_table.setHorizontalHeaderLabels(["분류", "마감일", "데드라인", "제목", "발신자", "날짜"])
        self.tabs.addTab(self.mail_table, "📧 전체 메일")
        layout.addWidget(self.tabs)
        # (옵션) 하단 통계/액션 영역 등 추가 가능

# --- 메인 윈도우 ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("이메일 To-Do 관리 (PyQt5)")
        self.resize(900, 600)
        self.central = QStackedWidget()
        self.setCentralWidget(self.central)
        self.login = LoginWidget(self.show_main)
        self.main = MainWidget()
        self.central.addWidget(self.login)
        self.central.addWidget(self.main)
        self.central.setCurrentWidget(self.login)
    def show_main(self):
        self.central.setCurrentWidget(self.main)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
