import streamlit as st
import pandas as pd
import datetime

# 페이지 레이아웃 설정 (와이드 모드 적용)
st.set_page_config(
    page_title="등교 알림이",
    page_icon="🏫",
    layout="wide"
)

# 사용자 지정 둥근 카드를 위한 CSS 스타일 적용
st.markdown("""
<style>
    .card {
        background-color: #ffffff;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .absent-card {
        background-color: #fff5f5;
        border-left: 5px solid #e53e3e;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
    }
    .schedule-card {
        background-color: #f7fafc;
        border-left: 5px solid #3182ce;
        padding: 10px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# 1. 데이터 세션 상태 초기화
if "students" not in st.session_state:
    st.session_state.students = [
        {"학번": "104", "이름": "최하은", "상태": "결석", "메모": "감기 몸살", "전화번호": "010-1234-5678"},
        {"학번": "106", "이름": "강수아", "상태": "결석", "메모": "병원 진료 예정", "전화번호": "010-2345-6789"},
        {"학번": "107", "이름": "윤호진", "상태": "결석", "메모": "체험학습 제출", "전화번호": "010-3456-7890"},
        {"학번": "101", "이름": "김민준", "상태": "출석", "메모": "", "전화번호": "010-4567-8901"},
        {"학번": "102", "이름": "이서연", "상태": "출석", "메모": "", "전화번호": "010-5678-9012"},
        {"학번": "103", "이름": "박도윤", "상태": "출석", "메모": "", "전화번호": "010-6789-0123"},
    ]

# 2. 메인 헤더
st.title("🏫 등교 알림이")

# 3. 이미지 레이아웃 복사 (3컬럼 구조 생성)
left_col, center_col, right_col = st.columns([1, 1.2, 1])

# ==========================================
# [좌측 컬럼] 검색 및 실시간 미등교 학생 관리
# ==========================================
with left_col:
    st.markdown("### 🔍 학생 검색 및 출결 관리")
    
    # 검색창
    search_query = st.text_input("번호 또는 이름 검색 (예: 104 최하은)", key="student_search")
    
    # 필터링
    filtered_list = st.session_state.students
    if search_query:
        filtered_list = [
            s for s in st.session_state.students 
            if search_query in s["학번"] or search_query in s["이름"]
        ]

    st.markdown("#### 🚨 실시간 미등교(결석) 학생")
    absent_list = [s for s in filtered_list if s["상태"] == "결석"]
    
    if absent_list:
        for student in absent_list:
            with st.container():
                st.markdown(f"""
                <div class="absent-card">
                    <strong>🔴 [{student['학번']}] {student['이름']}</strong><br/>
                    <small>사유: {student['메모'] if student['메모'] else '사유 미작성'}</small>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                if c1.button("출석으로 변경", key=f"att_{student['학번']}"):
                    student["상태"] = "출석"
                    st.rerun()
                if c2.button("📞 연락처 보기", key=f"call_{student['학번']}"):
                    st.info(f"{student['이름']} 학생 연락처: {student['전화번호']}")
    else:
        st.success("미등교 학생이 없습니다.")

    st.divider()
    
    # 학생 상태 직접 수정 폼 (학생 셀프 체크 영역)
    with st.expander("📝 본인 출결 정보 등록/수정"):
        selected_id = st.selectbox("본인 학번 선택", [s["학번"] + " " + s["이름"] for s in st.session_state.students])
        target_id = selected_id.split()[0]
        
        target_student = next(s for s in st.session_state.students if s["학번"] == target_id)
        
        new_status = st.radio("출결 상태", ["출석", "결석"], index=0 if target_student["상태"] == "출석" else 1, key="status_radio")
        new_memo = st.text_input("결석 사유 (결석일 경우 작성)", value=target_student["메모"])
        
        if st.button("출결 정보 저장"):
            target_student["상태"] = new_status
            target_student["메모"] = new_memo if new_status == "결석" else ""
            st.success(f"{target_student['이름']} 학생의 출결 상태가 업데이트되었습니다.")
            st.rerun()

# ==========================================
# [중앙 컬럼] 오늘의 학급 현황, 달력, 교시별 시간표
# ==========================================
with center_col:
    # 현황 요약 카드
    total_count = len(st.session_state.students)
    absent_cnt = sum(1 for s in st.session_state.students if s["상태"] == "결석")
    present_cnt = total_count - absent_cnt
    absent_names = ", ".join([s["이름"] for s in st.session_state.students if s["상태"] == "결석"])

    st.subheader("📅 오늘의 학급 현황 (3학년 2반)")
    st.info(f"**총원:** {total_count}명 | **출석:** {present_cnt}명 | **결석:** {absent_cnt}명\n\n(결석자: {absent_names if absent_names else '없음'})")
    
    # 달력 표시 (날짜 선택)
    selected_date = st.date_input("일정 및 결석 예정 조회", datetime.date.today())
    
    st.markdown("#### 🕒 오늘의 수업 시간표")
    timetable = [
        {"time": "09:00 - 10:00", "period": "1교시", "subject": "국어", "teacher": "이여명"},
        {"time": "10:10 - 11:10", "period": "2교시", "subject": "수학", "teacher": "이여자"},
        {"time": "11:20 - 12:20", "period": "3교시", "subject": "영어", "teacher": "영어일"},
        {"time": "12:20 - 13:20", "period": "4교시", "subject": "영업", "teacher": "고상사"},
        {"time": "13:30 - 14:30", "period": "5교시", "subject": "과학", "teacher": "과학사"},
        {"time": "14:40 - 15:10", "period": "6교시", "subject": "청소", "teacher": "고상사"},
    ]
    
    for item in timetable:
        st.markdown(f"""
        <div class="schedule-card">
            <strong>[{item['period']}] {item['subject']}</strong> ({item['teacher']} 선생님)<br/>
            <small>⏱️ {item['time']}</small>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# [우측 컬럼] 통계 대시보드 및 설정 관리
# ==========================================
with right_col:
    st.subheader("📊 통계 대보 (출결 데이터)")
    
    # 이미지 디자인 속 시각화 차트 구현
    chart_data = pd.DataFrame({
        "요일": ["월", "화", "수", "목", "금"],
        "결석 인원": [12, 11, 14, 18, 11]
    }).set_index("요일")
    
    st.markdown("**주간 자동 집계**")
    st.bar_chart(chart_data)

    st.markdown("**월간 자동 집계 비율**")
    pie_data = pd.DataFrame({
        "구분": ["출석", "병결", "무단결석"],
        "비율": [85, 10, 5]
    }).set_index("구분")
    st.line_chart(pie_data)

    st.divider()

    st.subheader("⚙️ 설정 및 관리")
    with st.expander("👤 계정 정보"):
        st.write("로그인 계정: 교사 전용 (admin@school.es.kr)")
    with st.expander("🔔 알림 설정"):
        st.checkbox("미등교 학생 발생 시 알림 수신", value=True)
    with st.expander("📁 기능 및 관리"):
        st.button("📄 출결 보고서 다운로드 (CSV)")
        st.button("☁️ 데이터 백업 및 복원")
        st.button("📢 공지사항 관리")
