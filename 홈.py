import streamlit as st
import pandas as pd
from datetime import datetime, date

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="출결 관리 - 선생님을 위한 스마트 출결 지원 시스템",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Custom CSS for White Background + Baby Pink Buttons
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* 전체 배경 및 사이드바 배경: 하얀색 */
    .stApp, section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
    }
    
    section[data-testid="stSidebar"] {
        border-right: 1px solid #F1F5F9;
    }

    /* 메인 타이틀 & 텍스트 색상 */
    h1, h2, h3 {
        color: #334155 !important;
    }
    p, span, label {
        color: #475569;
    }

    /* 버튼 공통 스타일 (베이비 핑크) */
    div.stButton > button {
        background-color: #FFB3C1 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        background-color: #FF8FAB !important;
        box-shadow: 0 4px 10px rgba(255, 143, 171, 0.3) !important;
    }

    /* Primary 버튼 (바로가기 버튼 등 강조 버튼) */
    div.stButton > button[kind="primary"] {
        background-color: #FF8FAB !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #FB6F92 !important;
    }

    /* Link Button (외부 사이트 링크 버튼) */
    a[data-testid="stLinkButton"] {
        background-color: #FFB3C1 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
    }
    a[data-testid="stLinkButton"]:hover {
        background-color: #FF8FAB !important;
    }

    /* 검색창 스타일링 */
    .stTextInput > div > div > input {
        border-radius: 8px !important;
        border: 1.5px solid #FFCCD5 !important;
        background-color: #FFFFFF !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #FF8FAB !important;
        box-shadow: 0 0 0 2px rgba(255, 143, 171, 0.2) !important;
    }

    /* 4대 기능 카드 스타일 (하얀 배경 + 은은한 핑크 테두리) */
    .card-container {
        background-color: #FFFFFF;
        border-radius: 14px;
        padding: 20px;
        border: 1px solid #FFE3E8;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
        height: 100%;
        margin-bottom: 10px;
    }
    
    .card-icon {
        font-size: 2rem;
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 10px;
        margin-bottom: 12px;
    }

    /* 각 카드 소프트 아이콘 배경 */
    .bg-pink-1 { background-color: #FFF0F3; color: #FF758F; }
    .bg-pink-2 { background-color: #FFE5EC; color: #FF8FAB; }
    .bg-pink-3 { background-color: #FFD6FF; color: #D883FF; }
    .bg-pink-4 { background-color: #FFE4E6; color: #FB7185; }

    .card-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 6px;
    }
    .card-desc {
        font-size: 0.88rem;
        color: #64748B;
        margin-bottom: 15px;
        min-height: 42px;
        line-height: 1.4;
    }

    /* 최근 사용 기능 / 사이트 가이드 박스 */
    .info-card {
        background-color: #FFFFFF;
        border-radius: 14px;
        padding: 20px;
        border: 1px solid #FFE3E8;
    }

    /* Expander 핑크 톤 적용 */
    .streamlit-expanderHeader {
        background-color: #FFF5F7 !important;
        border-radius: 8px !important;
        color: #334155 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Session State Initialization (Data Persistence)
# ---------------------------------------------------------
if 'current_page' not in st.session_state:
    st.session_state.current_page = "홈"

if 'recent_features' not in st.session_state:
    st.session_state.recent_features = [
        {"name": "오늘 출결 기록", "desc": "오늘의 출석 현황을 확인할 수 있어요.", "time": "오늘 10:24"},
        {"name": "결석 학생 확인", "desc": "결석한 학생 목록을 확인할 수 있어요.", "time": "어제 16:32"},
        {"name": "학부모 문자 발송", "desc": "출결 관련 문자를 발송할 수 있어요.", "time": "어제 14:17"}
    ]

def add_recent_feature(name, desc):
    """최근 사용한 기능 업데이트"""
    now_str = datetime.now().strftime("%H:%M")
    new_item = {"name": name, "desc": desc, "time": f"오늘 {now_str}"}
    
    st.session_state.recent_features = [f for f in st.session_state.recent_features if f["name"] != name]
    st.session_state.recent_features.insert(0, new_item)
    st.session_state.recent_features = st.session_state.recent_features[:4]

# 기본 학생 데이터 초기화
if 'students_df' not in st.session_state:
    st.session_state.students_df = pd.DataFrame([
        {"번호": 1, "이름": "강민우", "학부모": "강태성", "연락처": "010-1234-5678", "비상연락처": "010-1111-2222"},
        {"번호": 2, "이름": "김서연", "학부모": "이영희", "연락처": "010-2345-6789", "비상연락처": "010-2222-3333"},
        {"번호": 3, "이름": "박지훈", "학부모": "박준호", "연락처": "010-3456-7890", "비상연락처": "010-3333-4444"},
        {"번호": 4, "이름": "이지은", "학부모": "정경숙", "연락처": "010-4567-8901", "비상연락처": "010-4444-5555"},
        {"번호": 5, "이름": "최현우", "학부모": "최성진", "연락처": "010-5678-9012", "비상연락처": "010-5555-6666"}
    ])

# 출결 기록 초기화
if 'attendance_records' not in st.session_state:
    today_str = str(date.today())
    st.session_state.attendance_records = pd.DataFrame([
        {"날짜": today_str, "번호": 1, "이름": "강민우", "상태": "출석", "사유": ""},
        {"날짜": today_str, "번호": 2, "이름": "김서연", "상태": "출석", "사유": ""},
        {"날짜": today_str, "번호": 3, "이름": "박지훈", "상태": "미확인 결석", "사유": "연락 필요"},
        {"날짜": today_str, "번호": 4, "이름": "이지은", "상태": "출석", "사유": ""},
        {"날짜": today_str, "번호": 5, "이름": "최현우", "상태": "지각", "사유": "병원 진료"}
    ])

# ---------------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------------
st.sidebar.markdown("### 🌸 출결 관리")
st.sidebar.caption("선생님 전용 스마트 관리 도구")

page_options = {
    "홈": "🏠 홈",
    "리스트": "👤 학생 관리",
    "출결 기록": "📅 출결 기록",
    "학부모 연결": "👨‍👩‍👧 학부모 연결",
    "자동 문자": "✉️ 자동 문자"
}

selected_label = st.sidebar.radio(
    "메뉴 선택",
    options=list(page_options.values()),
    index=list(page_options.keys()).index(st.session_state.current_page)
)

# 사이드바 선택 변경 시 세션 페이지 업데이트
for key, val in page_options.items():
    if val == selected_label:
        st.session_state.current_page = key

st.sidebar.divider()
st.sidebar.caption("❓ 도움이 필요하신가요?\n고객센터: 1588-1234")


# ---------------------------------------------------------
# Page 1: 홈 (내부 페이지 연동 바로가기 버튼 적용)
# ---------------------------------------------------------
if st.session_state.current_page == "홈":
    st.title("안녕하세요!")
    st.write("출결 관리를 더 쉽고 편리하게, 지금 바로 시작해보세요.")

    # 1. 검색창 영역
    search_col1, search_col2 = st.columns([5, 1])
    with search_col1:
        search_query = st.text_input(
            "검색", 
            placeholder="출결 기능을 검색해 보세요. (예: 학생 결석 처리, 지각 수정, 출결 통계, 학부모에게 문자 보내기 등)",
            label_visibility="collapsed"
        )
    with search_col2:
        search_clicked = st.button("검색", type="primary", use_container_width=True)

    # 추천 검색어 버튼들
    st.markdown("**추천 검색어**")
    kw_col1, kw_col2, kw_col3, kw_col4, kw_col5 = st.columns(5)
    
    if kw_col1.button("학생 결석 처리", use_container_width=True):
        st.session_state.current_page = "출결 기록"
        add_recent_feature("오늘 출결 기록", "오늘의 출석 현황 확인 및 결석 처리")
        st.rerun()
    if kw_col2.button("지각 수정", use_container_width=True):
        st.session_state.current_page = "출결 기록"
        add_recent_feature("오늘 출결 기록", "지각 현황 수정 및 기록")
        st.rerun()
    if kw_col3.button("출결 통계", use_container_width=True):
        st.session_state.current_page = "출결 기록"
        add_recent_feature("오늘 출결 기록", "학급 출결 통계 확인")
        st.rerun()
    if kw_col4.button("학부모에게 문자 보내기", use_container_width=True):
        st.session_state.current_page = "자동 문자"
        add_recent_feature("학부모 문자 발송", "출결 관련 문자를 발송 및 연동")
        st.rerun()
    if kw_col5.button("출석 기록 확인", use_container_width=True):
        st.session_state.current_page = "출결 기록"
        add_recent_feature("오늘 출결 기록", "전체 출석 기록 확인")
        st.rerun()

    # 검색 입력 처리
    if search_query:
        if any(k in search_query for k in ["결석", "지각", "출석", "통계"]):
            st.info(f"🔍 '{search_query}' 검색 결과: **[출결 기록]** 페이지로 이동합니다.")
            if st.button("출결 기록 페이지로 이동"):
                st.session_state.current_page = "출결 기록"
                add_recent_feature("오늘 출결 기록", "출결 기록 페이지 접근")
                st.rerun()
        elif any(k in search_query for k in ["문자", "발송", "알림"]):
            st.info(f"🔍 '{search_query}' 검색 결과: **[자동 문자]** 페이지로 이동합니다.")
            if st.button("자동 문자 페이지로 이동"):
                st.session_state.current_page = "자동 문자"
                add_recent_feature("학부모 문자 발송", "자동 문자 페이지 접근")
                st.rerun()
        elif any(k in search_query for k in ["학생", "명단", "학부모"]):
            st.info(f"🔍 '{search_query}' 검색 결과: **[학생 관리 / 학부모 연결]** 페이지로 이동합니다.")
            if st.button("학부모 연결 페이지로 이동"):
                st.session_state.current_page = "학부모 연결"
                add_recent_feature("결석 학생 확인", "학부모 연결 페이지 접근")
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. 주요 4가지 기능 카드 레이아웃 (내부 페이지 바로가기 연결)
    c1, c2, c3, c4 = st.columns(4)

    # [카드 1] 리스트 페이지 바로가기
    with c1:
        st.markdown("""
        <div class="card-container">
            <div class="card-icon bg-pink-1">👥</div>
            <div class="card-title">리스트</div>
            <div class="card-desc">학생 명단 및 반/그룹을 관리할 수 있어요.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("바로가기 ➔", key="btn_goto_list", type="primary", use_container_width=True):
            st.session_state.current_page = "리스트"
            add_recent_feature("학생 관리 (리스트)", "학생 명단 및 반 정보 관리")
            st.rerun()
        
        # 하단 사용 방법 클릭 시 해당 페이지로 안내
        if st.button("🔗 [사용 방법] 학생 추가 방법", key="guide_list", use_container_width=True):
            st.session_state.current_page = "리스트"
            st.rerun()

    # [카드 2] 출결 기록 페이지 바로가기
    with c2:
        st.markdown("""
        <div class="card-container">
            <div class="card-icon bg-pink-2">📅</div>
            <div class="card-title">출결 기록</div>
            <div class="card-desc">출석, 지각, 결석 등 출결 상태를 기록하고 관리할 수 있어요.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("바로가기 ➔", key="btn_goto_record", type="primary", use_container_width=True):
            st.session_state.current_page = "출결 기록"
            add_recent_feature("오늘 출결 기록", "오늘의 출석 현황 확인 및 처리")
            st.rerun()
        
        if st.button("🔗 [사용 방법] 출석 처리 방법", key="guide_record", use_container_width=True):
            st.session_state.current_page = "출결 기록"
            st.rerun()

    # [카드 3] 학부모 연결 페이지 바로가기
    with c3:
        st.markdown("""
        <div class="card-container">
            <div class="card-icon bg-pink-3">👨‍👩‍👧</div>
            <div class="card-title">학부모 연결</div>
            <div class="card-desc">학부모 연락처를 관리하고 소통할 수 있어요.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("바로가기 ➔", key="btn_goto_parents", type="primary", use_container_width=True):
            st.session_state.current_page = "학부모 연결"
            add_recent_feature("결석 학생 확인", "미확인 결석 학생 명단 및 비상 연락처 조회")
            st.rerun()
        
        if st.button("🔗 [사용 방법] 학부모 정보 등록", key="guide_parents", use_container_width=True):
            st.session_state.current_page = "학부모 연결"
            st.rerun()

    # [카드 4] 자동 문자 페이지 바로가기
    with c4:
        st.markdown("""
        <div class="card-container">
            <div class="card-icon bg-pink-4">✉️</div>
            <div class="card-title">자동 문자</div>
            <div class="card-desc">출결 상황에 따른 문자 발송 및 예약을 할 수 있어요.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("바로가기 ➔", key="btn_goto_sms", type="primary", use_container_width=True):
            st.session_state.current_page = "자동 문자"
            add_recent_feature("학부모 문자 발송", "출결 관련 문자를 발송 및 외부 발송 연동")
            st.rerun()
            
        if st.button("🔗 [사용 방법] 문자 발송 방법", key="guide_sms", use_container_width=True):
            st.session_state.current_page = "자동 문자"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. 최근 사용한 기능 & 사이트 사용 가이드
    bot_col1, bot_col2 = st.columns(2)

    with bot_col1:
        st.markdown("### 💡 최근 사용한 기능")
        st.caption("선생님이 최근에 바로가기 버튼으로 이용하신 기능입니다.")
        for rf in st.session_state.recent_features:
            with st.expander(f"📌 {rf['name']} ({rf['time']})"):
                st.write(rf['desc'])

    with bot_col2:
        st.markdown("### 📖 사이트 사용 가이드")
        st.caption("각 기능 및 외부 발송 서비스의 자세한 사용 방법을 확인해보세요.")
        
        guides = [
            ("나이스(NEIS) 교무업무 문자 서비스", "https://www.neis.go.kr", "나이스 교무업무 -> 학급담임 -> 출결관리 -> SMS 발송 메뉴 이용"),
            ("학교알리미 통보 서비스", "https://www.schoolinfo.go.kr", "학교알리미 알림장 및 출결 통지 전송 모듈"),
            ("메세지미 학교전용 문자", "https://www.messageme.co.kr", "학교 맞춤형 대량 SMS/LMS 발송 서비스"),
            ("뿌리오 관공서 문자서비스", "https://www.ppurio.com", "단체 문자 및 예약 발송 시스템")
        ]
        
        for name, url, desc in guides:
            st.markdown(f"- **[{name}]({url})**: {desc}")


# ---------------------------------------------------------
# Page 2: 학생 관리 (리스트)
# ---------------------------------------------------------
elif st.session_state.current_page == "리스트":
    st.title("👤 학생 관리 (리스트)")
    st.write("학급 학생 명단과 학부모 연락처 정보를 관리합니다.")

    edited_students = st.data_editor(
        st.session_state.students_df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True
    )
    
    if st.button("💾 학생 명단 저장", type="primary"):
        st.session_state.students_df = edited_students
        st.success("학생 명단이 저장되었습니다!")


# ---------------------------------------------------------
# Page 3: 출결 기록
# ---------------------------------------------------------
elif st.session_state.current_page == "출결 기록":
    st.title("📅 출결 기록 및 관리")
    st.write(f"오늘 날짜({date.today()})의 출결 현황을 기록하고 변경합니다.")

    today_str = str(date.today())
    today_df = st.session_state.attendance_records[
        st.session_state.attendance_records["날짜"] == today_str
    ].copy()

    status_options = ["출석", "미확인 결석", "인정 결석", "질병 결석", "지각", "조퇴"]

    edited_att = st.data_editor(
        today_df,
        column_config={
            "상태": st.column_config.SelectboxColumn("출결 상태", options=status_options, required=True),
            "사유": st.column_config.TextColumn("사유 및 비고", width="large")
        },
        disabled=["날짜", "번호", "이름"],
        hide_index=True,
        use_container_width=True
    )

    if st.button("💾 당일 출결 기록 저장", type="primary"):
        st.session_state.attendance_records = pd.concat([
            st.session_state.attendance_records[st.session_state.attendance_records["날짜"] != today_str],
            edited_att
        ], ignore_index=True)
        st.success("출결 기록이 정상적으로 저장되었습니다.")


# ---------------------------------------------------------
# Page 4: 학부모 연결
# ---------------------------------------------------------
elif st.session_state.current_page == "학부모 연결":
    st.title("👨‍👩‍👧 학부모 연결 센터")
    st.write("미확인 결석자 및 주의가 필요한 학생의 학부모 연락처를 확인합니다.")

    today_str = str(date.today())
    today_att = st.session_state.attendance_records[st.session_state.attendance_records["날짜"] == today_str]
    unconfirmed = today_att[today_att["상태"] == "미확인 결석"]

    st.subheader("🚨 오늘 연락 필요 학생 (미확인 결석자)")
    
    if not unconfirmed.empty:
        for _, row in unconfirmed.iterrows():
            s_match = st.session_state.students_df[st.session_state.students_df["이름"] == row["이름"]]
            if not s_match.empty:
                s_info = s_match.iloc[0]
                with st.warning(f"⚠️ **{row['이름']}** 학생 (번호: {row['번호']})"):
                    st.write(f"• 학부모: **{s_info['학부모']}** | 주연락처: **{s_info['연락처']}** | 비상연락처: **{s_info['비상연락처']}**")
                    if st.button(f"✉️ {row['이름']} 학생 문자 작성하기", key=f"btn_link_{row['번호']}"):
                        st.session_state.target_student = row['이름']
                        st.session_state.current_page = "자동 문자"
                        st.rerun()
    else:
        st.success("🎉 현재 미확인 결석자가 없습니다.")

    st.divider()
    st.subheader("📋 전체 학생/학부모 연락처 목록")
    st.dataframe(st.session_state.students_df, use_container_width=True, hide_index=True)


# ---------------------------------------------------------
# Page 5: 자동 문자
# ---------------------------------------------------------
elif st.session_state.current_page == "자동 문자":
    st.title("✉️ 자동 문자 발송 및 외부분송 연동")
    st.write("상황에 맞는 문구를 작성하여 학교 전용 발송 시스템으로 전달합니다.")

    target_name = st.session_state.get("target_student", st.session_state.students_df["이름"].iloc[0])
    selected_student = st.selectbox("수신 학생 선택", st.session_state.students_df["이름"].unique(), index=list(st.session_state.students_df["이름"].unique()).index(target_name) if target_name in st.session_state.students_df["이름"].unique() else 0)

    s_info = st.session_state.students_df[st.session_state.students_df["이름"] == selected_student].iloc[0]

    tab1, tab2 = st.tabs(["📄 표준 템플릿 문구", "🤖 AI 맞춤 문구 생성 (Gemini)"])

    with tab1:
        st.caption("상황을 선택하면 문구가 자동 생성됩니다.")
        msg_type = st.radio("문자 유형", ["기본 미확인 결석 알림", "긴급 비상 연락 요청", "등교 지각 확인"], horizontal=True)
        
        if msg_type == "기본 미확인 결석 알림":
            draft = f"[OO학교 출결 안내]\n안녕하세요, {s_info['학부모']} 학부모님. 오늘 {selected_student} 학생이 등교하지 않아 확인차 연락드립니다. 확인 후 담임교사에게 연락 부탁드립니다."
        elif msg_type == "긴급 비상 연락 요청":
            draft = f"[🚨긴급 OO학교 출결 확인]\n안녕하세요, {s_info['학부모']} 학부모님. 현재 {selected_student} 학생의 연락 및 위치가 확인되지 않아 연락드립니다. 메시지를 확인하시는 대로 즉시 연락 바랍니다."
        else:
            draft = f"[OO학교 지각 안내]\n안녕하세요, {s_info['학부모']} 학부모님. {selected_student} 학생이 등교 시각보다 지연 등교하여 안내드립니다. 사유가 있으신 경우 말씀해 주세요."

        st.text_area("📋 생성된 문자 문구 (클립보드 복사용)", draft, height=130)
        st.info(f"📱 수신자: {s_info['학부모']} ({s_info['연락처']})")

    with tab2:
        api_key = st.secrets.get("GEMINI_API_KEY", None)
        if not api_key:
            st.warning("⚠️ Gemini API 키가 설정되지 않았습니다. Secrets에 `GEMINI_API_KEY`를 추가해주세요.")
        else:
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                
                user_prompt = st.text_input("AI에게 요청할 상황 설명", f"{selected_student} 학생이 연락 없이 무단 결석 중인데 정중하고 걱정스러운 어조로 학부모님께 보낼 문자를 작성해줘.")
                
                if st.button("✨ AI 문구 생성하기", type="primary"):
                    with st.spinner("Gemini AI가 문구를 생성하고 있습니다..."):
                        response = client.models.generate_content(
                            model='gemini-2.5-flash-lite',
                            contents=user_prompt,
                        )
                        st.success("문구 생성 완료!")
                        st.text_area("🤖 AI 추천 문자 문구", response.text, height=150)
            except Exception as e:
                st.error(f"API 오류 발생: {str(e)}")

    st.divider()

    st.subheader("🌐 학교 발송 시스템 바로가기")
    st.write("아래 버튼을 클릭하여 각 학교에서 사용하는 문자 발송 사이트로 이동하세요.")

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)

    with col_s1:
        st.markdown("**나이스(NEIS) 대국민**")
        st.caption("학교 공식 행정/교무업무 SMS 연동")
        st.link_button("👉 나이스 바로가기", "https://www.neis.go.kr")

    with col_s2:
        st.markdown("**학교알리미**")
        st.caption("학부모 알림장 및 출결 통지 전송")
        st.link_button("👉 학교알리미 바로가기", "https://www.schoolinfo.go.kr")

    with col_s3:
        st.markdown("**메세지미**")
        st.caption("학교 전용 대량 및 예약 문자")
        st.link_button("👉 메세지미 바로가기", "https://www.messageme.co.kr")

    with col_s4:
        st.markdown("**뿌리오**")
        st.caption("관공서 및 교육기관 문자 서비스")
        st.link_button("👉 뿌리오 바로가기", "https://www.ppurio.com")
