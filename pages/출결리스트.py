
import streamlit as st
import pandas as pd
import sqlite3
import time
from datetime import datetime
from pathlib import Path

# =========================================
# 1. 기본 설정
# =========================================

st.set_page_config(
    page_title="학생 출결 관리 시스템",
    page_icon="📋",
    layout="wide",
)

DB_PATH = Path(__file__).parent / "attendance.db"
TIME_LIMIT = 30 * 60  # 30분 = 1800초


# =========================================
# 2. 데이터베이스 설정
# =========================================

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
                status TEXT NOT NULL DEFAULT '출석',
                reason TEXT NOT NULL DEFAULT '-',
                started REAL,
                updated TEXT NOT NULL
            )
        """)

        # 처음 실행했을 때만 예시 학생을 등록합니다.
        count = conn.execute(
            "SELECT COUNT(*) FROM students"
        ).fetchone()[0]

        if count == 0:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sample_names = ["김민준", "이서연", "박지우", "최도윤", "정하은"]

            for name in sample_names:
                conn.execute(
                    """
                    INSERT INTO students
                    (name, status, reason, started, updated)
                    VALUES (?, '출석', '-', NULL, ?)
                    """,
                    (name, now),
                )


def get_students():
    with connect_db() as conn:
        rows = conn.execute(
            "SELECT * FROM students ORDER BY id"
        ).fetchall()

    return [dict(row) for row in rows]


# =========================================
# 3. 학생 정보 추가, 수정, 삭제
# =========================================

def add_student(name):
    name = name.strip()

    if not name:
        return False, "학생 이름을 입력해 주세요."

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with connect_db() as conn:
            conn.execute(
                """
                INSERT INTO students
                (name, status, reason, started, updated)
                VALUES (?, '출석', '-', NULL, ?)
                """,
                (name, now),
            )

        return True, f"'{name}' 학생을 등록했습니다."

    except sqlite3.IntegrityError:
        return False, "이미 등록된 이름입니다."


def rename_student(student_id, new_name):
    new_name = new_name.strip()

    if not new_name:
        return False, "새로운 이름을 입력해 주세요."

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with connect_db() as conn:
            cursor = conn.execute(
                """
                UPDATE students
                SET name = ?, updated = ?
                WHERE id = ?
                """,
                (new_name, now, student_id),
            )

            if cursor.rowcount == 0:
                return False, "학생 정보를 찾을 수 없습니다."

        return True, f"학생 이름을 '{new_name}'으로 수정했습니다."

    except sqlite3.IntegrityError:
        return False, "이미 등록된 이름입니다."


def delete_student(student_id):
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


# =========================================
# 4. 출결 상태 변경 및 사유 저장
# =========================================

def update_student(student_id, status, reason="-", started=None):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with connect_db() as conn:
        conn.execute(
            """
            UPDATE students
            SET status = ?, reason = ?, started = ?, updated = ?
            WHERE id = ?
            """,
            (status, reason, started, now, student_id),
        )


def start_pending_absence(student_id):
    # 결석 사유가 확인되지 않은 시점부터 타이머를 시작합니다.
    update_student(
        student_id,
        status="사유 확인 대기",
        reason="사유 미확인",
        started=time.time(),
    )


def confirm_absence_reason(student_id, reason):
    reason = reason.strip()

    if not reason:
        return False, "결석 사유를 입력해 주세요."

    update_student(
        student_id,
        status="결석",
        reason=reason,
        started=None,
    )

    return True, "결석 사유를 저장했습니다. 타이머가 종료되었습니다."


def process_timers():
    # 사유 확인 대기 상태인 학생을 검사합니다.
    students = get_students()
    now = time.time()

    for student in students:
        if student["status"] != "사유 확인 대기":
            continue

        started = student["started"]

        if started is None:
            continue

        if now - started >= TIME_LIMIT:
            update_student(
                student["id"],
                status="무단 결과",
                reason="30분 내 사유 미확인",
                started=None,
            )


def format_remaining(student):
    started = student["started"]

    if started is None:
        return "-"

    remaining = max(
        0,
        TIME_LIMIT - int(time.time() - started),
    )

    minutes = remaining // 60
    seconds = remaining % 60

    return f"{minutes:02d}:{seconds:02d}"


# =========================================
# 5. 화면 디자인
# =========================================

st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    div[data-testid="stMetric"] {
        background: #f5f7fb;
        border: 1px solid #e5e9f2;
        padding: 16px;
        border-radius: 12px;
    }

    div.stButton > button {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


# =========================================
# 6. 앱 초기화 및 메뉴
# =========================================

init_db()
process_timers()

st.sidebar.title("📋 출결 관리 시스템")
st.sidebar.caption("학생 출결 현황을 확인하고 관리합니다.")

page = st.sidebar.radio(
    "메뉴",
    ["출석 현황", "학생 관리", "출결 기록"],
)

st.sidebar.divider()
st.sidebar.caption("결석 사유 확인 제한 시간: 30분")


# =========================================
# 7. 출석 현황
# =========================================

if page == "출석 현황":
    st.title("📋 출석 현황")
    st.caption("학생들의 출결 상태와 결석 사유 확인 시간을 관리합니다.")

    students = get_students()

    total = len(students)
    present = sum(s["status"] == "출석" for s in students)
    pending = sum(s["status"] == "사유 확인 대기" for s in students)
    unauthorized = sum(s["status"] == "무단 결과" for s in students)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("전체 학생", f"{total}명")
    col2.metric("출석", f"{present}명")
    col3.metric("사유 확인 대기", f"{pending}명")
    col4.metric("무단 결과", f"{unauthorized}명")

    st.divider()

    # 학생 검색 및 상태 필터
    search_col, filter_col = st.columns([2, 1])

    with search_col:
        keyword = st.text_input(
            "🔎 학생 검색",
            placeholder="학생 이름을 입력하세요.",
        )

    with filter_col:
        status_filter = st.selectbox(
            "출결 상태 필터",
            [
                "전체",
                "출석",
                "사유 확인 대기",
                "결석",
                "무단 결과",
            ],
        )

    filtered = students

    if keyword:
        filtered = [
            s for s in filtered
            if keyword.lower() in s["name"].lower()
        ]

    if status_filter != "전체":
        filtered = [
            s for s in filtered
            if s["status"] == status_filter
        ]

    st.subheader("학생별 출결 목록")

    if filtered:
        table_data = []

        for i, student in enumerate(filtered, start=1):
            table_data.append({
                "번호": i,
                "학생 이름": student["name"],
                "출결 상태": student["status"],
                "결석 사유": student["reason"],
                "남은 시간": (
                    format_remaining(student)
                    if student["status"] == "사유 확인 대기"
                    else "-"
                ),
                "최근 수정": student["updated"],
            })

        st.dataframe(
            pd.DataFrame(table_data),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("조건에 맞는 학생이 없습니다.")

    # CSV 파일 다운로드
    if filtered:
        csv_data = pd.DataFrame([
            {
                "학생 이름": s["name"],
                "출결 상태": s["status"],
                "결석 사유": s["reason"],
                "최근 수정": s["updated"],
            }
            for s in filtered
        ]).to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            "📥 출결 목록 CSV 다운로드",
            data=csv_data,
            file_name="출결_현황.csv",
            mime="text/csv",
        )

    st.divider()

    # 결석 사유 확인
    st.subheader("📝 결석 사유 확인")

    pending_students = [
        s for s in students
        if s["status"] == "사유 확인 대기"
    ]

    if pending_students:
        st.warning(
            "사유 확인 대기 중인 학생이 있습니다. "
            "30분 안에 사유를 확인해 주세요."
        )

        selected_pending_id = st.selectbox(
            "사유를 확인할 학생",
            options=[s["id"] for s in pending_students],
            format_func=lambda sid: next(
                s["name"] for s in pending_students
                if s["id"] == sid
            ),
            key="pending_student_id",
        )

        with st.form("confirm_reason_form"):
            reason = st.text_input(
                "확인된 결석 사유",
                placeholder="예: 병원 진료, 가정 사정 등",
            )

            reason_submitted = st.form_submit_button(
                "사유 저장 및 타이머 종료",
                type="primary",
                use_container_width=True,
            )

            if reason_submitted:
                success, message = confirm_absence_reason(
                    selected_pending_id,
                    reason,
                )

                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    else:
        st.info("현재 사유 확인 대기 중인 학생이 없습니다.")

    # 테스트용 결석 등록
    st.divider()
    st.subheader("🧪 결석 사유 확인 대기 등록")
    st.caption(
        "테스트용 기능입니다. 실제 출결 앱과 자동으로 연결된 기능은 아닙니다."
    )

    all_students = get_students()
    eligible_students = [
        s for s in all_students
        if s["status"] == "출석"
    ]

    if eligible_students:
        with st.form("pending_absence_form"):
            selected_absence_id = st.selectbox(
                "학생 선택",
                options=[s["id"] for s in eligible_students],
                format_func=lambda sid: next(
                    s["name"] for s in eligible_students
                    if s["id"] == sid
                ),
                key="absence_student_id",
            )

            absence_submitted = st.form_submit_button(
                "사유 확인 대기 시작",
                use_container_width=True,
            )

            if absence_submitted:
                start_pending_absence(selected_absence_id)
                st.success("30분 타이머를 시작했습니다.")
                st.rerun()
    else:
        st.info("등록된 출석 학생이 없거나 모든 학생이 다른 상태입니다.")

    # 대기 중인 학생이 있으면 화면을 1초마다 새로고침합니다.
    # 새로고침할 때마다 위에서 타이머 만료 여부를 확인합니다.
    if any(
        s["status"] == "사유 확인 대기"
        for s in get_students()
    ):
        time.sleep(1)
        st.rerun()


# =========================================
# 8. 학생 관리
# =========================================

elif page == "학생 관리":
    st.title("👥 학생 관리")
    st.caption("학생을 등록하고, 이름을 수정하거나 삭제할 수 있습니다.")

    # -------------------------------------
    # 학생 등록
    # -------------------------------------

    with st.expander("➕ 새 학생 등록", expanded=True):
        with st.form("add_student_form"):
            new_name = st.text_input(
                "학생 이름",
                placeholder="등록할 학생의 이름을 입력하세요.",
            )

            add_submitted = st.form_submit_button(
                "학생 등록",
                type="primary",
                use_container_width=True,
            )

            if add_submitted:
                success, message = add_student(new_name)

                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    st.divider()

    students = get_students()

    st.subheader("✏️ 학생 이름 수정")

    if not students:
        st.info("등록된 학생이 없습니다.")

    else:
        selected_id = st.selectbox(
            "수정할 학생 선택",
            options=[s["id"] for s in students],
            format_func=lambda sid: next(
                s["name"] for s in students
                if s["id"] == sid
            ),
            key="edit_student_id",
        )

        selected = next(
            s for s in students
            if s["id"] == selected_id
        )

        with st.form("edit_student_form"):
            edited_name = st.text_input(
                "새 학생 이름",
                value=selected["name"],
                key=f"edit_name_{selected_id}",
            )

            edit_submitted = st.form_submit_button(
                "이름 수정 저장",
                type="primary",
                use_container_width=True,
            )

            if edit_submitted:
                success, message = rename_student(
                    selected_id,
                    edited_name,
                )

                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

        st.divider()

        # ---------------------------------
        # 학생 삭제
        # ---------------------------------

        st.subheader("🗑️ 학생 삭제")

        st.warning(
            "삭제하면 해당 학생의 현재 출결 정보도 함께 삭제됩니다. "
            "삭제 전에 학생 이름을 꼭 확인하세요."
        )

        with st.form("delete_student_form"):
            st.write(f"삭제할 학생: **{selected['name']}**")

            confirm_delete = st.checkbox(
                "선택한 학생을 삭제하는 것에 동의합니다."
            )

            delete_submitted = st.form_submit_button(
                "학생 삭제",
                use_container_width=True,
            )

            if delete_submitted:
                if not confirm_delete:
                    st.error("삭제 확인란을 먼저 선택해 주세요.")
                else:
                    success, message = delete_student(selected_id)

                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

    st.divider()

    # -------------------------------------
    # 현재 학생 목록
    # -------------------------------------

    st.subheader("📋 등록된 학생 목록")

    students = get_students()

    if students:
        st.dataframe(
            pd.DataFrame([
                {
                    "번호": i + 1,
                    "학생 이름": s["name"],
                    "출결 상태": s["status"],
                    "결석 사유": s["reason"],
                }
                for i, s in enumerate(students)
            ]),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("등록된 학생이 없습니다.")


# =========================================
# 9. 출결 기록
# =========================================

elif page == "출결 기록":
    st.title("🗂️ 출결 기록")
    st.caption("현재 결석 또는 무단 결과 상태인 학생을 확인합니다.")

    students = get_students()

    records = [
        s for s in students
        if s["status"] in ["결석", "무단 결과", "사유 확인 대기"]
    ]

    col1, col2 = st.columns(2)

    col1.metric(
        "결석 및 사유 확인 대기",
        f"{sum(s['status'] in ['결석', '사유 확인 대기'] for s in records)}명",
    )

    col2.metric(
        "무단 결과",
        f"{sum(s['status'] == '무단 결과' for s in records)}명",
    )

    st.divider()

    if records:
        st.dataframe(
            pd.DataFrame([
                {
                    "학생 이름": s["name"],
                    "출결 상태": s["status"],
                    "결석 사유": s["reason"],
                    "최근 수정": s["updated"],
                }
                for s in records
            ]),
            use_container_width=True,
            hide_index=True,
        )

        csv_data = pd.DataFrame([
            {
                "학생 이름": s["name"],
                "출결 상태": s["status"],
                "결석 사유": s["reason"],
                "최근 수정": s["updated"],
            }
            for s in records
        ]).to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            "📥 출결 기록 CSV 다운로드",
            data=csv_data,
            file_name="출결_기록.csv",
            mime="text/csv",
        )
    else:
        st.info("현재 표시할 결석 기록이 없습니다.")

    st.caption(
        "참고: 이 화면은 현재 학생 정보에 저장된 상태를 보여줍니다. "
        "날짜별로 누적되는 영구 출결 이력은 아직 구현되지 않았습니다."
    )


