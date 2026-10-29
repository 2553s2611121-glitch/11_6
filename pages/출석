
import streamlit as st
import sqlite3
from datetime import datetime, date, timedelta

st.set_page_config(
    page_title="지각알리미.py",
    page_icon="⏰",
    layout="wide"
)

DB = "jigak.db"

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                class_name TEXT NOT NULL,
                student_phone TEXT,
                parent_phone TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                report_date TEXT,
                reason TEXT DEFAULT '',
                detail TEXT DEFAULT '',
                status TEXT DEFAULT '응답 대기',
                due_at TEXT,
                FOREIGN KEY(student_id) REFERENCES students(id)
            )
        """)

def get_students():
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(
            "SELECT * FROM students ORDER BY class_name, name"
        ).fetchall()

def get_reports():
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute("""
            SELECT r.*, s.name, s.class_name
            FROM reports r
            JOIN students s ON s.id = r.student_id
            ORDER BY r.id DESC
        """).fetchall()

init_db()

st.title("⏰ 지각알리미.py")
st.caption("학생과 보호자를 위한 지각·결석 사유 관리 시스템")

page = st.sidebar.radio(
    "메뉴",
    ["대시보드", "학생 관리", "지각 사유 등록", "사유 설문", "응답 현황"]
)

# 설문 링크 접속 처리
if "survey" in st.query_params:
    report_id = int(st.query_params["survey"])

    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        report = conn.execute("""
            SELECT r.*, s.name, s.class_name
            FROM reports r
            JOIN students s ON s.id = r.student_id
            WHERE r.id = ?
        """, (report_id,)).fetchone()

    st.header("지각 사유 설문")

    if report is None:
        st.error("유효하지 않은 설문 링크입니다.")
    elif report["status"] == "응답 완료":
        st.success("이미 제출된 설문입니다.")
    else:
        st.write(f"학생: {report['class_name']} {report['name']}")
        st.write(f"날짜: {report['report_date']}")

        with st.form("survey_form"):
            reason = st.selectbox(
                "지각 또는 결석 사유",
                ["교통 문제", "건강 문제", "가정 사정", "개인 사정", "기타"]
            )
            detail = st.text_area("추가 설명 (선택)")
            respondent = st.radio(
                "응답자", ["학생", "보호자"],
                horizontal=True
            )
            submit = st.form_submit_button("설문 제출")

        if submit:
            with sqlite3.connect(DB) as conn:
                conn.execute("""
                    UPDATE reports
                    SET reason = ?, detail = ?, status = '응답 완료'
                    WHERE id = ?
                """, (
                    reason,
                    f"응답자: {respondent}\n{detail}",
                    report_id
                ))
            st.success("설문이 제출되었습니다.")
    st.stop()


if page == "대시보드":
    reports = get_reports()
    now = datetime.now()

    pending = [
        r for r in reports
        if r["status"] == "응답 대기"
    ]
    overdue = [
        r for r in pending
        if r["due_at"] and
        datetime.fromisoformat(r["due_at"]) < now
    ]

    a, b, c = st.columns(3)
    a.metric("전체 요청", len(reports))
    b.metric("응답 대기", len(pending))
    c.metric("기한 경과 · 확인 필요", len(overdue))

    st.subheader("최근 요청")
    for r in reports[:10]:
        st.write(
            f"**{r['class_name']} {r['name']}** · "
            f"{r['report_date']} · {r['status']}"
        )

elif page == "학생 관리":
    st.header("학생 관리")

    with st.form("student_form", clear_on_submit=True):
        name = st.text_input("학생 이름")
        class_name = st.text_input("학급 (예: 1-3)")
        student_phone = st.text_input("학생 전화번호")
        parent_phone = st.text_input("보호자 전화번호")
        save = st.form_submit_button("학생 등록")

    if save:
        if not name.strip() or not class_name.strip():
            st.error("학생 이름과 학급을 입력해 주세요.")
        else:
            with sqlite3.connect(DB) as conn:
                conn.execute("""
                    INSERT INTO students
                    (name, class_name, student_phone, parent_phone)
                    VALUES (?, ?, ?, ?)
                """, (
                    name.strip(), class_name.strip(),
                    student_phone.strip(), parent_phone.strip()
                ))
            st.success("학생이 등록되었습니다.")
            st.rerun()

    st.subheader("등록된 학생")
    students = get_students()

    if students:
        st.dataframe([
            {
                "학급": s["class_name"],
                "이름": s["name"],
                "학생 연락처": "등록됨" if s["student_phone"] else "미등록",
                "보호자 연락처": "등록됨" if s["parent_phone"] else "미등록"
            }
            for s in students
        ], use_container_width=True, hide_index=True)
    else:
        st.info("등록된 학생이 없습니다.")

elif page == "지각 사유 등록":
    st.header("지각·결석 사유 요청 등록")
    students = get_students()

    if not students:
        st.warning("먼저 학생을 등록해 주세요.")
    else:
        options = {
            f"{s['class_name']} {s['name']} (ID {s['id']})": s["id"]
            for s in students
        }

        with st.form("report_form"):
            student = st.selectbox("학생 선택", list(options.keys()))
            report_date = st.date_input("지각·결석 날짜", date.today())
            due_date = st.date_input(
                "응답 마감일", date.today() + timedelta(days=1)
            )
            due_time = st.time_input(
                "응답 마감 시간",
                datetime.strptime("18:00", "%H:%M").time()
            )
            create = st.form_submit_button("요청 등록")

        if create:
            due_at = datetime.combine(
                due_date, due_time
            ).isoformat(timespec="minutes")

            with sqlite3.connect(DB) as conn:
                conn.execute("""
                    INSERT INTO reports
                    (student_id, report_date, status, due_at)
                    VALUES (?, ?, '응답 대기', ?)
                """, (
                    options[student], report_date.isoformat(), due_at
                ))
                report_id = conn.execute(
                    "SELECT last_insert_rowid()"
                ).fetchone()[0]

            st.success(f"요청 등록 완료! 요청 번호: {report_id}")
            st.code(
                f"{st.get_option('server.baseUrlPath')}"
                f"?survey={report_id}"
            )
            st.info(
                "실제 배포 후에는 브라우저 주소와 "
                f"?survey={report_id}를 합쳐 설문 링크를 만드세요."
            )

elif page == "사유 설문":
    st.header("설문 링크 확인")
    reports = get_reports()

    if reports:
        for r in reports:
            st.write(
                f"요청 #{r['id']} · {r['class_name']} "
                f"{r['name']} · {r['report_date']}"
            )
            st.code(f"?survey={r['id']}")
    else:
        st.info("등록된 요청이 없습니다.")

elif page == "응답 현황":
    st.header("응답 현황")

    reports = get_reports()
    now = datetime.now()

    if not reports:
        st.info("등록된 요청이 없습니다.")

    for r in reports:
        expired = (
            r["status"] == "응답 대기"
            and r["due_at"]
            and datetime.fromisoformat(r["due_at"]) < now
        )

        status = (
            "기한 경과 · 확인 필요" if expired
            else r["status"]
        )

        with st.expander(
            f"{r['class_name']} {r['name']} · "
            f"{r['report_date']} · {status}"
        ):
            st.write("마감:", r["due_at"])
            if r["status"] == "응답 완료":
                st.write("사유:", r["reason"])
                st.write("설명:", r["detail"])
            elif expired:
                st.warning(
                    "마감 시간이 지났습니다. "
                    "담당 교사가 확인한 뒤 처리하세요."
                )

            if r["status"] == "응답 완료":
                if st.button("응답 대기로 변경", key=f"reset_{r['id']}"):
                    with sqlite3.connect(DB) as conn:
                        conn.execute(
                            "UPDATE reports SET status='응답 대기' WHERE id=?",
                            (r["id"],)
                        )
                    st.rerun()

st.sidebar.caption("지각알리미 · 시제품")
