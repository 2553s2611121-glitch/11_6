import streamlit as st
import pandas as pd

# 페이지 기본 설정
st.set_page_config(
    page_title="등교 알림이",
    page_icon="🔔",
    layout="wide"
)

# 세션 상태 초기화 (초기 학생 데이터 및 사유 관리)
if "students" not in st.session_state:
    st.session_state.students = [
        {"학번": "10101", "이름": "강민준", "상태": "출석", "사유": "", "결석교시": "전체"},
        {"학번": "10102", "이름": "김서연", "상태": "출석", "사유": "", "결석교시": "전체"},
        {"학번": "10103", "이름": "박도윤", "상태": "출석", "사유": "", "결석교시": "전체"},
        {"학번": "10104", "이름": "이지우", "상태": "출석", "사유": "", "결석교시": "전체"},
        {"학번": "10105", "이름": "최현우", "상태": "출석", "사유": "", "결석교시": "전체"},
    ]

if "schedule" not in st.session_state:
    st.session_state.schedule = {
        "1교시": "국어",
        "2교시": "수학",
        "3교시": "영어",
        "4교시": "과학",
        "5교시": "사회",
        "6교시": "체육",
        "7교시": "자율"
    }

st.title("🔔 등교 알림이")
st.caption("학생 직접 결석 처리 및 현황 조회 시스템")

# 상단 대시보드 (전체 인원 및 결석 인원 현황)
total_students = len(st.session_state.students)
absent_count = sum(1 for s in st.session_state.students if s["상태"] == "결석")
present_count = total_students - absent_count

col1, col2, col3 = st.columns(3)
col1.metric("총 학생 수", f"{total_students}명")
col2.metric("현재 출석 인원", f"{present_count}명")
col3.metric("결석 인원", f"{absent_count}명", delta=f"-{absent_count}" if absent_count > 0 else "0", delta_color="inverse")

st.divider()

# 탭 구성
tab1, tab2, tab3 = st.tabs(["📌 출결 등록 (학생용)", "🚨 결석자 현황 (교사용)", "📅 학교 시간표"])

# Tab 1: 학생 출결 등록
with tab1:
    st.subheader("학생 출결 체크")
    search_term = st.text_input("🔍 학번 또는 이름을 검색하세요", placeholder="예: 10101 또는 강민준")
    
    filtered_students = st.session_state.students
    if search_term:
        filtered_students = [
            s for s in st.session_state.students 
            if search_term in s["학번"] or search_term in s["이름"]
        ]
    
    if not filtered_students:
        st.warning("검색 결과가 없습니다.")
    else:
        for student in filtered_students:
            with st.expander(f"[{student['학번']}] {student['이름']} (현재 상태: {student['상태']})", expanded=True):
                with st.form(key=f"form_{student['학번']}"):
                    status = st.radio("출결 상태 선택", ["출석", "결석"], index=0 if student["상태"] == "출석" else 1, horizontal=True)
                    reason = st.text_input("결석 사유 (결석 선택 시 필수 입력)", value=student["사유"], placeholder="예: 감기 몸살, 병원 진료 등")
                    absent_period = st.selectbox(
                        "결석/조퇴 해당 교시", 
                        ["전체 (하루 종일)", "1~2교시", "3~4교시", "5~7교시", "기타"],
                        index=0
                    )
                    
                    submitted = st.form_submit_dict = st.form_submit_button("상태 저장하기")
                    if submitted:
                        if status == "결석" and not reason.strip():
                            st.error("결석 선택 시 사유를 반드시 입력해야 합니다.")
                        else:
                            student["상태"] = status
                            student["사유"] = reason if status == "결석" else ""
                            student["결석교시"] = absent_period if status == "결석" else "전체"
                            st.success(f"{student['이름']} 학생의 출결 정보가 저장되었습니다.")
                            st.rerun()

# Tab 2: 결석자 목록 확인
with tab2:
    st.subheader("결석 학생 명단")
    absent_list = [s for s in st.session_state.students if s["상태"] == "결석"]
    
    if absent_list:
        df_absent = pd.DataFrame(absent_list)[["학번", "이름", "상태", "사유", "결석교시"]]
        st.dataframe(df_absent, use_container_width=True)
    else:
        st.info("현재 결석으로 등록된 학생이 없습니다.")

# Tab 3: 학교 시간표
with tab3:
    st.subheader("오늘의 학교 시간표")
    df_schedule = pd.DataFrame(list(st.session_state.schedule.items()), columns=["교시", "과목"])
    st.table(df_schedule)
