import streamlit as st 
import pandas as pd
from datetime import datetime
st.set_page_config(
page_title="등교 알림이",
page_icon="🔔",
layout="wide",
initial_sidebar_state="expanded"
)
if "students_data" not in st.session_state:
st.session_state.students_data = [
{"학번": "20101", "이름": "강민준", "상태": "출석", "결석사유": "-", "빠지는교시": "-"},
{"학번": "20102", "이름": "김서연", "상태": "결석", "결석사유": "감기몸살 (병원 방문)", "빠지는교시": "전일 결석"},
{"학번": "20103", "이름": "박지후", "상태": "출석", "결석사유": "-", "빠지는교시": "-"},
{"학번": "20104", "이름": "이하은", "상태": "출석", "결석사유": "-", "빠지는교시": "-"},
{"학번": "20105", "이름": "정우진", "상태": "결석", "결석사유": "조퇴 (치과 진료)", "빠지는교시": "5~7교시"},
{"학번": "20106", "이름": "최윤아", "상태": "출석", "결석사유": "-", "빠지는교시": "-"},
{"학번": "20107", "이름": "한도현", "상태": "출석", "결석사유": "-", "빠지는교시": "-"},
{"학번": "20108", "이름": "수지", "상태": "출석", "결석사유": "-", "빠지는교시": "-"},
]
timetable_data = {
"교시": ["1교시", "2교시", "3교시", "4교시", "5교시", "6교시", "7교시"],
"시간": ["09:00 - 09:50", "10:00 - 10:50", "11:00 - 11:50", "12:00 - 12:50", "14:00 - 14:50", "15:00 - 15:50", "16:00 - 16:50"],
"과목": ["국어", "수학", "영어", "사회", "과학", "체육", "자율/동아리"],
"담당 교사": ["김선생", "이선생", "박선생", "최선생", "정선생", "강선생", "담임교사"]
}
timetable_data = {
"교시": ["1교시", "2교시", "3교시", "4교시", "5교시", "6교시", "7교시"],
"시간": ["09:00 - 09:50", "10:00 - 10:50", "11:00 - 11:50", "12:00 - 12:50", "14:00 - 14:50", "15:00 - 15:50", "16:00 - 16:50"],
"과목": ["국어", "수학", "영어", "사회", "과학", "체육", "자율/동아리"],
"담당 교사": ["김선생", "이선생", "박선생", "최선생", "정선생", "강선생", "담임교사"]
}
st.sidebar.title("📊 학급 출석 요약")
st.sidebar.caption(f"기준일자: {datetime.now().strftime('%Y-%m-%d')}")

total_students = len(st.session_state.students_data)
absent_students_list = [s for s in st.session_state.students_data if s["상태"] == "결석"]
absent_count = len(absent_students_list)
present_count = total_students - absent_count

st.sidebar.metric(label="👥 재적 인원", value=f"{total_students}명")
st.sidebar.metric(label="✅ 현재 출석 인원 (결석 제외)", value=f"{present_count}명")
st.sidebar.metric(label="🚨 현재 결석 인원", value=f"{absent_count}명", delta=f"-{absent_count}명", delta_color="inverse")

st.sidebar.divider()
st.sidebar.subheader("📌 데이터 관리")
if st.sidebar.button("🔄 출결 상태 전체 출석으로 리셋"):
for s in st.session_state.students_data:
s["상태"] = "출석"
s["결석사유"] = "-"
s["빠지는교시"] = "-"
st.sidebar.success("모든 학생의 출결 상태가 '출석'으로 초기화되었습니다.")
st.rerun()
st.title("🔔 등교 알림이 (학생 출결 체크 시스템)")
st.write("학생들이 직접 등교 전 출결 상태를 등록하고 결석 현황 및 일정을 확인하는 공간입니다.")
with tab1:
st.subheader("🔍 본인 이름 또는 학번으로 검색")
search_term = st.text_input("학번이나 이름을 입력하세요 (예: 강민준 또는 20101):", placeholder="이름/학번 검색...").strip()
with tab1:
st.subheader("🔍 본인 이름 또는 학번으로 검색")
search_term = st.text_input("학번이나 이름을 입력하세요 (예: 강민준 또는 20101):", placeholder="이름/학번 검색...").strip()

# 검색어 필터링
filtered_students = [
    s for s in st.session_state.students_data 
    if search_term in s["학번"] or search_term in s["이름"]
] if search_term else st.session_state.students_data

if not filtered_students:
    st.warning("🔍 검색 결과와 일치하는 학생이 없습니다.")
else:
    st.info("💡 본인의 항목에서 [출석/결석] 상태를 선택 후 저장하세요.")
    
    for idx, student in enumerate(filtered_students):
        with st.expander(f"📌 [{student['학번']}] {student['이름']} — (현재: {student['상태']})", expanded=bool(search_term)):
            with st.form(key=f"student_form_{student['학번']}"):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    new_status = st.radio(
                        "출결 선택",
                        options=["출석", "결석"],
                        index=0 if student["상태"] == "출석" else 1,
                        key=f"status_radio_{student['학번']}"
                    )
                
                with col2:
                    reason = st.text_input(
                        "결석/조퇴 사유 (결석 선택 시 필수 입력)",
                        value="" if student["결석사유"] == "-" else student["결석사유"],
                        placeholder="예: 독감 병결, 5교시 치과 조퇴, 현장체험학습 등",
                        key=f"reason_input_{student['학번']}"
                    )
                    
                    period = st.selectbox(
                        "빠지는 교시 (일부 수업 결석/조퇴 시 선택)",
                        options=["전일 결석", "1~2교시", "3~4교시", "5~7교시", "기타"],
                        index=0 if student["빠지는교시"] == "전일 결석" or student["빠지는교시"] == "-" else 1,
                        key=f"period_select_{student['학번']}"
                    )

                submit_button = st.form_submit_button("💾 출결 상태 저장")
                
                if submit_button:
                    # 예외 처리: 결석 선택 시 사유 입력 확인
                    if new_status == "결석" and not reason.strip():
                        st.error("⚠️ 결석 선택 시 사유를 반드시 적어주세요!")
                    else:
                        # 데이터 업데이트
                        student["상태"] = new_status
                        student["결석사유"] = reason.strip() if new_status == "결석" else "-"
                        student["빠지는교시"] = period if new_status == "결석" else "-"
                        
                        st.success(f"✅ {student['이름']} 학생의 출결이 '{new_status}'(으)로 반영되었습니다.")
                        st.rerun()
with tab2:
st.subheader("🚨 결석/조퇴 등록 학생 명단")
st.caption("결석으로 선택된 학생들만 자동으로 분류되어 표시됩니다.")

if absent_count == 0:
    st.balloons()
    st.success("🎉 오늘 결석/조퇴한 학생이 없습니다! 전원 출석 상태입니다.")
else:
    absent_df = pd.DataFrame(absent_students_list)
    
    # 테이블 컬럼 재정렬
    display_df = absent_df[["학번", "이름", "상태", "결석사유", "빠지는교시"]]
    
    # 가시성 높은 데이터프레임 출력
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    
    # 카드 형태 추가 가독성 제공
    st.write("---")
    st.write("📋 **개별 결석 카드 상세 보기**")
    cols = st.columns(3)
    for i, abs_student in enumerate(absent_students_list):
        with cols[i % 3]:
            st.error(f"**{abs_student['학번']} {abs_student['이름']}**")
            st.write(f"- **구분:** {abs_student['상태']}")
            st.write(f"- **사유:** {abs_student['결석사유']}")
            st.write(f"- **해당 교시:** {abs_student['빠지는교시']}")
          with tab3:
st.subheader("📅 오늘 학급 시간표")
st.caption("결석 및 조퇴 시 어떤 교시 수업에 차질이 생기는지 확인할 수 있습니다.")

df_timetable = pd.DataFrame(timetable_data)
st.table(df_timetable)

st.write("---")
st.subheader("🔔 주요 학사 공지 사항")
st.info("• 이번 주 금요일은 6, 7교시 동아리 활동이 예정되어 있습니다.\n• 감기나 독감 증상이 있는 학생은 병원 진단서 제출 시 병결 처리 가능합니다.")
