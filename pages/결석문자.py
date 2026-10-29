import time
import pandas as pd
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_config_title="학생 결석 사유 관리 시스템",
    page_title="학생 결석 사유 관리 시스템",
    page_icon="🏫",
    layout="wide",
)

# 세션 상태 초기화 (앱 리로드 시 데이터 유지)
if "students" not in st.session_state:
    st.session_state.students = [
        {
            "id": "10101",
            "name": "김철수",
            "phone": "010-1234-5678",
            "status": "미응답",
            "sent_time": None,
            "reason": "",
        },
        {
            "id": "10102",
            "name": "이영희",
            "phone": "010-8765-4321",
            "status": "미응답",
            "sent_time": None,
            "reason": "",
        },
        {
            "id": "10103",
            "name": "박민수",
            "phone": "010-5555-7777",
            "status": "미응답",
            "sent_time": None,
            "reason": "",
        },
    ]


# 자동 상태 업데이트 함수 (20분 = 1200초 경과 시 무단결과 처리)
def update_statuses():
    current_time = time.time()
    for student in st.session_state.students:
        if student["status"] == "문자발송 완료" and student["sent_time"]:
            elapsed = current_time - student["sent_time"]
            if elapsed >= 1200:  # 20분(1200초) 초과 시
                student["status"] = "무단결과"


# 매 실행마다 시간 체크
update_statuses()

# --- 화면 헤더 ---
st.title("🏫 미통보 결석 학생 사유 확인 시스템")
st.caption(
    "결석 문자 발송 후 **20분 이내**에 사유를 제출하지 않으면 자동으로 **무단결과** 처리됩니다."
)
st.markdown("---")

# --- 사이드바: 신규 결석 학생 등록 ---
with st.sidebar:
    st.header("➕ 결석 학생 등록")
    with st.form("add_student_form", clear_on_submit=True):
        student_id = st.text_input("학번", placeholder="예: 10104")
        student_name = st.text_input("이름", placeholder="예: 홍길동")
        student_phone = st.text_input("연락처", placeholder="010-0000-0000")
        submit_btn = st.form_submit_button("학생 추가", use_container_width=True)

        if submit_btn:
            if student_id and student_name and student_phone:
                st.session_state.students.append(
                    {
                        "id": student_id,
                        "name": student_name,
                        "phone": student_phone,
                        "status": "미응답",
                        "sent_time": None,
                        "reason": "",
                    }
                )
                st.success(f"{student_name} 학생이 등록되었습니다.")
                st.rerun()
            else:
                st.error("모든 항목을 입력해 주세요.")

    st.markdown("---")
    st.caption("💡 Tip: 테스트용으로 타이머를 빠르게 확인하고 싶다면 아래 새로고침 버튼을 누르세요.")
    if st.button("
