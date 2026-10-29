import time
import pandas as pd
import streamlit as st

# ==========================================
# 1. 페이지 기본 설정 및 디자인
# ==========================================
st.set_page_config(
    page_title="스마트 결석 사유 확인 & 무단결석 관리 시스템",
    page_icon="🏫",
    layout="wide",
)

# Custom CSS 커스텀 스타일 적용 (에러 안전 방식)
st.markdown(
    """
    <style>
    .student-card {
        background-color: #1e222d;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #2e3545;
        margin-bottom: 15px;
    }
    .timer-badge {
        background-color: #2b1f0d;
        color: #ffaa00;
        padding: 8px 12px;
        border-radius: 8px;
        border: 1px solid #664400;
        font-weight: bold;
        font-size: 1.1rem;
    }
    .absent-badge {
        background-color: #3d1418;
        color: #ff4d4d;
        padding: 8px 12px;
        border-radius: 8px;
        border: 1px solid #801a24;
        font-weight: bold;
    }
    .success-badge {
        background-color: #0d331e;
        color: #00e676;
        padding: 8px 12px;
        border-radius: 8px;
        border: 1px solid #006633;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 세션 데이터 초기화
if "students" not in st.session_state:
    st.session_state.students = [
        {
            "id": "10101",
            "name": "김철수",
            "phone": "010-1234-5678",
            "parent_phone": "010-1111-2222",
            "status": "미응답",
            "student_sent_time": None,
            "parent_sent_time": None,
            "reason": "",
            "submitted_by": "",
        },
        {
            "id": "10102",
            "name": "이영희",
            "phone": "010-8765-4321",
            "parent_phone": "010-3333-4444",
            "status": "미응답",
            "student_sent_time": None,
            "parent_sent_time": None,
            "reason": "",
            "submitted_by": "",
        },
    ]


# 20분(1200초) 카운트다운 및 자동 무단결석 처리
def update_statuses():
    current_time = time.time()
    for student in st.session_state.students:
        if student["status"] in ["문자발송 완료", "학생발송 완료", "학부모발송 완료"]:
            times = [t for t in [student["student_sent_time"], student["parent_sent_time"]] if t is not None]
            if times:
                first_sent_time = min(times)
                if current_time - first_sent_time >= 1200:  # 20분 초과
                    student["status"] = "무단결석"


# 자동 업데이트
update_statuses()

# ==========================================
# 2. 대시보드 헤더 & 사이드바
# ==========================================
st.title("🏫 스마트 결석 사유 확인 & 무단결석 처리 시스템")
st.caption("학생/학부모 개별 문자 발송 | **20분 미응답 시 자동 무단결석 처리** | 스마트 실시간 모니터링")
st.markdown("---")

# 사이드바
with st.sidebar:
    st.header("➕ 신규 결석 학생 추가")
    with st.form("add_student_form", clear_on_submit=True):
        input_id = st.text_input("학번", placeholder="예: 10103")
        input_name = st.text_input("학생 이름", placeholder="예: 박민수")
        input_phone = st.text_input("학생 연락처", placeholder="010-0000-0000")
        input_parent_phone = st.text_input("학부모 연락처", placeholder="010-0000-0000")
        submit_add = st.form_submit_button("학생 추가하기", use_container_width=True)

        if submit_add:
            if input_id and input_name and (input_phone or input_parent_phone):
                st.session_state.students.append(
