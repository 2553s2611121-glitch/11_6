import time
import pandas as pd
import streamlit as st

# ==========================================
# 1. 페이지 기본 설정 및 스타일링
# ==========================================
st.set_page_config(
    page_title="학생 & 학부모 결석 사유 확인 시스템",
    page_icon="🏫",
    layout="wide",
)

# 커스텀 CSS 적용 (사이트 꾸미기)
st.markdown(
    """
    <style>
    /* 전체 배경 스타일 */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* 대시보드 메트릭 카드리뷰 */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0px 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    /* 학생 카드 스타일 */
    .student-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.03);
        margin-bottom: 10px;
    }

    /* 뱃지 스타일 */
    .badge-pending {
        background-color: #FEF3C7;
        color: #D97706;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .badge-success {
        background-color: #D1FAE5;
        color: #059669;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .badge-danger {
        background-color: #FEE2E2;
        color: #DC2626;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 2. 세션 상태 및 타이머 함수
# ==========================================
if "students" not in st.session_state:
    st.session_state.students = [
        {
            "id": "10101",
            "name": "김철수",
            "phone": "010-1234-5678",
            "parent_phone": "010-1111-2222",
            "student_sent": False,
            "parent_sent": False,
            "status": "미응답",
            "sent_time": None,
            "reason": "",
            "submitted_by": "",
        },
        {
            "id": "10102",
            "name": "이영희",
            "phone": "010-8765-4321",
            "parent_phone": "010-3333-4444",
            "student_sent": False,
            "parent_sent": False,
            "status": "미응답",
            "sent_time": None,
            "reason": "",
            "submitted_by": "",
        },
    ]


# 20분(1200초) 초과 시 무단결과 처리 함수
def update_statuses():
    current_time = time.time()
    for student in st.session_state.students:
        if student["status"] == "문자발송 완료" and student["sent_time"] is not None:
            elapsed = current_time - student["sent_time"]
            if elapsed >= 1200:  # 20분 초과
                student["status"] = "무단결과"


update_statuses()

# ==========================================
# 3. 사이드바 및 헤더
# ==========================================
st.title("🏫 미통보 결석 학생 사유 확인 시스템")
st.caption(
    "문자 발송 후 **20분 이내**에 학생 또는 학부모가 사유를 제출하지 않으면 **무단결과** 처리됩니다."
)
st.markdown("---")

with st.sidebar:
    st.header("➕ 결석 학생 신규 등록")
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
                        "student_sent": False,
                        "parent_sent": False,
                        "status": "미응답",
                        "sent_time": None,
                        "reason": "",
                        "submitted_by": "",
                    }
                )
                st.success(f"{input_name} 학생 정보가 등록되었습니다.")
                st.rerun()
            else:
                st.error("학번, 이름, 최소 한 개 이상의 연락처를 입력하세요.")

    st.markdown("---")
    st.header("⏱️ 화면 및 타이머 제어")
    auto_refresh = st.checkbox("1초 실시간 타이머 갱신", value=True)
    if st.button("🔄 화면 새로고침", use_container_width=True):
        st.rerun()

# ==========================================
# 4. 메인 탭 구성
# ==========================================
tab_teacher, tab_submit = st.tabs(["📱 교사용 - 학생/학부모 개별 관리", "📩 수신용 - 사유 제출 화면"])

# ------------------------------------------
# TAB 1: 교사용 화면
# ------------------------------------------
with tab_teacher:
    if not st.session_state.students:
        st.info("등록된 결석 학생이 없습니다.")
    else:
        # 요약 메트릭
        total_cnt = len(st.session_state.students)
        pending_cnt = sum(1 for s in st.session_state.students if s["status"] == "문자발송 완료")
        done_cnt = sum(1 for s in st.session_state.students if s["status"] == "사유제출 완료")
        absent_cnt = sum(1 for s in st.session_state.students if s["status"] == "무단결과")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("총 결석 인원", f"{total_cnt}명")
        m2.metric("답변 대기중", f"{pending_cnt}명")
        m3.metric("사유 제출 완료", f"{done_cnt}명")
        m4.metric("🚨 무단결과 처리", f"{absent_cnt}명")

        st.markdown("<br>", unsafe_allow_html=True)

        # 학생 카드리스트
        for idx, student in enumerate(st.session_state.students):
            with st.container():
                col_info, col_timer, col_action, col_del = st.columns([2.8, 3.2, 3, 0.8])

                # 1. 인적사항 및 연락처 발송 상태
                s_sent_badge = "✅ 발송됨" if student["student_sent"] else "⚪ 미발송"
                p_sent_badge = "✅ 발송됨" if student["parent_sent"] else "⚪ 미발송"

                col_info.markdown(
                    f"### {student['name']} (`{student['id']}`)\n"
                    f
