import streamlit as st
import pandas as pd
import datetime

# 1. 페이지 레이아웃 및 카드 스타일 설정
st.set_page_config(
    page_title="등교 알림이",
    page_icon="🏫",
    layout="wide"
)

st.markdown("""
<style>
    .stApp {
        background-color: #f4f6f9;
    }
    div[data-testid="stVerticalBlock"] > div {
        background-color: white;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 10px;
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

# 3. 메인 화면 3컬럼 레이아웃
col_left, col_center, col_right = st.columns([1, 1.2, 1])

# ==========================================
# [왼쪽 컬럼] 검색, 학생 추가, 미등교 관리
# ==========================================
with col_left:
    st.title("🏫 등교 알림이")
    st.caption(f"📅 {datetime.date.today().strftime('%Y년 %m월 %d일')}")
    
    # 🆕 1. 학생 신규 등록 기능
    with st.expander("➕ 새 학생 추가하기", expanded=False):
        with st.form("add_student_form", clear_on_submit=True):
            new_num = st.text_input("학번 / 번호 입력", placeholder="예: 108")
            new_name = st.text_input("학생 이름 입력", placeholder="예: 홍길동")
            add_btn = st.form_submit_button("학생 등록하기")
            
            if add_btn:
                if not new_num.strip() or not new_name.strip():
                    st.error("학번과 이름을 모두 입력해 주세요.")
                elif any(s["번호"] == new_num.strip() for s in st.session_state.students):
                    st.warning("이미 존재하는 학번/번호입니다.")
                else:
                    st.session_state.students.append({
                        "번호": new_num.strip(),
                        "이름": new_name.strip(),
                        "상태": "출석",
                        "사유": "",
                        "교시": ""
                    })
                    st.success(f"[{new_num}] {new_name} 학생이 명단에 추가되었습니다!")
                    st.rerun()

    # 2. 학생 검색창
    search_query = st.text_input("🔍 번호 또는 이름 검색", placeholder="예: 104 또는 최하은")
    
    st.subheader("🚨 실시간 미등교 학생")
    
    # 미등교/결석 학생 필터링
    absent_students = [s for s in st.session_state.students if s["상태"] == "결석"]
    
    if search_query:
        absent_students = [s for s in absent_students if search_query in s["번호"] or search_query in s["이름"]]
        
    if absent_students:
        for student in absent_students:
            st.error(f"**{student['번호']} {student['이름']}** | {student['상태']} ({student['교시']})\n\n사유: {student['사유']}")
    else:
        st.success("🎉 현재 미등교/결석 학생이 없습니다.")
        
    st.divider()
    
    # 3. 출결 상태 및 사유 등록
    with st.expander("📝 학생 출결 입력 / 수정", expanded=False):
        if not st.session_state.students:
            st.info("등록된 학생이 없습니다. 상단에서 학생을 먼저 추가해 주세요.")
        else:
            with st.form("attendance_form"):
                target_student = st.selectbox(
                    "학생 선택", 
                    options=[f"{s['번호']} {s['이름']}" for s in st.session_state.students]
                )
                status_choice = st.radio("출결 상태", ["출석", "결석"], horizontal=True)
                period_choice = st.selectbox("결석/빠지는 교시", ["전체 (하루종일)", "1~2교시", "3~4교시", "5~6교시"])
                reason_input = st.text_input("결석 사유 직접 적기", placeholder="예: 병원 방문, 개인 사정 등")
                
                submit_btn = st.form_submit_button("상태 저장")
                
                if submit_btn:
                    target_num = target_student.split()[0]
                    for s in st.session_state.students:
                        if s["번호"] == target_num:
                            s["상태"] = status_choice
                            s["사유"] = reason_input if status_choice == "결석" else ""
                            s["교시"] = period_choice if status_choice == "결석" else ""
                    st.success("출결 정보가 갱신되었습니다!")
                    st.rerun()

# ==========================================
# [중앙 컬럼] 오늘의 학급 현황 및 시간표
# ==========================================
with col_center:
    total_cnt = len(st.session_state.students)
    absent_cnt = sum(1 for s in st.session_state.students if s["상태"] == "결석")
    present_cnt = total_cnt - absent_cnt
    
    absent_names = ", ".join([s["이름"] for s in st.session_state.students if s["상태"] == "결석"])
    if not absent_names:
        absent_names = "없음"
        
    st.markdown(f"""
    ### 📊 오늘의 학급 현황 (3학년 2반)
    **총원 {total_cnt}명 / 출석 {present_cnt}명 / 결석 {absent_cnt}명**  
    *(결석: {absent_names})*
    """)
    
    st.date_input("📅 결석 예정일 등록 / 달력 확인", datetime.date.today())
    
    st.subheader("📚 오늘의 학교 시간표")
    timetable_data = [
        {"교시": "1교시 (09:00~10:00)", "과목": "국어", "담당": "이여명"},
        {"교시": "2교시 (10:10~11:10)", "과목": "수학", "담당": "이여자"},
        {"교시": "3교시 (11:20~12:20)", "과목": "영어", "담당": "영어일"},
        {"교시": "4교시 (12:20~13:20)", "과목": "영업", "담당": "고상사"},
        {"교시": "5교시 (13:30~14:30)", "과목": "과학", "담당": "과학사"},
        {"교시": "6교시 (14:40~15:10)", "과목": "청소", "담당": "고상사"},
    ]
    st.table(pd.DataFrame(timetable_data))

# ==========================================
# [오른쪽 컬럼] 통계 및 전체 학생 관리
# ==========================================
with col_right:
    st.subheader("📈 통계 대보")
    
    chart_data = pd.DataFrame({
        "요일": ["월", "화", "수", "목", "금"],
        "결석 건수": [2, 1, 4, 3, 1]
    }).set_index("요일")
    st.bar_chart(chart_data)
    
    st.divider()
    
    st.subheader("⚙️ 전체 학생 명단 및 삭제")
    if st.session_state.students:
        df_students = pd.DataFrame(st.session_state.students)[["번호", "이름", "상태"]]
        st.dataframe(df_students, use_container_width=True)
        
        # 🗑️ 학생 삭제 기능
        delete_target = st.selectbox(
            "삭제할 학생 선택", 
            options=[f"{s['번호']} {s['이름']}" for s in st.session_state.students],
            key="delete_select"
        )
        if st.button("❌ 선택한 학생 명단에서 삭제"):
            del_num = delete_target.split()[0]
            st.session_state.students = [s for s in st.session_state.students if s["번호"] != del_num]
            st.success(f"{delete_target} 학생이 명단에서 삭제되었습니다.")
            st.rerun()
    else:
        st.info("등록된 학생이 없습니다.")
