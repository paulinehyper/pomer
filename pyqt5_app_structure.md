# 이메일/할일 관리 PyQt5 앱 구조 설계

## 1. 주요 화면 및 기능
- 로그인 화면: 이메일/비밀번호 입력, 로그인 버튼
- 메인 화면: 탭(Tab) 구조
    - 할일 목록(제출/검토): 테이블(상태, 분류, 마감일, D-day, 제목, 발신자)
    - 전체 메일: 테이블(분류, 마감일, D-day, 제목, 발신자, 날짜)
    - (옵션) 환경설정: 서버, 기간 등 설정 다이얼로그
- 상세 보기/수정: 더블클릭 또는 버튼으로 상세 정보 팝업
- 분류/마감일/상태 변경, 통계 표시

## 2. PyQt5 위젯 매핑
- QMainWindow: 전체 앱 프레임
- QStackedWidget: 로그인/메인 전환
- QTabWidget: 할일/전체메일 탭
- QTableWidget/QTableView: 리스트(할일, 메일)
- QDialog: 환경설정, 상세보기
- QLineEdit/QComboBox/QPushButton: 입력/액션
- QVBoxLayout/QHBoxLayout: 레이아웃

## 3. 주요 클래스 구조
- MainWindow(QMainWindow): 앱 전체, 로그인/메인 전환
- LoginWidget(QWidget): 로그인 카드형 UI
- MainWidget(QWidget): 탭, 리스트, 액션버튼, 통계 등
- TodoTable(QTableWidget): 할일 목록
- MailTable(QTableWidget): 전체 메일
- SettingsDialog(QDialog): 환경설정
- DetailDialog(QDialog): 상세보기/수정

## 4. 데이터 흐름
- 로그인 성공 시 MainWidget으로 전환
- 이메일 데이터 fetch 후 테이블에 표시
- 테이블 선택/더블클릭 시 상세/수정
- 분류/마감일/상태 변경 시 데이터 갱신

---

# 다음 단계: PyQt5 코드 생성 및 반영
