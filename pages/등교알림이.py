import streamlit as st
import pandas as pd
import datetime

# 1. 페이지 레이아웃 및 스타일 설정
st.set_page_config(
    page_title="등교 알림이",
    page_icon="🏫",
    layout="wide"
)

# Custom CSS로 초록색(Green) 계열 테마 적용
st.markdown("""
<style>
    /* 전체 배경색: 연한 쑥색/민트빛 밝은 배경 */
    .stApp {
        background-color: #f2f7f4;
    }
    
    /* 각 카드 영역 컴포넌트 */
    div[data-testid="stVerticalBlock"] > div {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 2px 6px rgba(46, 125, 50, 0.08);
        border: 1px solid #e0ebd9;
        margin-bottom: 10px;
    }
    
    /* 타이틀 및 헤더 텍스트 색상 (짙은 초록) */
    h1, h2, h3, .stSubheader {
        color: #1b4332 !important;
    }
    
    /* 결석자/미등교 경고 카드 */
    .stAlert {
        border-radius: 8px;
    }
    
    /* 버튼 스타일 초록색으로 통일 */
    .stButton > button {
        background-color: #2d6a4f;
        color: white;
        border-radius: 8px;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #1b4332;
        color: #d8f3dc;
    }
</style>
""", unsafe_allow_html=True)

# 2. 데이터 초기화 (세션 상태 관리)
if "students" not in st.session_state:
    st.session_state.students = [
        {"번호": "104", "이름": "최하은", "상태": "결석", "사유": "감기 몸살", "교시": "전체"},
        {"번호": "106", "이름": "강수아", "상태": "결석", "사유": "병원 진료", "교시": "1~2교시"},
        {"번호": "107", "이름": "윤호진", "상태": "결석", "사유": "체험 학습", "교시": "전체"},
        {"번호": "101", "이름": "김민준", "상태": "출석", "사유": "", "교시": ""},
        {"번호": "102", "이름": "박서연", "상태": "출석", "사유": "", "교시": ""},
        {"번호": "103", "이름": "이도윤", "상태": "출석", "사유": "", "교시": ""},
    ]

# 3. 메인 화면 3컬럼 레이아웃 구성
col_left, col_center, col_right = st.columns([1, 1.2, 1])

# [왼쪽 컬럼] 검색 및 실시간 미등교 학생 관리
with col_left:
    st.title("🏫 등교 알림이")
    st.caption(f"🌿 {datetime.date.today().strftime('%Y년 %m월 %d일')}")
    
    # 학생 검색창
    search_query = st.text_input("🔍 번호 또는 이름 검색", placeholder="예: 104 또는 최하은")
    
    st.subheader("🚨 실시간 미등교 학생")
    
    # 미등교/결석 학생 필터링
    absent_students = [s for s in st.session_state.students if s["상태"] == "결석"]
    
    if search_query:
        absent_students = [s for s in absent_students if search_query in s["번호"] or search_query in s["이름"]]
        
    if absent_students:
        for student in absent_students:
            st.warning(f"**[{student['번호']}] {student['이름']}** | {student['상태']} ({student['교시']})\n\n📝 사유: {student['사유']}")
    else:
        st.success("🌱 현재 미등교/결석 학생이 없습니다.")
        
    st.divider()
    
    # 학생 직접 결석 및 사유 등록
    with st.expander("➕ 학생 직접 출결 입력 / 수정", expanded=False):
        with st.form("attendance_form"):
            target_student = st.selectbox(
                "학생 선택", 
                options=[f"{s['번호']} {s['이름']}" for s in st.session_state.students]
            )
            status_choice = st.radio("출결 상태", ["출석", "결석"], horizontal=True)
            period_choice = st.selectbox("결석/빠지는 교시", ["전체 (하루종일)", "1~2교시", "3~4교시", "5~6교시"])
            reason_input = st.text_input("결석 사유 직접 적기", placeholder="예: 병원 방문, 개인 사정 등")
            
            submit_btn = st.form_submit_button("상태 저장하기")
            
            if submit_btn:
                target_num = target_student.split()[0]
                for s in st.session_state.students:
                    if s["번호"] == target_num:
                        s["상태"] = status_choice
                        s["사유"] = reason_input if status_choice == "결석" else ""
                        s["교시"] = period_choice if status_choice == "결석" else ""
                st.success("출결 정보가 변경되었습니다.")
                st.rerun()

# [중앙 컬럼] 오늘의 학급 현황 및 학교 시간표
with col_center:
    total_cnt = len(st.session_state.students)
    absent_cnt = sum(1 for s in st.session_state.students if s["상태"] == "결석")
    present_cnt = total_cnt - absent_cnt
    
    absent_names = ", ".join([s["이름"] for s in st.session_state.students if s["상태"] == "결석"])
    if not absent_names:
        absent_names = "없음"
        
    st.markdown(f"""
    ### 📊 오늘의 학급 현황 (3학년 2반)
    **총원 {total_cnt}명 / 출석 <span style='color:#2d6a4f;'>{present_cnt}명</span> / 결석 <span style='color:#e63946;'>{absent_cnt}명</span>**  
    *(결석 명단: {absent_names})*
    """, unsafe_allow_html=True)
    
    # 주간 미니 달력 표기
    st.date_input("📅 결석 예정일 등록 / 달력 확인", datetime.date.today())
    
    st.subheader("📚 오늘의 학교 시간표")
    timetable_data = [
        {"교시": "1교시 (09:00~10:00)", "과목": "국어", "담당": "이여명"},
        {"교시": "2교시 (10:10~11:10)", "과목": "수학", "담당": "이여자"},
        {"교시": "3교시 (11:20~12:20)", "과목": "영어", "담당": "영어일"},
        {"교시": "4교시 (12:20~13:20)", "과목": "사회", "담당": "고상사"},
        {"교시": "5교시 (13:30~14:30)", "과목": "과학", "담당": "과학사"},
        {"교시": "6교시 (14:40~15:10)", "과목": "청소", "담당": "고상사"},
    ]
    st.table(pd.DataFrame(timetable_data))

# [오른쪽 컬럼] 통계 대보 및 설정
with col_right:
    st.subheader("📈 주간 결석 통계")
    
    # 주간 출결 통계 데이터
    chart_data = pd.DataFrame({
        "요일": ["월", "화", "수", "목", "금"],
        "결석 건수": [2, 1, 4, 3, 1]
    }).set_index("요일")
    
    # 막대 그래프 출력
    st.bar_chart(chart_data, color="#2d6a4f")
    
    st.divider()
    
    st.subheader("⚙️ 설정 및 관리")
    st.button("👤 계정 정보 관리", use_container_width=True)
    st.button("🔔 알림 수신 설정", use_container_width=True)
    st.button("📄 출결 보고서 다운로드 (CSV)", use_container_width=True)
    st.button("💾 데이터 백업 및 복원", use_container_width=True)
