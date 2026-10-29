import time
import pandas as pd
import streamlit as st

# ==========================================
# 1. 페이지 기본 설정 및 세션 초기화
# ==========================================
st.set_page_config(
    page_title="학생/학부모 결석 사유 관리 System",
    page_icon="🏫",
    layout="wide",
)

# 기본 데이터 구조
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
            "sent_time": None,  # 최초 발송 시간 (20분 타이머 기준)
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
        # 문자가 1회 이상 발송되었고 답변 대기 상태인 경우
        if student["status"] in ["학생 발송 완료", "학부모 발송 완료", "학생+학부모 발송 완료"] and student["sent_time"] is not None:
            elapsed = current_time - student["sent_time"]
            if elapsed >= 1200:  # 20분 초과
                student["status"] = "무단결과"


# 상태 업데이트 체크
update_statuses()

# ==========================================
# 2. 메인 화면 타이틀 및 사이드바
# ==========================================
st.title("🏫 학생 & 학부모 결석 사유 확인 시스템")
st.caption(
    "학생/학부모 중 누군가에게 문자를 보낸 시점부터 **20분 타이머**가 작동하며, 시간 내 사유를 제출하지 않으면 **무단결과** 처리됩니다."
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
                st.error("학번, 이름, 그리고 최소 하나의 연락처를 입력하세요.")

    st.markdown("---")
    st.header("⏱️ 타이머 설정")
    auto_refresh = st.checkbox("1초 자동 화면 갱신", value=True)
    if st.button("🔄 수동 새로고침", use_container_width=True):
        st.rerun()

# ==========================================
# 3. 메인 탭 구성
# ==========================================
tab_teacher, tab_submit = st.tabs(["📱 교사용 - 결석/발송 관리", "📩 학생·학부모용 - 사유 제출"])

# ------------------------------------------
# TAB 1: 교사용 관리 화면
# ------------------------------------------
with tab_teacher:
    st.subheader("📋 개별 발송 현황 및 20분 타이머")

    if not st.session_state.students:
        st.info("현재 등록된 결석 학생이 없습니다.")
    else:
        # 요약 메트릭
        total_cnt = len(st.session_state.students)
        pending_cnt = sum(
            1 for s in st.session_state.students 
            if s["status"] in ["학생 발송 완료", "학부모 발송 완료", "학생+학부모 발송 완료"]
        )
        done_cnt = sum(1 for s in st.session_state.students if s["status"] == "사유제출 완료")
        absent_cnt = sum(1 for s in st.session_state.students if s["status"] == "무단결과")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("총 대상 인원", f"{total_cnt}명")
        m2.metric("답변 대기 (20분)", f"{pending_cnt}명")
        m3.metric("사유 제출 완료", f"{done_cnt}명")
        m4.metric("🚨 무단결과 처리", f"{absent_cnt}명")

        st.markdown("---")

        # 학생별 카드리스트
        for idx, student in enumerate(st.session_state.students):
            col_info, col_timer, col_action, col_delete = st.columns([2.5, 3.5, 3, 0.8])

            # 1. 정보 표시
            col_info.markdown(
                f"### {student['name']} (`{student['id']}`)\n"
                f"📱 **학생:** `{student['phone'] or '없음'}`\n\n"
                f"👨‍👩‍👧 **학부모:** `{student['parent_phone'] or '없음'}`"
            )

            # 2. 개별 타이머 및 진행 상태
            if student["status"] == "미응답":
                col_timer.info("⚪ **문자 미발송**\n\n학생 또는 학부모에게 문자를 발송해
