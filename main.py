# main.py - GUI/실행부 진입점
import tkinter as tk
from tkinter import ttk, messagebox
from classifier import EmailClassifier
from email_client import fetch_emails
from models import MAIL_PRESETS, CATEGORY_DESCRIPTIONS, calculate_days_remaining, extract_due_date_candidate
from storage import load_settings, save_settings, load_categories

# ...
# (여기에 기존 3.py의 TodoApp, SettingsDialog, main 실행부를 옮겨오면 됩니다)
# 예시:

class SettingsDialog:
    # ... 기존 코드 그대로 ...
    pass

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("이메일 To-Do 관리")
        self.root.geometry("900x600")
        # 스타일 적용 (모던 화이트)
        self.style = ttk.Style()
        self.style.theme_use('clam')
        # KakaoTalk palette
        kakao_yellow = '#FFEB3B'
        kakao_yellow_hover = '#ffe066'
        kakao_gray_bg = '#F7F7F7'
        kakao_panel = '#FFFFFF'
        kakao_border = '#E0E0E0'
        kakao_text = '#222'
        kakao_tab_sel = '#FFF9C4'
        kakao_tab_unsel = '#F7F7F7'
        kakao_tab_border = '#FFEB3B'
        kakao_font = ("Kakao Regular", 11)
        kakao_font_bold = ("Kakao Regular", 11, "bold")
        # Base
        self.style.configure('.', background=kakao_gray_bg, foreground=kakao_text, font=kakao_font)
        self.style.configure('TLabel', background=kakao_gray_bg, foreground=kakao_text, font=kakao_font)
        self.style.configure('TFrame', background=kakao_panel, font=kakao_font, borderwidth=0, relief='flat')
        # Button: rounded, white, black text (Kakao style: white base, yellow only for highlights)
        self.style.configure('TButton', background=kakao_panel, foreground=kakao_text, font=kakao_font_bold, borderwidth=0, relief='flat', padding=8)
        self.style.map('TButton',
            background=[('active', kakao_tab_sel), ('pressed', kakao_tab_sel), ('!active', kakao_panel)],
            foreground=[('active', kakao_text), ('pressed', kakao_text), ('!active', kakao_text)]
        )
        # Entry: flat, white, no shadow/gradient, subtle border
        self.style.configure('TEntry', fieldbackground=kakao_panel, foreground=kakao_text, font=kakao_font, borderwidth=1, relief='flat', padding=6, highlightthickness=0, highlightcolor=kakao_border)
        # Remove any focus/active background or border color changes for flat look
        self.style.map('TEntry',
            fieldbackground=[('active', kakao_panel), ('!active', kakao_panel)],
            background=[('active', kakao_panel), ('!active', kakao_panel)]
        )
        # Notebook (tabs)
        self.style.configure('TNotebook', background=kakao_gray_bg, borderwidth=0, font=kakao_font, padding=4)
        self.style.configure('TNotebook.Tab', background=kakao_tab_unsel, foreground=kakao_text, font=kakao_font_bold, padding=[16, 8], borderwidth=0)
        self.style.map('TNotebook.Tab',
            background=[('selected', kakao_tab_sel), ('active', kakao_yellow_hover), ('!selected', kakao_tab_unsel)],
            foreground=[('selected', kakao_text), ('active', kakao_text), ('!selected', kakao_text)],
            font=[('selected', kakao_font_bold), ('!selected', kakao_font)]
        )
        # Treeview (list): rounded, subtle border, soft header
        self.style.configure('Treeview', background=kakao_panel, fieldbackground=kakao_panel, foreground=kakao_text, rowheight=30, font=kakao_font, borderwidth=0, relief='flat')
        self.style.configure('Treeview.Heading', background=kakao_gray_bg, foreground=kakao_text, font=kakao_font_bold, borderwidth=0, relief='flat')
        # Labelframe: rounded, soft border
        self.style.configure('TLabelframe', background=kakao_panel, foreground=kakao_text, font=kakao_font_bold, borderwidth=0, relief='flat')
        self.style.configure('TLabelframe.Label', background=kakao_panel, foreground=kakao_text, font=kakao_font_bold)
        # Scrollbar: minimal
        self.style.configure('TScrollbar', background=kakao_gray_bg, troughcolor=kakao_panel, borderwidth=0, relief='flat')
        self.root.configure(bg=kakao_gray_bg)
        # Load settings
        self.settings = load_settings()
        # Variables
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.emails_data = []
        # AI Classifier
        self.classifier = EmailClassifier()
        self.classifier.train()
        # Categories
        self.categories = load_categories()
        self.create_widgets()
        self.update_status_with_settings()

    def create_widgets(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="설정", menu=settings_menu)
        settings_menu.add_command(label="환경설정", command=self.open_settings)
        settings_menu.add_separator()
        settings_menu.add_command(label="종료", command=self.root.quit)
        login_frame = ttk.LabelFrame(self.root, text="IMAP 로그인", padding=10)
        login_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(login_frame, text="사용자명:").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Entry(login_frame, textvariable=self.username_var, width=30).grid(row=0, column=1, padx=5)
        ttk.Label(login_frame, text="비밀번호:").grid(row=1, column=0, sticky="w", padx=5)
        ttk.Entry(login_frame, textvariable=self.password_var, show="*", width=30).grid(row=1, column=1, padx=5)
        ttk.Button(login_frame, text="이메일 가져오기", command=self.fetch_emails_handler).grid(row=0, column=2, rowspan=2, padx=10)
        ttk.Button(login_frame, text="⚙ 환경설정", command=self.open_settings).grid(row=0, column=3, rowspan=2, padx=5)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        todo_tab = ttk.Frame(self.notebook)
        self.notebook.add(todo_tab, text="📋 할일 목록")
        email_tab = ttk.Frame(self.notebook)
        self.notebook.add(email_tab, text="📧 전체 메일")
        todo_container = ttk.Frame(todo_tab)
        todo_container.pack(fill="both", expand=True, padx=5, pady=5)
        todo_list_frame = ttk.LabelFrame(todo_container, text="할일 목록 (제출/검토)", padding=10)
        todo_list_frame.pack(side="left", fill="both", expand=True)
        todo_columns = ("상태", "분류", "마감일", "데드라인", "제목", "발신자")
        self.todo_tree = ttk.Treeview(todo_list_frame, columns=todo_columns, show="tree headings", height=20)
        self.todo_tree.heading("#0", text="번호")
        self.todo_tree.column("#0", width=50)
        for col in todo_columns:
            self.todo_tree.heading(col, text=col)
        self.todo_tree.column("상태", width=60)
        self.todo_tree.column("분류", width=60)
        self.todo_tree.column("마감일", width=100)
        self.todo_tree.column("데드라인", width=80)
        self.todo_tree.column("제목", width=300)
        self.todo_tree.column("발신자", width=120)
        todo_scrollbar = ttk.Scrollbar(todo_list_frame, orient="vertical", command=self.todo_tree.yview)
        self.todo_tree.configure(yscrollcommand=todo_scrollbar.set)
        self.todo_tree.pack(side="left", fill="both", expand=True)
        todo_scrollbar.pack(side="right", fill="y")
        todo_action_frame = ttk.LabelFrame(todo_container, text="할일 관리", padding=10)
        todo_action_frame.pack(side="right", fill="y", padx=(10, 0))
        ttk.Button(todo_action_frame, text="✓ 완료 처리", command=self.mark_todo_complete, width=15).pack(pady=5)
        ttk.Button(todo_action_frame, text="↻ 미완료로 변경", command=self.mark_todo_incomplete, width=15).pack(pady=5)
        ttk.Button(todo_action_frame, text="상세 보기", command=self.view_todo_detail, width=15).pack(pady=5)
        ttk.Separator(todo_action_frame, orient="horizontal").pack(fill="x", pady=10)
        ttk.Label(todo_action_frame, text="할일 통계:", font=("", 9, "bold")).pack(anchor="w", pady=(0, 5))
        self.todo_stats_label = ttk.Label(todo_action_frame, text="", font=("", 8), foreground="gray")
        self.todo_stats_label.pack(anchor="w", fill="x")
        self.todo_tree.bind("<<TreeviewSelect>>", self.on_todo_select)
        self.todo_tree.bind("<Double-1>", lambda e: self.view_todo_detail())
        email_container = ttk.Frame(email_tab)
        email_container.pack(fill="both", expand=True, padx=5, pady=5)
        list_frame = ttk.LabelFrame(email_container, text="이메일 목록", padding=10)
        list_frame.pack(side="left", fill="both", expand=True)
        columns = ("분류", "마감일", "데드라인", "제목", "발신자", "날짜")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="tree headings", height=15)
        self.tree.heading("#0", text="번호")
        self.tree.column("#0", width=50)
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.column("분류", width=70)
        self.tree.column("마감일", width=100)
        self.tree.column("데드라인", width=80)
        self.tree.column("제목", width=220)
        self.tree.column("발신자", width=120)
        self.tree.column("날짜", width=100)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        detail_category_frame = ttk.Frame(email_container)
        detail_category_frame.pack(side="right", fill="y", padx=(10, 0))
        category_frame = ttk.LabelFrame(detail_category_frame, text="분류 관리", padding=10)
        category_frame.pack(fill="both", expand=True)
        ttk.Label(category_frame, text="현재 분류:").pack(anchor="w", pady=(0, 5))
        self.current_category_label = ttk.Label(category_frame, text="-", font=("", 10, "bold"))
        self.current_category_label.pack(anchor="w", pady=(0, 5))
        ttk.Label(category_frame, text="마감일:").pack(anchor="w", pady=(0, 5))
        self.due_date_label = ttk.Label(category_frame, text="-", font=("", 9), foreground="red")
        self.due_date_label.pack(anchor="w", pady=(0, 10))
        ttk.Separator(category_frame, orient="horizontal").pack(fill="x", pady=5)
        ttk.Label(category_frame, text="분류 변경:").pack(anchor="w", pady=(0, 5))
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(category_frame, textvariable=self.category_var, 
                                            values=self.categories, state="readonly", width=15)
        self.category_combo.pack(pady=(0, 5))
        ttk.Button(category_frame, text="분류 적용", command=self.apply_category, width=15).pack(pady=(0, 5))
        ttk.Label(category_frame, text="마감일 설정:").pack(anchor="w", pady=(10, 5))
        due_date_entry_frame = ttk.Frame(category_frame)
        due_date_entry_frame.pack(fill="x", pady=(0, 5))
        self.due_date_entry = ttk.Entry(due_date_entry_frame, width=10)
        self.due_date_entry.pack(side="left")
        ttk.Label(due_date_entry_frame, text="MM/DD", font=("", 8)).pack(side="left", padx=(5, 0))
        ttk.Button(category_frame, text="마감일 적용", command=self.apply_due_date, width=15).pack(pady=(0, 10))
        ttk.Separator(category_frame, orient="horizontal").pack(fill="x", pady=10)
        ttk.Label(category_frame, text="카테고리 관리:").pack(anchor="w", pady=(0, 5))
        ttk.Button(category_frame, text="새 카테고리 추가", command=self.add_category, width=15).pack(pady=(0, 5))
        ttk.Separator(category_frame, orient="horizontal").pack(fill="x", pady=10)
        ttk.Label(category_frame, text="AI 학습 상태:", font=("", 8)).pack(anchor="w")
        self.training_status_label = ttk.Label(category_frame, text=f"{len(self.classifier.training_data)}개 학습됨", 
                                                font=("", 8), foreground="gray")
        self.training_status_label.pack(anchor="w", pady=(0, 5))
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.status_label = ttk.Label(self.root, text="준비", relief="sunken")
        self.status_label.pack(fill="x", side="bottom", padx=10, pady=5)

    def update_status_with_settings(self):
        server_name = self.settings.get("mail_server", "KSD 메일")
        days = self.settings.get("days_lookback", 7)
        self.status_label.config(text=f"현재 설정: {server_name} | {days}일 조회")

    def open_settings(self):
        dialog = SettingsDialog(self.root, self.settings)
        self.root.wait_window(dialog.dialog)
        if dialog.result:
            self.settings = dialog.result
            save_settings(self.settings)
            self.update_status_with_settings()
            messagebox.showinfo("설정 저장", "환경설정이 저장되었습니다.")

    def get_mail_config(self):
        server_name = self.settings.get("mail_server", "KSD 메일")
        if server_name == "사용자 정의":
            return {
                "host": self.settings.get("custom_host", ""),
                "port": self.settings.get("custom_port", 993),
                "use_ssl": self.settings.get("custom_ssl", True)
            }
        elif server_name in MAIL_PRESETS:
            return MAIL_PRESETS[server_name]
        else:
            return MAIL_PRESETS["KSD 메일"]

    def fetch_emails_handler(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        if not username or not password:
            messagebox.showwarning("입력 오류", "사용자명과 비밀번호를 입력하세요.")
            return
        mail_config = self.get_mail_config()
        if not mail_config["host"]:
            messagebox.showerror("설정 오류", "메일 서버 호스트가 설정되지 않았습니다.\n환경설정에서 서버를 설정하세요.")
            return
        server_name = self.settings.get("mail_server", "KSD 메일")
        days = self.settings.get("days_lookback", 7)
        self.status_label.config(text=f"이메일 가져오는 중... ({server_name})")
        self.root.update()
        try:
            self.emails_data = fetch_emails(
                username, 
                password, 
                mail_config["host"], 
                mail_config["port"], 
                mail_config["use_ssl"],
                days
            )
            self.populate_tree()
            self.populate_todo_tree()
            self.status_label.config(text=f"{server_name}에서 {len(self.emails_data)}개의 이메일을 가져왔습니다.")
            messagebox.showinfo("성공", f"{len(self.emails_data)}개의 이메일을 가져왔습니다.")
        except Exception as e:
            self.status_label.config(text="오류 발생")
            messagebox.showerror("오류", f"이메일 가져오기 실패:\n{str(e)}\n\n팁: Gmail은 앱 비밀번호가 필요하며,\nNaver는 IMAP 설정을 활성화해야 합니다.")

    def populate_todo_tree(self):
        for item in self.todo_tree.get_children():
            self.todo_tree.delete(item)
        todo_count = 0
        completed_count = 0
        overdue_count = 0
        for idx, email_data in enumerate(self.emails_data, 1):
            category = email_data.get("category", "")
            if category not in ["제출", "검토"]:
                continue
            subject = email_data.get("subject", "제목 없음")
            from_ = email_data.get("from", "발신자 없음")
            due_date = email_data.get("due_date")
            is_completed = email_data.get("is_completed", False)
            if is_completed:
                status = "✓ 완료"
                completed_count += 1
            else:
                status = "☐ 대기"
                todo_count += 1
            # 마감일 및 D-day 계산
            if due_date:
                days_remaining, remaining_str = calculate_days_remaining(due_date)
                due_date_str = f"{due_date.strftime('%m/%d')}"
                # D-day 포맷
                if days_remaining == 0:
                    dday_str = "D-day"
                elif days_remaining > 0:
                    dday_str = f"D-{days_remaining}"
                else:
                    dday_str = f"D+{abs(days_remaining)}"
                if not is_completed and days_remaining < 0:
                    overdue_count += 1
            else:
                due_date_str = "-"
                dday_str = "-"
            item_id = self.todo_tree.insert("", "end", text=str(idx), 
                                            values=(status, category, due_date_str, dday_str, subject, from_))
            if is_completed:
                self.todo_tree.item(item_id, tags=("completed",))
            elif due_date and days_remaining < 0:
                self.todo_tree.item(item_id, tags=("overdue",))
        self.todo_tree.tag_configure("completed", foreground="gray")
        self.todo_tree.tag_configure("overdue", foreground="red")
        stats_text = f"미완료: {todo_count}개\n완료: {completed_count}개\n기한경과: {overdue_count}개"
        self.todo_stats_label.config(text=stats_text)

    def populate_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for idx, email_data in enumerate(self.emails_data, 1):
            subject = email_data.get("subject", "제목 없음")
            from_ = email_data.get("from", "발신자 없음")
            date_header = email_data.get("date_header", "날짜 없음")
            body = email_data.get("body", "")
            if "category" not in email_data:
                category = self.classifier.predict(subject, body, from_)
                email_data["category"] = category
            else:
                category = email_data["category"]
            due_date_str = "-"
            dday_str = "-"
            if "due_date" not in email_data and category == "제출":
                full_text = f"{subject} {body}"
                due_date = extract_due_date_candidate(full_text)
                if due_date:
                    email_data["due_date"] = due_date
                    days_remaining, _ = calculate_days_remaining(due_date)
                    due_date_str = f"{due_date.strftime('%m/%d')}"
                    if days_remaining == 0:
                        dday_str = "D-day"
                    elif days_remaining > 0:
                        dday_str = f"D-{days_remaining}"
                    else:
                        dday_str = f"D+{abs(days_remaining)}"
                else:
                    email_data["due_date"] = None
            elif "due_date" in email_data and email_data["due_date"]:
                due_date = email_data["due_date"]
                days_remaining, _ = calculate_days_remaining(due_date)
                due_date_str = f"{due_date.strftime('%m/%d')}"
                if days_remaining == 0:
                    dday_str = "D-day"
                elif days_remaining > 0:
                    dday_str = f"D-{days_remaining}"
                else:
                    dday_str = f"D+{abs(days_remaining)}"
            self.tree.insert("", "end", text=str(idx), values=(category, due_date_str, dday_str, subject, from_, date_header))

    def on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        item = selection[0]
        idx = int(self.tree.item(item, "text")) - 1
        if 0 <= idx < len(self.emails_data):
            email_data = self.emails_data[idx]
            # 상세 정보 표시
            # (상세 정보 표시 위젯이 main.py에 구현되어 있으면 여기에 추가)
            # 현재 분류 표시
            self.current_category_label.config(text=email_data.get('category', '미분류'))
            self.category_var.set(email_data.get('category', '미분류'))
            # 마감일 표시
            due_date = email_data.get('due_date')
            if due_date:
                days_remaining, remaining_str = calculate_days_remaining(due_date)
                due_str = f"{due_date.strftime('%Y-%m-%d')}\n{remaining_str}"
                color = "red" if days_remaining < 0 else "orange" if days_remaining <= 3 else "green"
                self.due_date_label.config(text=due_str, foreground=color)
                self.due_date_entry.delete(0, "end")
                self.due_date_entry.insert(0, due_date.strftime("%m/%d"))
            else:
                self.due_date_label.config(text="-", foreground="gray")
                self.due_date_entry.delete(0, "end")

    def apply_category(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("선택 없음", "분류를 변경할 메일을 선택하세요.")
            return
        item = selection[0]
        idx = int(self.tree.item(item, "text")) - 1
        new_category = self.category_var.get()
        if not new_category:
            messagebox.showwarning("분류 없음", "적용할 분류를 선택하세요.")
            return
        if 0 <= idx < len(self.emails_data):
            email_data = self.emails_data[idx]
            old_category = email_data.get("category", "")
            email_data["category"] = new_category
            self.classifier.add_training_data(
                email_data.get("subject", ""),
                email_data.get("body", ""),
                new_category
            )
            values = list(self.tree.item(item, "values"))
            values[0] = new_category
            if new_category == "제출" and not email_data.get("due_date"):
                full_text = f"{email_data.get('subject', '')} {email_data.get('body', '')}"
                due_date = extract_due_date_candidate(full_text)
                if due_date:
                    email_data["due_date"] = due_date
                    _, remaining_str = calculate_days_remaining(due_date)
                    values[1] = f"{due_date.strftime('%m/%d')} {remaining_str}"
                    self.due_date_label.config(text=f"{due_date.strftime('%Y-%m-%d')}\n{remaining_str}")
                    self.due_date_entry.delete(0, "end")
                    self.due_date_entry.insert(0, due_date.strftime("%m/%d"))
            elif new_category != "제출":
                values[1] = "-"
            self.tree.item(item, values=values)
            self.current_category_label.config(text=new_category)
            self.training_status_label.config(text=f"{len(self.classifier.training_data)}개 학습됨")
            self.populate_todo_tree()
            if old_category != new_category:
                messagebox.showinfo("분류 변경", f"'{old_category}' → '{new_category}'로 변경되었습니다.\nAI 학습이 업데이트되었습니다.")

    def apply_due_date(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("선택 없음", "마감일을 설정할 메일을 선택하세요.")
            return
        item = selection[0]
        idx = int(self.tree.item(item, "text")) - 1
        due_date_str = self.due_date_entry.get().strip()
        if not due_date_str:
            messagebox.showwarning("입력 오류", "마감일을 MM/DD 형식으로 입력하세요.\n예: 11/30")
            return
        try:
            parts = due_date_str.split("/")
            if len(parts) != 2:
                raise ValueError("형식 오류")
            month, day = map(int, parts)
            from datetime import datetime, date
            year = datetime.now().year
            due_date = date(year, month, day)
            if due_date < date.today():
                due_date = date(year + 1, month, day)
        except Exception as e:
            messagebox.showerror("입력 오류", f"올바른 날짜 형식이 아닙니다.\nMM/DD 형식으로 입력하세요.\n예: 11/30\n\n오류: {e}")
            return
        if 0 <= idx < len(self.emails_data):
            email_data = self.emails_data[idx]
            email_data["due_date"] = due_date
            values = list(self.tree.item(item, "values"))
            _, remaining_str = calculate_days_remaining(due_date)
            values[1] = f"{due_date.strftime('%m/%d')} {remaining_str}"
            self.tree.item(item, values=values)
            days_remaining, remaining_str = calculate_days_remaining(due_date)
            due_str = f"{due_date.strftime('%Y-%m-%d')}\n{remaining_str}"
            if days_remaining < 0:
                color = "red"
            elif days_remaining == 0:
                color = "red"
            elif days_remaining <= 3:
                color = "orange"
            else:
                color = "green"
            self.due_date_label.config(text=due_str, foreground=color)
            self.populate_todo_tree()
            messagebox.showinfo("마감일 설정", f"마감일이 {due_date.strftime('%Y년 %m월 %d일')}로 설정되었습니다.\n{remaining_str}")

    def add_category(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("새 카테고리 추가")
        dialog.geometry("350x150")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="새 카테고리 이름:").pack(anchor="w", pady=(0, 5))
        category_entry = ttk.Entry(frame, width=30)
        category_entry.pack(pady=(0, 10))
        category_entry.focus()
        def save_new_category():
            new_cat = category_entry.get().strip()
            if not new_cat:
                messagebox.showwarning("입력 오류", "카테고리 이름을 입력하세요.")
                return
            if new_cat in self.categories:
                messagebox.showwarning("중복", "이미 존재하는 카테고리입니다.")
                return
            self.categories.append(new_cat)
            save_categories(self.categories)
            self.category_combo['values'] = self.categories
            messagebox.showinfo("성공", f"'{new_cat}' 카테고리가 추가되었습니다.")
            dialog.destroy()
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=(10, 0))
        ttk.Button(button_frame, text="추가", command=save_new_category).pack(side="left", padx=5)
        ttk.Button(button_frame, text="취소", command=dialog.destroy).pack(side="left", padx=5)
        category_entry.bind("<Return>", lambda e: save_new_category())

    def on_todo_select(self, event):
        selection = self.todo_tree.selection()
        if not selection:
            return
        item = selection[0]
        idx = int(self.todo_tree.item(item, "text")) - 1
        if 0 <= idx < len(self.emails_data):
            pass

    def mark_todo_complete(self):
        selection = self.todo_tree.selection()
        if not selection:
            messagebox.showwarning("선택 없음", "완료 처리할 할일을 선택하세요.")
            return
        item = selection[0]
        idx = int(self.todo_tree.item(item, "text")) - 1
        if 0 <= idx < len(self.emails_data):
            email_data = self.emails_data[idx]
            email_data["is_completed"] = True
            values = list(self.todo_tree.item(item, "values"))
            values[0] = "✓ 완료"
            self.todo_tree.item(item, values=values, tags=("completed",))
            self.populate_todo_tree()
            messagebox.showinfo("완료", "할일이 완료 처리되었습니다.")

    def mark_todo_incomplete(self):
        selection = self.todo_tree.selection()
        if not selection:
            messagebox.showwarning("선택 없음", "미완료로 변경할 할일을 선택하세요.")
            return
        item = selection[0]
        idx = int(self.todo_tree.item(item, "text")) - 1
        if 0 <= idx < len(self.emails_data):
            email_data = self.emails_data[idx]
            email_data["is_completed"] = False
            values = list(self.todo_tree.item(item, "values"))
            values[0] = "☐ 대기"
            self.todo_tree.item(item, values=values, tags=())
            self.populate_todo_tree()
            messagebox.showinfo("변경", "할일이 미완료로 변경되었습니다.")

    def view_todo_detail(self):
        selection = self.todo_tree.selection()
        if not selection:
            messagebox.showwarning("선택 없음", "상세 보기할 할일을 선택하세요.")
            return
        item = selection[0]
        idx = int(self.todo_tree.item(item, "text")) - 1
        if 0 <= idx < len(self.emails_data):
            email_data = self.emails_data[idx]
            detail_window = tk.Toplevel(self.root)
            detail_window.title("할일 상세 정보")
            detail_window.geometry("700x500")
            detail_window.transient(self.root)
            frame = ttk.Frame(detail_window, padding=20)
            frame.pack(fill="both", expand=True)
            info_frame = ttk.Frame(frame)
            info_frame.pack(fill="x", pady=(0, 10))
            category = email_data.get('category', '미분류')
            due_date = email_data.get('due_date')
            is_completed = email_data.get('is_completed', False)
            ttk.Label(info_frame, text=f"분류: {category}", font=("", 10, "bold")).pack(anchor="w")
            if due_date:
                days_remaining, remaining_str = calculate_days_remaining(due_date)
                color = "red" if days_remaining < 0 else "orange" if days_remaining <= 3 else "green"
                due_label = ttk.Label(info_frame, 
                                     text=f"마감일: {due_date.strftime('%Y년 %m월 %d일')} ({remaining_str})",
                                     font=("", 10), foreground=color)
                due_label.pack(anchor="w")
            status_text = "✓ 완료됨" if is_completed else "☐ 진행 중"
            ttk.Label(info_frame, text=f"상태: {status_text}", font=("", 10)).pack(anchor="w")
            ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=10)
            content_frame = ttk.LabelFrame(frame, text="메일 내용", padding=10)
            content_frame.pack(fill="both", expand=True)
            text_widget = tk.Text(content_frame, wrap="word", height=15)
            text_scroll = ttk.Scrollbar(content_frame, orient="vertical", command=text_widget.yview)
            text_widget.configure(yscrollcommand=text_scroll.set)
            content = f"제목: {email_data.get('subject', '')}\n"
            content += f"발신자: {email_data.get('from', '')}\n"
            content += f"날짜: {email_data.get('date_header', '')}\n"
            content += "\n" + "="*50 + "\n\n"
            content += email_data.get('body', '')
            text_widget.insert("1.0", content)
            text_widget.config(state="disabled")
            text_widget.pack(side="left", fill="both", expand=True)
            text_scroll.pack(side="right", fill="y")
            button_frame = ttk.Frame(frame)
            button_frame.pack(fill="x", pady=(10, 0))
            if is_completed:
                ttk.Button(button_frame, text="미완료로 변경", 
                          command=lambda: [email_data.update({"is_completed": False}), 
                                          self.populate_todo_tree(), detail_window.destroy()]).pack(side="right", padx=5)
            else:
                ttk.Button(button_frame, text="완료 처리", 
                          command=lambda: [email_data.update({"is_completed": True}), 
                                          self.populate_todo_tree(), detail_window.destroy()]).pack(side="right", padx=5)
            ttk.Button(button_frame, text="닫기", command=detail_window.destroy).pack(side="right")

def main():
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
