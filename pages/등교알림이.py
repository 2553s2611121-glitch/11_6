import streamlit as st
import pandas as pd
import datetime

# 1. 페이지 레이아웃 설정
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

# 2. 약 30명의 학생 초기 데이터 생성
if "students" not in st.session_state:
    sample_names = [
        "김민준", "박서연", "이도윤", "최하은", "정지우", 
        "강수아", "윤호진", "임예준", "한지민", "오주원",
        "서유나", "신현우", "권다은", "황도현", "송서현",
        "류민서", "전우진", "홍채원", "고태양", "문소율",
        "양하준", "손지아", "배준혁", "백수빈", "허성민",
        "남윤아", "심건우", "유하은", "노진우", "하은서"
    ]
    
    initial_students = []
    for idx, name in enumerate(sample_names, start=101):
        # 데모용으로 몇몇 학생에게 초기 결석 상태 부여
        if idx in [104, 106, 107, 115]:
            status = "결석"
            reason = "병결 (감기)" if idx == 104 else ("병원 진료" if idx == 106 else "체험 학습")
            period = "1~2교시" if idx == 106 else "전체 (하루종일)"
        else:
            status = "출석"
            reason = ""
            period = ""
            
        initial_students.append({
            "번호": str(idx),
            "이름": name,
            "상태": status,
            "사유": reason,
            "교시": period
        })
        
    st.session_state.students = initial_students

# 3. 메인 화면 레이아웃 (3컬럼)
col_left, col_center, col_right = st.columns([1, 1.2, 1])

# ==========================================
# [왼쪽 컬럼] 검색, 학생 추가, 미등교 관리
# ==========================================
with col_left:
    st.title("🏫 등교 알림이")
    st.caption(f"📅 {datetime.date.today().strftime('%Y년 %m월 %d일')}")
    
    # ➕ 학생 신규 등록
    with st.expander("➕ 새 학생 추가하기", expanded=False):
        with st.form("add_student_form", clear_on_submit=True):
            new_num = st.text_input("학번 / 번호 입력", placeholder="예: 131")
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

    # 🔍 학생 검색창
    search_query = st.text_input("🔍 번호 또는 이름 검색", placeholder="예: 104 또는 최하은")
    
    st.subheader("🚨 실시간 미등교 학생")
    
    absent_students = [s for s in st.session_state.students if s["상태"] == "결석"]
    if
