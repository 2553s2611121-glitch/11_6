
import streamlit as st
import sqlite3
import time
import html
from pathlib import Path
from datetime import datetime, date, timedelta

# ==================================================
# 1. 기본 설정
# ==================================================

st.set_page_config(
    page_title="출결 관리 시스템",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = Path(__file__).parent / "attendance.db"
TIME_LIMIT = 30 * 60


# ==================================================
# 2. 데이터베이스
# ==================================================

def connect_db():
    conn = sqlite3.connect(str(DB_PATH), timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                class_name TEXT NOT NULL DEFAULT '2학년 3반',
                student_number TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT '출석',
                reason TEXT NOT NULL DEFAULT '-',
                started REAL,
                updated TEXT NOT NULL
            )
        """)

        # 기존 데이터베이스에 새 열이 없으면 추가합니다.
        columns = {
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(students)"
            ).fetchall()
        }

        if "class_name" not in columns:
            conn.execute("""
                ALTER TABLE students
                ADD COLUMN class_name TEXT NOT NULL DEFAULT '2학년 3반'
            """)

        if "student_number" not in columns:
            conn.execute("""
                ALTER TABLE students
                ADD COLUMN student_number TEXT DEFAULT ''
            """)

        count = conn.execute(
            "SELECT COUNT(*) FROM students"
        ).fetchone()[0]

        if count == 0:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            examples = [
                ("김도현", "2학년 3반", "1"),
                ("이서연", "2학년 3반", "2"),
                ("박지민", "2학년 3반", "3"),
                ("최예은", "2학년 3반", "4"),
                ("정민준", "2학년 3반", "5"),
                ("한지민", "2학년 3반", "6"),
                ("강민서", "2학년 3반", "7"),
                ("이준호", "2학년 3반", "8"),
                ("유나영", "2학년 3반", "9"),
                ("신동우", "2학년 3반", "10"),
                ("조하은", "2학년 3반", "11"),
                ("성지윤", "2학년 3반", "12"),
                ("윤서준", "2학년 3반", "13"),
                ("이다은", "2학년 3반", "14"),
            ]

            for name, class_name, number in examples:
                conn.execute("""
                    INSERT INTO students
                    (name, class_name, student_number,
                     status, reason, started, updated)
                    VALUES (?, ?, ?, '출석', '-', NULL, ?)
                """, (name, class_name, number, now))


def get_students(class_name=None):
    with connect_db() as conn:
        if class_name and class_name != "전체":
            rows = conn.execute("""
                SELECT * FROM students
                WHERE class_name = ?
                ORDER BY CAST(student_number AS INTEGER), id
            """, (class_name,)).fetchall()
        else:
            rows = conn.execute("""
                SELECT * FROM students
                ORDER BY class_name, CAST(student_number AS INTEGER), id
            """).fetchall()

    return [dict(row) for row in rows]


def get_classes():
    with connect_db() as conn:
        rows = conn.execute("""
            SELECT DISTINCT class_name
            FROM students
            ORDER BY class_name
        """).fetchall()

    return [row["class_name"] for row in rows]


# ==================================================
# 3. 학생 등록, 수정, 삭제
# ==================================================

def add_student(name, class_name, student_number):
    name = name.strip()
    class_name = class_name.strip()
    student_number = student_number.strip()

    if not name:
        return False, "학생 이름을 입력해 주세요."

    if not class_name:
        return False, "학급을 입력해 주세요."

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with connect_db() as conn:
            conn.execute("""
                INSERT INTO students
                (name, class_name, student_number,
                 status, reason, started, updated)
                VALUES (?, ?, ?, '출석', '-', NULL, ?)
            """, (name, class_name, student_number, now))

        return True, f"{name} 학생을 등록했습니다."

    except sqlite3.IntegrityError:
        return False, "이미 등록된 이름입니다."


def rename_student(student_id, name, class_name, student_number):
    name = name.strip()
    class_name = class_name.strip()
    student_number = student_number.strip()

    if not name or not class_name:
        return False, "학생 이름과 학급을 입력해 주세요."

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with connect_db() as conn:
            conn.execute("""
                UPDATE students
                SET name = ?, class_name = ?,
                    student_number = ?, updated = ?
                WHERE id = ?
            """, (
                name, class_name, student_number,
                now, student_id
            ))

        return True, "학생 정보를 수정했습니다."

    except sqlite3.IntegrityError:
        return False, "이미 등록된 이름입니다."


def delete_student(student_id):
    with connect_db() as conn:
        cursor = conn.execute(
            "DELETE FROM students WHERE id = ?",
            (student_id,)
        )

        if cursor.rowcount == 0:
            return False, "학생 정보를 찾을 수 없습니다."

    return True, "학생을 삭제했습니다."


# ==================================================
# 4. 출결 처리와 타이머
# ==================================================

def update_student(student_id, status, reason="-", started=None):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with connect_db() as conn:
        conn.execute("""
            UPDATE students
            SET status = ?, reason = ?,
                started = ?, updated = ?
            WHERE id = ?
        """, (status, reason, started, now, student_id))


def start_absence(student_id):
    update_student(
        student_id,
        "사유 확인 대기",
        "사유 미확인",
        time.time(),
    )


def confirm_reason(student_id, reason):
    reason = reason.strip()

    if not reason:
        return False, "결석 사유를 입력해 주세요."

    update_student(
        student_id,
        "결석",
        reason,
        None,
    )

    return True, "사유를 저장하고 타이머를 종료했습니다."


def set_status(student_id, status):
    if status == "사유 확인 대기":
        start_absence(student_id)
    elif status == "출석":
        update_student(student_id, "출석", "-", None)
    elif status == "지각":
        update_student(student_id, "지각", "-", None)
    elif status == "결석":
        update_student(student_id, "결석", "사유 미확인", None)
    elif status == "무단결석":
        update_student(student_id, "무단결석", "사유 미확인", None)


def process_timers():
    now = time.time()
    students = get_students()

    for student in students:
        if (
            student["status"] == "사유 확인 대기"
            and student["started"] is not None
            and now - student["started"] >= TIME_LIMIT
        ):
            update_student(
                student["id"],
                "무단결석",
                "30분 내 사유 미확인",
                None,
            )


def remaining_seconds(student):
    if student["started"] is None:
        return None

    return max(
        0,
        TIME_LIMIT - int(time.time() - student["started"])
    )


def format_timer(student):
    remaining = remaining_seconds(student)

    if remaining is None:
        return "-"

    minutes = remaining // 60
    seconds = remaining % 60

    return f"{minutes:02d}:{seconds:02d}"


# ==================================================
# 5. 화면 스타일
# ==================================================

st.markdown("""
<style>
    .stApp {
        background: #f5f8fc;
        color: #203653;
    }

    [data-testid="stHeader"] {
        background: rgba(245, 248, 252, 0.95);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #203c60, #142d4b);
    }

    [data-testid="stSidebar"] * {
        color: #ffffff;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1600px;
    }

    h1, h2, h3 {
        color: #203653;
        letter-spacing: -0.5px;
    }

    .page-subtitle {
        color: #8798ad;
        font-size: 13px;
        margin-top: -10px;
        margin-bottom: 18px;
    }

    .metric-card {
        background: white;
        border: 1px solid #e4ebf4;
        border-radius: 12px;
        padding: 15px 10px;
        text-align: center;
        min-height: 88px;
        box-shadow: 0 2px 8px rgba(27, 57, 91, 0.03);
    }

    .metric-label {
        font-size: 13px;
        color: #71839b;
        margin-bottom: 6px;
    }

    .metric-value {
        font-size: 25px;
        font-weight: 750;
        color: #203653;
    }

    .detail-card {
        background: white;
        border: 1px solid #e1e9f3;
        border-radius: 13px;
        padding: 17px;
        margin-bottom: 12px;
        box-shadow: 0 3px 10px rgba(27, 57, 91, 0.035);
    }

    .student-avatar {
        background: #e7eef8;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
    }

    .student-name {
        font-size: 20px;
        font-weight: 750;
        color: #203653;
    }

    .student-meta {
        font-size: 12px;
        color: #8092a9;
        margin-top: 4px;
    }

    .timer-card {
        background: #fff5f5;
        border: 1px solid #ffd5d8;
        border-radius: 10px;
        padding: 17px 8px;
        text-align: center;
        margin: 12px 0;
    }

    .timer-label {
        color: #e64b55;
        font-weight: 700;
        font-size: 14px;
    }

    .timer-number {
        color: #e64b55;
        font-size: 31px;
        font-weight: 800;
        margin: 3px 0;
    }

    .timer-caption {
        color: #8292a8;
        font-size: 12px;
    }

    .attendance-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        background: #ffffff;
        border: 1px solid #e3ebf4;
        border-radius: 10px;
        overflow: hidden;
        font-size: 12px;
    }

    .attendance-table th {
        background: #f0f5fb;
        color: #506783;
        font-weight: 700;
        padding: 11px 5px;
        text-align: center;
        border-bottom: 1px solid #e3ebf4;
    }

    .attendance-table td {
        padding: 9px 5px;
        text-align: center;
        border-bottom: 1px solid #edf1f6;
        color: #344962;
    }

    .attendance-table tr:last-child td {
        border-bottom: none;
    }

    .attendance-table tr.pending-row {
        background: #fff4f4;
    }

    .status-pill {
        display: inline-block;
        border-radius: 20px;
        padding: 4px 9px;
        font-weight: 700;
        white-space: nowrap;
    }

    .status-present {
        background: #d8f5e8;
        color: #1b9b68;
    }

    .status-late {
        background: #fff0cc;
        color: #bb811b;
    }

    .status-absent {
        background: #ffe0e2;
        color: #e14f59;
    }

    .status-pending {
        background: #ffe0e2;
        color: #e14f59;
    }

    .status-unauthorized {
        background: #e9eef4;
        color: #40566d;
    }

    .timer-pill {
        display: inline-block;
        background: #fff0f1;
        color: #e14f59;
        border: 1px solid #ffc8cd;
        border-radius: 20px;
        padding: 4px 9px;
        font-weight: 750;
    }

    .flow-wrap {
        background: #eef4ff;
        padding: 17px;
        border-radius: 14px;
        border: 1px solid #e4edff;
        margin-top: 15px;
    }

    .flow-card {
        background: #ffffff;
        border-radius: 11px;
        padding: 14px 9px;
        text-align: center;
        min-height: 148px;
        border: 1px solid #edf2fa;
    }

    .flow-number {
        display: inline-block;
        background: #4f80e5;
        color: white;
        border-radius: 50%;
        width: 26px;
        height: 26px;
        line-height: 26px;
        font-weight: 800;
        margin-bottom: 7px;
    }

    .flow-title {
        color: #234e92;
        font-size: 13px;
        font-weight: 750;
        margin-bottom: 8px;
    }

    .flow-description {
        color: #6d819b;
        font-size: 11px;
        line-height: 1.6;
        margin-top: 7px;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e2eaf4;
        padding: 12px;
        border-radius: 12px;
    }

    div[data-testid="stMetricLabel"] {
        color: #71839b;
    }

    div.stButton > button,
    div.stFormSubmitButton > button {
        border-radius: 8px;
        font-weight: 650;
    }

    hr {
        border-color: #e7edf5;
    }

    @media (max-width: 900px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .attendance-table {
            font-size: 10px;
        }

        .attendance-table th,
        .attendance-table td {
            padding: 7px 2px;
        }
    }
</style>
""", unsafe_allow_html=True)


# ==================================================
# 6. 초기화 및 메뉴
# ==================================================

init_db()
process_timers()

if "selected_student_id" not in st.session_state:
    st.session_state.selected_student_id = None

st.sidebar.markdown("## ☑ 출결 관리 시스템")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "메뉴",
    ["출석 현황", "출결 기록", "학생 관리", "설정"],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.caption("학생 출결 관리 대시보드")
st.sidebar.caption("30분 사유 확인 타이머")


# ==================================================
# 7. 출석 현황 대시보드
# ==================================================

if page == "출석 현황":

    st.title("출석 현황")
    st.markdown(
        '<div class="page-subtitle">'
        '학생들의 출석 현황을 확인하고 결석 사유를 관리할 수 있습니다.'
        '</div>',
        unsafe_allow_html=True,
    )

    # 날짜와 학급 선택
    control1, control2, control3 = st.columns([1.2, 1.0, 1.5])

    with control1:
        selected_date = st.date_input(
            "조회 날짜",
            value=date.today(),
            label_visibility="collapsed",
        )

    classes = get_classes()

    with control2:
        selected_class = st.selectbox(
            "학급 선택",
            options=classes if classes else ["전체"],
            label_visibility="collapsed",
        )

    with control3:
        search_name = st.text_input(
            "학생 검색",
            placeholder="학생 이름 검색",
            label_visibility="collapsed",
        )

    students = get_students(selected_class)

    if search_name:
        students = [
            s for s in students
            if search_name.strip().lower() in s["name"].lower()
        ]

    # 학생 수 통계
    present_count = sum(s["status"] == "출석" for s in students)
    late_count = sum(s["status"] == "지각" for s in students)
    absent_count = sum(
        s["status"] in ["결석", "사유 확인 대기"]
        for s in students
    )
    other_count = sum(s["status"] == "무단결석" for s in students)

    m1, m2, m3, m4 = st.columns(4)

    metric_values = [
        ("출석", present_count, "#22a875"),
        ("지각", late_count, "#d99b27"),
        ("결석", absent_count, "#e45660"),
        ("기타", other_count, "#72869d"),
    ]

    for col, (label, value, color) in zip(
        [m1, m2, m3, m4], metric_values
    ):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value" style="color:{color}">
                        {value}
                        <span style="font-size:13px">명</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("")

    left, right = st.columns([1.65, 1.0], gap="medium")

    # ------------------------------------------------
    # 왼쪽: 출결 표
    # ------------------------------------------------

    with left:
        st.subheader("학생별 출결 목록")

        if not students:
            st.info("표시할 학생이 없습니다.")
        else:
            rows_html = ""

            for i, student in enumerate(students, start=1):
                status = student["status"]
                safe_name = html.escape(student["name"])
                safe_reason = html.escape(student["reason"] or "-")
                timer = format_timer(student)

                if status == "출석":
                    badge = '<span class="status-pill status-present">♟ 출석</span>'
                elif status == "지각":
                    badge = '<span class="status-pill status-late">♟ 지각</span>'
                elif status == "결석":
                    badge = '<span class="status-pill status-absent">♟ 결석</span>'
                elif status == "사유 확인 대기":
                    badge = '<span class="status-pill status-pending">♟ 결석</span>'
                else:
                    badge = '<span class="status-pill status-unauthorized">무단결석</span>'

                if status == "사유 확인 대기":
                    reason_cell = f'<span class="timer-pill">◷ {timer}</span>'
                    row_class = "pending-row"
                elif status == "무단결석":
                    reason_cell = '<span class="status-pill status-unauthorized">무단결석</span>'
                    row_class = ""
                else:
                    reason_cell = safe_reason
                    row_class = ""

                rows_html += f"""
                <tr class="{row_class}">
                    <td>{i}</td>
                    <td><b>{safe_name}</b></td>
                    <td>{badge}</td>
                    <td>{reason_cell}</td>
                    <td>-</td>
                </tr>
                """

            st.markdown(
                f"""
                <table class="attendance-table">
                    <thead>
                        <tr>
                            <th>번호</th>
                            <th>이름</th>
                            <th>출석 상태</th>
                            <th>결석 사유 / 타이머</th>
                            <th>비고</th>
                        </tr>
                    </thead>
                    <tbody>{rows_html}</tbody>
                </table>
                """,
                unsafe_allow_html=True,
            )

            st.caption(
                "상세 정보를 확인하려면 오른쪽 패널에서 학생을 선택하세요."
            )

            csv_data = "\ufeff" + "학생 이름,학급,출석 상태,결석 사유\n"

            for s in students:
                values = [
                    s["name"], s["class_name"],
                    s["status"], s["reason"]
                ]
                csv_data += ",".join(
                    '"' + str(v).replace('"', '""') + '"'
                    for v in values
                ) + "\n"

            st.download_button(
                "📥 출결 목록 다운로드",
                data=csv_data.encode("utf-8"),
                file_name=f"출결현황_{selected_date}.csv",
                mime="text/csv",
                use_container_width=True,
            )

    # ------------------------------------------------
    # 오른쪽: 선택 학생 상세 정보
    # ------------------------------------------------

    with right:
        st.subheader("학생 상세 정보")

        if students:
            ids = [s["id"] for s in students]

            if st.session_state.selected_student_id not in ids:
                st.session_state.selected_student_id = ids[0]

            selected_id = st.selectbox(
                "학생 선택",
                options=ids,
                format_func=lambda sid: next(
                    s["name"] for s in students
                    if s["id"] == sid
                ),
                key="dashboard_student_select",
            )

            st.session_state.selected_student_id = selected_id

            selected = next(
                s for s in students
                if s["id"] == selected_id
            )

            safe_name = html.escape(selected["name"])
            safe_class = html.escape(selected["class_name"])
            safe_number = html.escape(
                str(selected["student_number"] or "-")
            )

            st.markdown(
                f"""
                <div class="detail-card">
                    <div style="display:flex;align-items:center;gap:13px">
                        <div class="student-avatar">👤</div>
                        <div>
                            <div class="student-name">{safe_name}</div>
                            <div class="student-meta">
                                {safe_class} · {safe_number}번
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if selected["status"] == "사유 확인 대기":
                st.markdown(
                    f"""
                    <div class="timer-card">
                        <div class="timer-label">◷ 결석 사유 미확인</div>
                        <div class="timer-number">
                            {format_timer(selected)}
                        </div>
                        <div class="timer-caption">
                            30분 이내에 사유가 확인되지 않으면<br>
                            무단결석으로 처리됩니다.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                with st.form("reason_form"):
                    reason = st.text_input(
                        "결석 사유 확인",
                        placeholder="예: 병원 진료, 가정 사정",
                    )

                    if st.form_submit_button(
                        "사유 저장 및 타이머 종료",
                        type="primary",
                        use_container_width=True,
                    ):
                        success, message = confirm_reason(
                            selected_id, reason
                        )

                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)

            else:
                st.markdown(
                    f"""
                    <div class="detail-card">
                        <div style="color:#71839b;font-size:12px">
                            현재 출결 상태
                        </div>
                        <div style="font-size:22px;font-weight:750;
                                    margin:8px 0">
                            {html.escape(selected["status"])}
                        </div>
                        <div style="color:#71839b;font-size:12px">
                            결석 사유: {html.escape(selected["reason"] or "-")}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                with st.expander("출결 상태 수정"):
                    new_status = st.selectbox(
                        "새 출결 상태",
                        [
                            "출석", "지각", "결석",
                            "사유 확인 대기", "무단결석"
                        ],
                        index=[
                            "출석", "지각", "결석",
                            "사유 확인 대기", "무단결석"
                        ].index(selected["status"]),
                        key=f"status_{selected_id}",
                    )

                    if st.button(
                        "출결 상태 저장",
                        use_container_width=True,
                    ):
                        set_status(selected_id, new_status)
                        st.success("출결 상태를 수정했습니다.")
                        st.rerun()

            st.markdown("#### 최근 처리 정보")

            st.markdown(
                f"""
                <div class="detail-card">
                    <div style="font-size:12px;color:#71839b">
                        마지막 수정 시간
                    </div>
                    <div style="font-weight:650;margin-top:5px">
                        {html.escape(selected["updated"])}
                    </div>
                    <hr>
                    <div style="font-size:12px;color:#71839b">
                        결석 사유
                    </div>
                    <div style="margin-top:5px">
                        {html.escape(selected["reason"] or "-")}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.link_button(
                "출결 앱 열기 ↗",
                "https://example.com",
                use_container_width=True,
            )
            st.caption(
                "위 링크는 예시 주소입니다. 실제 출결 앱 주소로 변경하세요."
            )

        else:
            st.info("먼저 학생을 등록해 주세요.")

    # ------------------------------------------------
    # 아래쪽: 출결 처리 흐름
    # ------------------------------------------------

    st.markdown(
        """
        <div class="flow-wrap">
            <h3 style="margin-top:0">출결 처리 흐름</h3>
            <div style="display:grid;
                        grid-template-columns:repeat(5,minmax(0,1fr));
                        gap:10px">
                <div class="flow-card">
                    <div class="flow-number">1</div>
                    <div class="flow-title">결석 확인</div>
                    <div style="font-size:26px">📋</div>
                    <div class="flow-description">
                        교사가 학생의<br>출결 현황을 확인합니다.
                    </div>
                </div>
                <div class="flow-card">
                    <div class="flow-number">2</div>
                    <div class="flow-title">30분 타이머 시작</div>
                    <div style="font-size:26px">⏱️</div>
                    <div class="flow-description">
                        사유가 확인되지 않으면<br>타이머가 작동합니다.
                    </div>
                </div>
                <div class="flow-card">
                    <div class="flow-number">3</div>
                    <div class="flow-title">사유 제출 및 확인</div>
                    <div style="font-size:26px">📱</div>
                    <div class="flow-description">
                        확인된 사유를 입력하면<br>타이머가 종료됩니다.
                    </div>
                </div>
                <div class="flow-card">
                    <div class="flow-number">4</div>
                    <div class="flow-title">사유 기록</div>
                    <div style="font-size:26px">🗂️</div>
                    <div class="flow-description">
                        확인된 사유가<br>학생 정보에 저장됩니다.
                    </div>
                </div>
                <div class="flow-card">
                    <div class="flow-number">5</div>
                    <div class="flow-title">무단결석 처리</div>
                    <div style="font-size:26px">⚠️</div>
                    <div class="flow-description">
                        30분 안에 사유가 확인되지 않으면<br>
                        무단결석 상태로 바뀝니다.
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 타이머가 작동 중이면 1초마다 갱신합니다.
    if any(
        s["status"] == "사유 확인 대기"
        for s in get_students()
    ):
        time.sleep(1)
        st.rerun()


# ==================================================
# 8. 출결 기록
# ==================================================

elif page == "출결 기록":
    st.title("출결 기록")
    st.markdown(
        '<div class="page-subtitle">'
        '현재 결석, 사유 확인 대기, 무단결석 상태인 학생을 확인합니다.'
        '</div>',
        unsafe_allow_html=True,
    )

    classes = get_classes()
    selected_class = st.selectbox(
        "학급 선택",
        ["전체"] + classes,
    )

    students = get_students(selected_class)

    records = [
        s for s in students
        if s["status"] in [
            "결석", "사유 확인 대기", "무단결석"
        ]
    ]

    c1, c2, c3 = st.columns(3)
    c1.metric("결석", sum(s["status"] == "결석" for s in records))
    c2.metric(
        "사유 확인 대기",
        sum(s["status"] == "사유 확인 대기" for s in records),
    )
    c3.metric(
        "무단결석",
        sum(s["status"] == "무단결석" for s in records),
    )

    st.divider()

    if records:
        st.dataframe(
            [
                {
                    "이름": s["name"],
                    "학급": s["class_name"],
                    "상태": s["status"],
                    "결석 사유": s["reason"],
                    "수정 시간": s["updated"],
                }
                for s in records
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("현재 표시할 출결 기록이 없습니다.")

    st.caption(
        "현재 버전은 학생별 최신 상태를 보여 줍니다. "
        "날짜별 과거 기록을 누적하는 기능은 별도로 구현해야 합니다."
    )


# ==================================================
# 9. 학생 관리
# ==================================================

elif page == "학생 관리":
    st.title("학생 관리")
    st.markdown(
        '<div class="page-subtitle">'
        '학생을 등록하고 이름, 학급, 번호를 수정하거나 삭제합니다.'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.expander("➕ 새 학생 등록", expanded=True):
        with st.form("add_student_form"):
            new_name = st.text_input("학생 이름")
            new_class = st.text_input(
                "학급",
                value="2학년 3반",
            )
            new_number = st.text_input("번호")

            submitted = st.form_submit_button(
                "학생 등록",
                type="primary",
                use_container_width=True,
            )

            if submitted:
                success, message = add_student(
                    new_name, new_class, new_number
                )

                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    st.divider()

    students = get_students()

    if students:
        st.subheader("✏️ 학생 정보 수정")

        selected_id = st.selectbox(
            "수정할 학생",
            options=[s["id"] for s in students],
            format_func=lambda sid: next(
                s["name"] for s in students
                if s["id"] == sid
            ),
            key="management_edit_id",
        )

        selected = next(
            s for s in students
            if s["id"] == selected_id
        )

        with st.form("edit_student_form"):
            edited_name = st.text_input(
                "학생 이름",
                value=selected["name"],
                key=f"edit_name_{selected_id}",
            )
            edited_class = st.text_input(
                "학급",
                value=selected["class_name"],
                key=f"edit_class_{selected_id}",
            )
            edited_number = st.text_input(
                "번호",
                value=str(selected["student_number"] or ""),
                key=f"edit_number_{selected_id}",
            )

            edit_submitted = st.form_submit_button(
                "수정 내용 저장",
                type="primary",
                use_container_width=True,
            )

            if edit_submitted:
                success, message = rename_student(
                    selected_id,
                    edited_name,
                    edited_class,
                    edited_number,
                )

                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

        st.divider()
        st.subheader("🗑️ 학생 삭제")

        st.warning(
            "삭제하면 해당 학생의 현재 출결 정보도 함께 삭제됩니다."
        )

        with st.form("delete_student_form"):
            st.write(f"삭제할 학생: **{selected['name']}**")

            confirm_delete = st.checkbox(
                "이 학생을 삭제하는 것에 동의합니다."
            )

            delete_submitted = st.form_submit_button(
                "학생 삭제",
                use_container_width=True,
            )

            if delete_submitted:
                if not confirm_delete:
                    st.error("삭제 확인란을 먼저 체크해 주세요.")
                else:
                    success, message = delete_student(selected_id)

                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

        st.divider()
        st.subheader("📋 등록된 학생 목록")

        st.dataframe(
            [
                {
                    "이름": s["name"],
                    "학급": s["class_name"],
                    "번호": s["student_number"],
                    "출결 상태": s["status"],
                    "결석 사유": s["reason"],
                }
                for s in get_students()
            ],
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("등록된 학생이 없습니다.")


# ==================================================
# 10. 설정
# ==================================================

elif page == "설정":
    st.title("설정")
    st.markdown(
        '<div class="page-subtitle">'
        '출결 관리 시스템의 기본 설정을 확인합니다.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.subheader("타이머 설정")
    st.info("현재 사유 확인 제한 시간은 30분입니다.")

    st.subheader("데이터 관리")
    st.warning(
        "이 버전은 SQLite 파일에 데이터를 저장합니다. "
        "Streamlit Cloud에서 재배포하거나 실행 환경이 바뀌면 "
        "데이터가 유지되지 않을 수 있습니다."
    )

    st.subheader("시스템 안내")
    st.write(
        "- 현재 학생별 최신 출결 상태를 저장합니다.\n"
        "- 실제 학교 출결 앱과 자동으로 연결되어 있지는 않습니다.\n"
        "- 실제 학생 정보를 사용할 때는 로그인과 접근 권한 보호가 필요합니다.\n"
        "- 학교의 공식 출결 처리 규정에 맞게 상태 명칭과 처리 절차를 확인하세요."
    )
