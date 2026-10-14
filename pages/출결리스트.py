

import sqlite3
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st


# =========================================
# 1. 기본 설정
# =========================================
st.set_page_config(
    page_title="스마트 출결 관리",
    page_icon="📋",
    layout="wide",
)

DB_PATH = Path(__file__).resolve().parent / "attendance.db"
TIME_LIMIT = 30 * 60

STATUS_OPTIONS = ["출석", "지각", "결석", "무단 결과"]


# =========================================
# 2. 디자인
# =========================================
st.markdown("""
<style>
.stApp {
    background: #F4F7FB;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}
[data-testid="stSidebar"] {
    background: #17365D;
}
[data-testid="stSidebar"] * {
    color: white;
}
.dashboard-title {
    color: #17365D;
    font-size: 32px;
    font-weight: 800;
}
.dashboard-subtitle {
    color: #758399;
    margin-bottom: 20px;
}
.metric-card {
    background: white;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #E4EAF2;
}
.metric-label {
    color: #758399;
    font-size: 14px;
}
.metric-number {
    color: #17365D;
    font-size: 30px;
    font-weight: 800;
}
div.stButton > button {
    border-radius: 9px;
}
</style>
""", unsafe_allow_html=True)


# =========================================
# 3. 데이터베이스
# =========================================
def connect_db():
    conn = sqlite3.connect(
        str(DB_PATH),
        timeout=10,
    )
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL DEFAULT '출석',
                reason TEXT NOT NULL DEFAULT '-',
                started REAL,
                updated TEXT NOT NULL
            )
        """)

        count = conn.execute(
            "SELECT COUNT(*) FROM students"
        ).fetchone()[0]

        if count == 0:
            now = time.time()
            today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            demo_students = [
                ("김도현", "출석", "-", None, today),
                ("이서연", "출석", "-", None, today),
                ("박지민", "출석", "-", None, today),
                ("최예은", "지각", "-", None, today),
                ("정민준", "출석", "-", None, today),
                ("한지민", "결석", "미확인", now, today),
                ("강민서", "출석", "-", None, today),
                ("이준호", "출석", "-", None, today),
                ("유나영", "결석", "질병(감기)", None, today),
                ("신동우", "출석", "-", None, today),
            ]

            conn.executemany("""
                INSERT OR IGNORE INTO students
                (name, status, reason, started, updated)
                VALUES (?, ?, ?, ?, ?)
            """, demo_students)


def get_students():
    with connect_db() as conn:
        rows = conn.execute("""
            SELECT id, name, status, reason, started, updated
            FROM students
            ORDER BY id
        """).fetchall()
    return [dict(row) for row in rows]


def update_student(student_id, status, reason, started):
    updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with connect_db() as conn:
        conn.execute("""
            UPDATE students
            SET status = ?, reason = ?, started = ?, updated = ?
            WHERE id = ?
        """, (status, reason, started, updated, student_id))


def add_student(name):
def rename_student(student_id, new_name):
    """학생 이름을 변경합니다."""
    new_name = new_name.strip()

    if not new_name:
        return False, "새로운 이름을 입력해 주세요."

    try:
        updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with connect_db() as conn:
            cursor = conn.execute(
                """
                UPDATE students
                SET name = ?, updated = ?
                WHERE id = ?
                """,
                (new_name, updated, student_id),
            )

            if cursor.rowcount == 0:
                return False, "학생 정보를 찾을 수 없습니다."

        return True, f"학생 이름을 '{new_name}'으로 변경했습니다."

    except sqlite3.IntegrityError:
        return False, "이미 등록된 이름입니다."


def delete_student(student_id):
    """선택한 학생을 데이터베이스에서 삭제합니다."""
    try:
        with connect_db() as conn:
            cursor = conn.execute(
                "DELETE FROM students WHERE id = ?",
                (student_id,),
            )

            if cursor.rowcount == 0:
                return False, "학생 정보를 찾을 수 없습니다."

        return True, "학생을 삭제했습니다."

    except sqlite3.Error:
        return False, "삭제에 실패했습니다. 다시 시도해 주세요."

    name = name.strip()

    if not name:
        return False, "학생 이름을 입력해 주세요."

    try:
        updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with connect_db() as conn:
            conn.execute("""
                INSERT INTO students
                (name, status, reason, started, updated)
                VALUES (?, '출석', '-', NULL, ?)
            """, (name, updated))

        return True, f"{name} 학생을 등록했습니다."

    except sqlite3.IntegrityError:
        return False, "이미 등록된 학생 이름입니다."


# =========================================
# 4. 타이머 처리
# =========================================
def process_timers():
    now = time.time()
    students = get_students()

    for student in students:
        if (
            student["status"] == "결석"
            and student["reason"] == "미확인"
            and student["started"] is not None
            and now - student["started"] >= TIME_LIMIT
        ):
            update_student(
                student["id"],
                "무단 결과",
                "30분 내 사유 미확인",
                None,
            )


def format_remaining(student):
    if (
        student["status"] != "결석"
        or student["reason"] != "미확인"
        or student["started"] is None
    ):
        return "-"

    remaining = max(
        0,
        TIME_LIMIT - int(time.time() - student["started"]),
    )

    return f"{remaining // 60:02d}:{remaining % 60:02d}"


# =========================================
# 5. 안전한 초기화
# =========================================
try:
    init_db()
    process_timers()
except (sqlite3.Error, OSError) as exc:
    st.error("데이터베이스를 준비하지 못했습니다.")
    st.caption(f"오류 내용: {exc}")
    st.stop()


# =========================================
# 6. 사이드바
# =========================================
with st.sidebar:
    st.markdown("## 📋 스마트 출결")
    st.caption("SCHOOL ATTENDANCE")
    st.divider()

    page = st.radio(
        "메뉴",
        ["출석 현황", "학생 관리", "출결 기록"],
    )

    st.divider()
    st.caption("시제품 · 가상 데이터")


# =========================================
# 7. 출석 현황
# =========================================
if page == "출석 현황":
    st.markdown(
        '<div class="dashboard-title">출석 현황</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="dashboard-subtitle">'
        '학생들의 출결 상태와 결석 사유를 관리합니다.'
        '</div>',
        unsafe_allow_html=True,
    )

    students = get_students()

    counts = {
        status: sum(
            s["status"] == status for s in students
        )
        for status in STATUS_OPTIONS
    }

    cols = st.columns(4)

    icons = {
        "출석": "🟢",
        "지각": "🟠",
        "결석": "🔴",
        "무단 결과": "⚠️",
    }

    for col, status in zip(cols, STATUS_OPTIONS):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">
                        {icons[status]} {status}
                    </div>
                    <div class="metric-number">
                        {counts[status]}명
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")

    search_col, filter_col = st.columns([2, 1])

    with search_col:
        keyword = st.text_input(
            "🔎 학생 검색",
            placeholder="이름으로 검색",
        )

    with filter_col:
        status_filter = st.selectbox(
            "출결 상태",
            ["전체"] + STATUS_OPTIONS,
        )

    filtered = []

    for s in students:
        if keyword and keyword not in s["name"]:
            continue
        if status_filter != "전체" and s["status"] != status_filter:
            continue
        filtered.append(s)

    table_rows = [
        {
            "학생 이름": s["name"],
            "출결 상태": s["status"],
            "결석 사유": s["reason"],
            "남은 시간": format_remaining(s),
            "최근 변경": s["updated"],
        }
        for s in filtered
    ]

    st.subheader("학생 출결 목록")

    st.dataframe(
        pd.DataFrame(
            table_rows,
            columns=[
                "학생 이름",
                "출결 상태",
                "결석 사유",
                "남은 시간",
                "최근 변경",
            ],
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.caption(f"총 {len(filtered)}명 표시")

    # CSV 내려받기
    csv_data = pd.DataFrame(table_rows).to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "📥 출결 현황 CSV 다운로드",
        data=csv_data,
        file_name=f"attendance_{datetime.now():%Y%m%d}.csv",
        mime="text/csv",
    )

    st.divider()
    st.subheader("⏱️ 결석 사유 확인")

    unresolved = [
        s for s in students
        if s["status"] == "결석"
        and s["reason"] == "미확인"
    ]

    if unresolved:
        selected_id = st.selectbox(
            "확인할 학생",
            options=[s["id"] for s in unresolved],
            format_func=lambda sid: next(
                s["name"] for s in unresolved
                if s["id"] == sid
            ),
        )

        selected = next(
            s for s in unresolved
            if s["id"] == selected_id
        )

        st.warning(
            f"{selected['name']} 학생의 결석 사유가 확인되지 않았습니다."
        )

        st.metric("남은 시간", format_remaining(selected))

        with st.form("reason_form"):
            reason = st.text_input(
                "확인된 결석 사유",
                placeholder="예: 질병, 병원 진료",
            )

            confirmed = st.form_submit_button(
                "사유 확인 완료",
                type="primary",
            )

            if confirmed:
                if reason.strip():
                    update_student(
                        selected["id"],
                        "결석",
                        reason.strip(),
                        None,
                    )
                    st.success("결석 사유를 기록했습니다.")
                    st.rerun()
                else:
                    st.error("사유를 입력해 주세요.")

    else:
        st.success("확인 대기 중인 결석이 없습니다.")

    # 테스트용 결석 등록
    with st.expander("🧪 테스트: 미확인 결석 등록"):
        eligible = [
            s for s in students
            if s["status"] in ["출석", "지각"]
        ]

        if eligible:
            target_id = st.selectbox(
                "학생 선택",
                options=[s["id"] for s in eligible],
                format_func=lambda sid: next(
                    s["name"] for s in eligible
                    if s["id"] == sid
                ),
                key="absent_student",
            )

            if st.button("30분 타이머 시작"):
                target = next(
                    s for s in eligible
                    if s["id"] == target_id
                )
                update_student(
                    target["id"],
                    "결석",
                    "미확인",
                    time.time(),
                )
                st.rerun()

    # 미확인 결석이 있을 때만 주기적으로 갱신
    if unresolved:
        time.sleep(1)
        st.rerun()


# =========================================
# 8. 학생 관리
# =========================================
elif page == "학생 관리":
    st.title("👥 학생 관리")
    st.caption("학생을 등록하고 목록을 확인합니다.")

    with st.form("add_student_form"):
        new_name = st.text_input(
            "학생 이름",
            placeholder="이름 입력",
        )
        add_submitted = st.form_submit_button(
            "학생 등록",
            type="primary",
        )

        if add_submitted:
            success, message = add_student(new_name)

            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    students = get_students()

    st.subheader("등록된 학생")

    st.dataframe(
        pd.DataFrame([
            {
                "번호": i + 1,
                "이름": s["name"],
                "출결 상태": s["status"],
            }
            for i, s in enumerate(students)
        ]),
        use_container_width=True,
        hide_index=True,
    )


# =========================================
# 9. 출결 기록
# =========================================
elif page == "출결 기록":
    st.title("🗂️ 출결 기록")
    st.caption("현재 학생별 출결 상태와 사유를 확인합니다.")

    students = get_students()

    records = [
        {
            "학생 이름": s["name"],
            "출결 상태": s["status"],
            "결석 사유": s["reason"],
            "최근 변경": s["updated"],
        }
        for s in students
        if s["status"] != "출석" or s["reason"] != "-"
    ]

    if records:
        st.dataframe(
            pd.DataFrame(records),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("표시할 기록이 없습니다.")

st.caption(
    "스마트 출결 관리 시제품 | 예시 데이터 사용"
)
