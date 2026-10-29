import time
import pandas as pd
import streamlit as st

# ==========================================
# 1. 페이지 기본 설정 및 세션 초기화
# ==========================================
st.set_page_config(
    page_title="단계별 결석 사유 관리 System",
    page_icon="🏫",
    layout="wide",
)

# 기본 학생 데이터 구조
if "students" not in st.session_state:
    st.session_state.students = [
        {
            "id": "10101",
            "name": "김철수",
            "phone": "010-1234-5678",
            "parent_phone": "010-1111-2222",
            "status": "미응답",  # 미응답, 학생대기중, 학부모대기중, 사유제출 완료, 무단결과
            "stu_sent_time": None,
            "par_sent_time": None,
            "reason": "",
            "submitted_by": "",
        },
        {
            "id": "10102",
            "name": "이영희",
            "phone": "010-8765-4321",
            "parent_phone": "010-3333-4444",
            "status": "미응답",
            "stu_sent_time": None,
            "par_sent_time": None,
            "reason": "",
            "submitted_by": "",
        },
    ]


# 자동 상태 업데이트 함수 (20분 타이머 체크)
def update_statuses():
    current_time = time.time()
    for student in st.session_state.students:
        # 학부모에게 문자를 보낸 상태에서 20분이 지난 경우 -> 무단결과
        if student["status"] == "학부모대기중" and student["par_sent_time"] is not None:
            if current_time - student["par_sent_time"] >= 1200:  # 20분
                student["status"] = "무단결과"


update_statuses()

# ==========================================
# 2. 메인 화면 타이틀 및 사이드바
# ==========================================
st.title("🏫 단계별 학생/학부모 결석 사유 확인 시스템")
st.caption(
    "1차로 학생에게 문자를 발송하고, 무응답 시 2차로 학부모에게 문자를 발송합니다. **학부모 문자 발송 후 20분 내 미응답 시 무단결과** 처리됩니다."
)
st.markdown("---")

# 사이드바: 신규 학생 등록 및 타이머 설정
with st.sidebar:
    st.header("➕ 결석 학생/학부모 등록")
    with st.form("add_student_form", clear_on_submit=True):
        input_id = st.text_input("학번", placeholder="예: 10103")
        input_name = st.text_input("학생 이름", placeholder="예: 박민수")
        input_phone = st.text_input("학생 연락처", placeholder="010-0000-0000")
        input_parent_phone = st.text_input("학부모 연락처", placeholder="010-0000-0000")
        submit_add = st.form_submit_button("등록하기", use_container_width=True)

        if submit_add:
            if input_id and input_name and input_phone and input_parent_phone:
                st.session_state.students.append(
                    {
                        "id": input_id,
                        "name": input_name,
                        "phone": input_phone,
                        "parent_phone": input_parent_phone,
                        "status": "미응답",
                        "stu_sent_time": None,
                        "par_sent_time": None,
                        "reason": "",
                        "submitted_by": "",
                    }
                )
                st.success(f"{input_name} 학생 정보가 추가되었습니다.")
                st.rerun()
            else:
                st.error("학번, 이름, 학생/학부모 연락처를 모두 입력해 주세요.")

    st.markdown("---")
    st.header("⏱️ 타이머 설정")
    auto_refresh = st.checkbox("1초 자동 화면 갱신", value=True)
    if st.button("🔄 수동 새로고침", use_container_width=True):
        st.rerun()

# ==========================================
# 3. 메인 탭 구성
# ==========================================
tab_teacher, tab_submit = st.tabs(["📱 교사용 - 단계별 발송 관리", "📩 학생·학부모용 - 사유 제출"])

# ------------------------------------------
# TAB 1: 교사용 화면
# ------------------------------------------
with tab_teacher:
    st.subheader("📋 학생 1차 & 학부모 2차 발송 및 타이머")

    if not st.session_state.students:
        st.info("현재 등록된 결석 학생이 없습니다.")
    else:
        # 요약 지표
        total_cnt = len(st.session_state.students)
        stu_wait_cnt = sum(1 for s in st.session_state.students if s["status"] == "학생대기중")
        par_wait_cnt = sum(1 for s in st.session_state.students if s["status"] == "학부모대기중")
        done_cnt = sum(1 for s in st.session_state.students if s["status"] == "사유제출 완료")
        absent_cnt = sum(1 for s in st.session_state.students if s["status"] == "무단결과")

        m1, m
