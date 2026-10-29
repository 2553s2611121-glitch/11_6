import streamlit as st
import pandas as pd
import datetime

# 페이지 레이아웃 설정 (와이드 모드)
st.set_page_config(
    page_title="등교 알림이",
    page_icon="🏫",
    layout="wide"
)

# 파란색 배경 및 스타일 정의 (CSS)
st.markdown("""
<style>
    /* 전체 배경 파란색 계열 적용 */
    .stApp {
        background-color: #8faec4;
    }
    
    /* 각 메인 카드 컴포넌트 스타일 */
    .main-card {
        background-color: #ffffff;
        padding: 18px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 15px;
    }
    
    /* 미등교 학생 (붉은 강조 카드) */
    .absent-card {
        background-color: #fff5f5;
        border-left: 6px solid #e53e3e;
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    
    /* 시간표 카드 (블루 포인트) */
    .schedule-card {
        background-color: #edf2f7;
        border-left: 6px solid #2b6cb0;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
    }

    /* 헤더 및 텍스트 파란 배경 레이아웃에 맞춤 */
    h1, h2, h3, h4 {
        color: #1a365d;
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

# 2. 메인 타이틀
st.title("🏫 등교 알림이")

# 3. 3컬럼 화면 구조
left_col, center_col, right_col = st.columns([1, 1.2, 1])

# ==========================================
# [좌측] 검색, 학생 추가 및 실시간 미등교 학생 관리
# ==========================================
with left_col:
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.subheader("🔍 학생 검색 및 출결")
    
    search_query = st.text_input("번호 또는 이름 검색 (예: 104 최하은)", key="student_search")
    
    filtered_list = st.session_state.students
    if search_query:
        filtered_list = [
            s for s in st.session_state.students 
            if search_query in s["학번"] or search_query in s["이름"]
        ]

    st.markdown("#### 🚨 실시간 미등교 학생")
    absent_list = [s for s in filtered_list if s["상태"] == "결석"]
    
    if absent_list:
        for student in absent_list:
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
                st.info(f"{student['이름']} 연락처: {student['전화번호']}")
    else:
        st.success("미등교 학생이 없습니다.")

    st.divider()
    
    # ➕ 신규 학생 추가 기능
    with st.expander("➕ 신규 학생 등록"):
        with st.form(key="add_student_form", clear_on_submit=True):
            new_id = st.text_input("학번 / 번호 (예: 108)")
            new_name = st.text_input("학생 이름")
            new_phone = st.text_input("연락처", value="010-0000-0000")
            initial_status = st.radio("초기 출결 상태", ["출석", "결석"], horizontal=True)
            initial_memo = st.text_input("초기 사유 (결석 시 작성)")
            
            add_submitted = st.form_submit_button("학생 추가 완료")
            if add_submitted:
                if not new_id.strip() or not new_name.strip():
                    st.error("학번과 이름을 모두 입력해주세요.")
                elif any(s["학번"] == new_id.strip() for s in st.session_state.students):
                    st.error("이미 존재하는 학번입니다.")
                else:
                    st.session_state.students.append({
                        "학번": new_id.strip(),
                        "이름": new_name.strip(),
                        "상태": initial_status,
                        "메모": initial_memo if initial_status == "결석" else "",
                        "전화번호": new_phone.strip()
                    })
                    st.success(f"[{new_id.strip()}] {new_name.strip()} 학생이 등록되었습니다.")
                    st.rerun()

    # 📝 기존 학생 출결 변경 기능
    with st.expander("📝 본인 출결 정보 등록/수정"):
        if st.session_state.students:
            selected_id = st.selectbox("본인 학번 선택", [s["학번"] + " " + s["이름"] for s in st.session_state.students])
            target_id = selected_id.split()[0]
            
            target_student = next(s for s in st.session_state.students if s["학번"] == target_id)
            
            new_status = st.radio("출결 상태", ["출석", "결석"], index=0 if target_student["상태"] == "출석" else 1, key="status_radio")
            new_memo = st.text_input("결석 사유", value=target_student["메모"])
            
            if st.button("출결 정보 저장"):
                target_student["상태"] = new_status
                target_student["메모"] = new_memo if new_status == "결석" else ""
                st.success(f"{target_student['이름']} 학생의 출결 상태가 수정되었습니다.")
                st.rerun()
        else:
            st.info("등록된 학생이 없습니다.")
            
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# [중앙] 학급 현황, 달력, 교시별 시간표
# ==========================================
with center_col:
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    total_count = len(st.session_state.students)
    absent_cnt = sum(1 for s in st.session_state.students if s["상태"] == "결석")
    present_cnt = total_count - absent_cnt
    absent_names = ", ".join([s["이름"] for s in st.session_state.students if s["상태"] == "결석"])

    st.subheader("📅 오늘의 학급 현황 (3학년 2반)")
    st.info(f"**총원:** {total_count}명 | **출석:** {present_cnt}명 | **결석:** {absent_cnt}명\n\n(결석자: {absent_names if absent_names else '없음'})")
    
    selected_date = st.date_input("일정 및 결석 예정 조회", datetime.date.today())
    
    st.markdown("#### 🕒 오늘 수업 시간표")
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
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# [우측] 통계 대시보드 및 설정 관리
# ==========================================
with right_col:
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.subheader("📊 통계 대보")
    
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
    st.markdown("</div>", unsafe_allow_html=True)
