
import time
from datetime import datetime

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh


# -------------------------------
# 1. 기본 설정
# -------------------------------
st.set_page_config(
    page_title="출결 관리 시스템",
    page_icon="📋",
    layout="wide",
)

# 1초마다 화면을 갱신해 타이머를 표시
st_autorefresh(interval=1000, key="page_refresh")


# -------------------------------
# 2. 디자인
# -------------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #F5F7FB;
    }
    [data-testid="stSidebar"] {
        background-color: #172F50;
    }
    [data-testid="stSidebar"] * {
        color: white;
    }
    .main-title {
        color: #17365D;
        font-size: 32px;
        font-weight: 800;
        margin-bottom: 3px;
    }
    .sub-title {
        color: #738198;
        font-size: 14px;
        margin-bottom: 22px;
    }
    .info-card {
        background: white;
        padding: 20px;
        border: 1px solid #E5EAF2;
        border-radius: 14px;
        margin-bottom: 12px;
    }
    .small-label {
        color: #718096;
        font-size: 14px;
    }
    .big-number {
        color: #17365D;
        font-size: 30px;
        font-weight: 800;
    }
    .timer {
        color: #DC4545;
        font-size: 27px;
        font-weight: 800;
    }
    div.stButton > button {
        border-radius: 9px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# -------------------------------
# 3. 예시 학생 데이터
# -------------------------------
if "students" not in st.session_state:
    now = time.time()

    st.session_state.students = [
        {"name": "김도현", "status": "출석",
         "reason": "-", "started": None},
        {"name": "이서연", "status": "출석",
         "reason": "-", "started": None},
        {"name": "박지민", "status": "출석",
         "reason": "-", "started": None},
        {"name": "최예은", "status": "지각",
         "reason": "-", "started": None},
        {"name": "정민준", "status": "출석",
         "reason": "-", "started": None},
        {"name": "한지민", "status": "결석",
         "reason": "미확인", "started": now},
        {"name": "강민서", "status": "출석",
         "reason": "-", "started": None},
        {"name": "이준호", "status": "출석",
         "reason": "-", "started": None},
        {"name": "유나영", "status": "결석",
         "reason": "질병(감기)", "started": None},
        {"name": "신동우", "status": "출석",
         "reason": "-", "started": None},
        {"name": "조하은", "status": "출석",
         "reason": "-", "started": None},
        {"name": "성지윤", "status": "출석",
         "reason": "-", "started": None},
        {"name": "윤서준", "status": "무단 결과",
         "reason": "미제출", "started": now - 1900},
        {"name": "이다은", "status": "출석",
         "reason": "-", "started": None},
    ]


students = st.session_state.students


# -------------------------------
# 4. 타이머 및 자동 처리
# -------------------------------
now = time.time()

for student in students:
    if (
        student["status"] == "결석"
        and student["reason"] == "미확인"
        and student["started"] is not None
    ):
        elapsed = now - student["started"]

        if elapsed >= 1800:
            student["status"] = "무단 결과"
            student["reason"] = "미제출"


# -------------------------------
# 5. 왼쪽 메뉴
# -------------------------------
with st.sidebar:
    st.markdown("## 📋 출결 관리")
    st.caption("SCHOOL ATTENDANCE")
    st.divider()

    page = st.radio(
        "메뉴",
        ["출석 현황", "출결 기록", "학생 관리"],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption("시제품 · 가상 학생 데이터")


# -------------------------------
# 6. 출석 현황 페이지
# -------------------------------
if page == "출석 현황":

    st.markdown(
        '<div class="main-title">출석 현황</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sub-title">'
        '학생들의 출석 상태와 미확인 결석을 관리합니다.'
        '</div>',
        unsafe_allow_html=True,
    )

    top1, top2 = st.columns([1, 1])

    with top1:
        selected_date = st.date_input(
            "조회 날짜",
            value=datetime.now().date(),
        )

    with top2:
        selected_class = st.selectbox(
            "학급",
            ["2학년 3반"],
        )

    # 요약 통계
    count_present = sum(
        s["status"] == "출석" for s in students
    )
    count_late = sum(
        s["status"] == "지각" for s in students
    )
    count_absent = sum(
        s["status"] == "결석" for s in students
    )
    count_unexcused = sum(
        s["status"] == "무단 결과" for s in students
    )

    metrics = st.columns(4)

    metric_data = [
        ("출석", count_present, "🟢"),
        ("지각", count_late, "🟠"),
        ("결석", count_absent, "🔴"),
        ("무단 결과", count_unexcused, "⚠️"),
    ]

    for col, (label, value, emoji) in zip(
        metrics, metric_data
    ):
        with col:
            st.markdown(
                f"""
                <div class="info-card">
                    <div class="small-label">
                        {emoji} {label}
                    </div>
                    <div class="big-number">{value}명</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()

    # 검색 및 필터
    st.subheader("학생 출결 목록")

    search_col, filter_col = st.columns([2, 1])

    with search_col:
        search_name = st.text_input(
            "🔎 학생 검색",
            placeholder="학생 이름을 입력하세요",
        )

    with filter_col:
        status_filter = st.selectbox(
            "출결 상태 필터",
            ["전체", "출석", "지각", "결석", "무단 결과"],
        )

    # 표 데이터 만들기
    rows = []

    for student in students:
        if (
            search_name
            and search_name not in student["name"]
        ):
            continue

        if (
            status_filter != "전체"
            and status_filter != student["status"]
        ):
            continue

        timer_text = "-"

        if (
            student["status"] == "결석"
            and student["reason"] == "미확인"
            and student["started"] is not None
        ):
            remaining = max(
                0,
                1800 - int(time.time() - student["started"]),
            )
            timer_text = (
                f"{remaining // 60:02d}:"
                f"{remaining % 60:02d}"
            )

        rows.append({
            "학생 이름": student["name"],
            "출석 상태": student["status"],
            "결석 사유": student["reason"],
            "남은 시간": timer_text,
        })

    if rows:
        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("검색 결과가 없습니다.")

    st.caption(
        f"{selected_date.strftime('%Y-%m-%d')} · "
        f"{selected_class} · 총 {len(rows)}명 표시"
    )

    st.divider()

    # 결석 사유 확인
    st.subheader("⏱️ 결석 사유 확인")

    unresolved = [
        s for s in students
        if (
            s["status"] == "결석"
            and s["reason"] == "미확인"
        )
    ]

    if unresolved:
        selected_name = st.selectbox(
            "사유를 확인할 학생",
            [s["name"] for s in unresolved],
        )

        selected_student = next(
            s for s in unresolved
            if s["name"] == selected_name
        )

        remaining = max(
            0,
            1800 - int(
                time.time() - selected_student["started"]
            ),
        )

        st.markdown(
            f"""
            <div class="info-card">
                <div class="small-label">
                    {selected_student['name']} ·
                    결석 사유 미확인
                </div>
                <div class="timer">
                    ⏱️ {remaining // 60:02d}:
                    {remaining % 60:02d}
                </div>
                <div class="small-label">
                    사유가 30분 이내에 확인되지 않으면
                    무단 결과로 처리됩니다.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("reason_form"):
            reason = st.text_input(
                "확인된 결석 사유",
                placeholder="예: 병원 진료, 질병",
            )

            submitted = st.form_submit_button(
                "사유 확인 완료",
                type="primary",
                use_container_width=True,
            )

            if submitted:
                if reason.strip():
                    selected_student["reason"] = reason.strip()
                    selected_student["started"] = None
                    st.success(
                        f"{selected_name} 학생의 사유가 기록되었습니다."
                    )
                    st.rerun()
                else:
                    st.error("결석 사유를 입력해 주세요.")

    else:
        st.success("현재 확인 대기 중인 결석이 없습니다.")

    st.divider()

    # 테스트용 결석 등록
    with st.expander("🧪 시제품 테스트: 결석 등록"):
        st.caption(
            "실제 출결 앱 연결 전, 타이머 기능을 시험하기 위한 메뉴입니다."
        )

        eligible = [
            s["name"] for s in students
            if s["status"] in ["출석", "지각"]
        ]

        if eligible:
            absent_name = st.selectbox(
                "결석으로 변경할 학생",
                eligible,
                key="test_absent_name",
            )

            if st.button("미확인 결석 등록"):
                target = next(
                    s for s in students
                    if s["name"] == absent_name
                )
                target["status"] = "결석"
                target["reason"] = "미확인"
                target["started"] = time.time()
                st.rerun()


# -------------------------------
# 7. 출결 기록 페이지
# -------------------------------
elif page == "출결 기록":
    st.title("🗂️ 출결 기록")
    st.caption("현재 시제품에 기록된 출결 상태")

    history_rows = [
        {
            "학생 이름": s["name"],
            "출석 상태": s["status"],
            "결석 사유": s["reason"],
        }
        for s in students
        if s["status"] != "출석"
    ]

    if history_rows:
        st.dataframe(
            pd.DataFrame(history_rows),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("표시할 출결 기록이 없습니다.")


# -------------------------------
# 8. 학생 관리 페이지
# -------------------------------
elif page == "학생 관리":
    st.title("👥 학생 관리")
    st.caption("현재 시제품에 등록된 학생 목록")

    st.dataframe(
        pd.DataFrame([
            {"번호": i + 1, "학생 이름": s["name"]}
            for i, s in enumerate(students)
        ]),
        use_container_width=True,
        hide_index=True,
    )

    st.info(
        "이 버전은 예시 학생 목록을 사용합니다. "
        "실제 학생 등록 및 저장 기능은 추후 추가할 수 있습니다."
    )

st.caption(
    "출결 관리 시제품 · 예시 데이터 전용 · "
    "실제 출결 시스템과 연결되지 않음"
)

