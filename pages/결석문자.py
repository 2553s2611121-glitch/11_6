import time
import pandas as pd
import streamlit as st

# ==========================================
# 1. 페이지 기본 설정 및 디자인 CSS
# ==========================================
st.set_page_config(
    page_title="미통보 결석 학생·학부모 사유 확인 시스템",
    page_icon="🏫",
    layout="wide",
)

# Custom CSS 스타일
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .student-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .badge-gray { background-color: #F1F5F9; color: #475569; padding: 4px 8px; border-radius: 6px; font-weight: 600; }
    .badge-blue { background-color: #DBEAFE; color: #1E40AF; padding: 4px 8px; border-radius: 6px; font-weight: 600; }
    .badge-green { background-color: #DCFCE7; color: #166534; padding: 4px 8px; border-radius: 6px; font-weight: 600; }
    .badge-red { background-color: #FEE2E2; color: #991B1B; padding: 4px 8px; border-radius: 6px; font-weight: 600; }
    </style>
""",
    unsafe_allow_style_gradient=True,
    unsafe_allow_html=True,
)

# ==========================================
# 2. 세션 상태 초기화 및 무단결석 판정 로직
# ==========================================
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


# 자동 상태 업데이트 (최초 발송 후 20분(1200초) 초과 시 미응답이면 무단결과 처리)
def update_statuses():
    current_time = time.time()
    for student in st.session_state.students:
        if student["status"] == "문자발송 완료":
            # 최초로 문자를 발송한 시각 기준
            times = [
                t
                for t in [
                    student["student_sent_time"],
                    student["parent_sent_time"],
                ]
                if t is not None
            ]
            if times:
                earliest_sent = min(times)
                elapsed = current_time - earliest_sent
                if elapsed >= 1200:  # 20분 초과 시 무단결과(무단결석)
                    student["status"] = "무단결과"


update_statuses()

# ==========================================
# 3. 헤더 및 사이드바
# ==========================================
st.markdown(
    '<div class="main-header">🏫 미통보 결석 학생·학부모 사유 확인 시스템</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-header">학생 발송 후에도 학부모에게 추가 발송할 수 있으며, <b>20분 이내 무응답 시 자동으로 무단결과 처리</b>됩니다.</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("➕ 신규 결석 학생 등록")
    with st.form("add_student_form", clear_on_submit=True):
        input_id = st.text_input("학번", placeholder="예: 10103")
        input_name = st.text_input("학생 이름", placeholder="예: 박민수")
        input_phone = st.text_input("학생 연락처", placeholder="010-0000-0000")
        input_parent_phone = st.text_input("학부모 연락처", placeholder="010-0000-0000")
        submit_add = st.form_submit_button("신규 등록", use_container_width=True)

        if submit_add:
            if input_id and input_name and (input_phone or input_parent_phone):
                st.session_state.students.append(
                    {
                        "id": input_id,
                        "name": input_name,
                        "phone": input_phone,
                        "parent_phone": input_parent_phone,
                        "status": "미응답",
                        "student_sent_time": None,
                        "parent_sent_time": None,
                        "reason": "",
                        "submitted_by": "",
                    }
                )
                st.success(f"{input_name} 학생이 목록에 등록되었습니다.")
                st.rerun()
            else:
                st.error("학번, 이름 및 최소 하나 이상의 연락처를 입력해주세요.")

    st.markdown("---")
    st.header("⚙️ 화면 설정")
    auto_
