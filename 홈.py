import streamlit as st
import pandas as pd
from datetime import datetime, date
import google.generativeai as genai

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정 및 Custom CSS (이미지 디자인 스타일링)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="스마트 출결 관리 시스템",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS로 깔끔한 카드 및 UI 스타일 적용
st.markdown("""
    <style>
    /* 메인 배경 및 폰트 설정 */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* 카드 스타일링 */
    .feature-card {
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #E2E8F0;
        height: 100%;
    }
    .card-blue { background-color: #EFF6FF; border-top: 4px solid #2563EB; }
    .card-green { background-color: #ECFDF5; border-top: 4px solid #10B981; }
    .card-purple { background-color: #F3E8FF; border-top: 4px solid #9333EA; }
    .card-orange { background-color: #FFF7ED; border-top: 4px solid #F97316; }

    .card-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 8px;
        color: #1E293B;
    }
    .card-desc {
        font-size: 0.9rem;
        color: #64748B;
        min-height: 40px;
        margin-bottom: 15px;
    }
    
    /* 최근 사용 기능 / 가이드 박스 */
    .info-box {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 세션 상태(Session State) 초기화
# -----------------------------------------------------------------------------
if "students" not in st.session_state:
    # 초기 데모 학생 데이터
    st.session_state.students = pd.DataFrame([
        {"학번": 1, "이름": "김민수", "반": "1반", "학부모연락처": "010-1234-5678", "비고": "특이사항 없음"},
        {"학번": 2, "이름": "이서연", "반": "1반", "학부모연락처": "010-2345-6789", "비고": "체육 특기생"},
        {"학번": 3, "이름": "박지훈", "반": "1반", "학부모연락처": "010-3456-7890", "비고": "알레르기 보유"},
        {"학번": 4, "이름": "최유진", "반": "1반", "학부모연락처": "010-4567-8901", "비고": "특이사항 없음"},
        {"학번": 5, "이름": "정현우", "반": "1반", "학부모연락처": "010-5678-9012", "비고": "특이사항 없음"},
    ])

if "attendance_records" not in st.session_state:
    # 당일 기본 출석 기록 데이터
    today_str = str(date.today())
    st.session_state.attendance_records = {
        today_str: {
            "김민수": {"status": "출석", "reason": ""},
            "이서연": {"status": "미락결석", "reason": "연락 없음 (확인 필요)"},
            "박지훈": {"status": "지각", "reason": "병원 진료"},
            "최유진": {"status": "출석", "reason": ""},
            "정현우": {"status": "미락결석", "reason": "연락 없음 (확인 필요)"},
        }
    }

if "recent_activities" not in st.session_state:
    st.session_state.recent_activities = [
        {"time": "오늘 08:50", "activity": "미연락 결석 학생 2명 확인 (이서연, 정현우)"},
        {"time": "어제 16:30", "activity": "학부모 안내 문자 전송 완료"},
        {"time": "어제 14:15", "activity": "출결 기록 수정 및 업데이트"}
    ]

if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 홈"

# Gemini API 설정 함수
def get_gemini_response(prompt):
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        response = model.generate_content(prompt)
        return response.text
    except KeyError:
        return "⚠️ Secrets에 'GEMINI_API_KEY'가 설정되지 않았습니다. 기본 템플릿 문자를 이용해주세요."
    except Exception as e:
        return f"⚠️ API 호출 중 오류가 발생했습니다: {str(e)}"

# 최근 활동 추가 함수
def log_activity(activity_text):
    now_str = datetime.now().strftime("%H:%M")
    st.session_state.recent_activities.insert(0, {"time": f"오늘 {now_str}", "activity": activity_text})
    if len(st.session_state.recent_activities) > 5:
        st.session_state.recent_activities.pop()

# -----------------------------------------------------------------------------
# 3. 사이드바 (Sidebar) 메뉴
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("🛡️ 출결 관리")
    st.caption("선생님을 위한 스마트 출결 연동 시스템")
    st.divider()

    selected_menu = st.radio(
        "메뉴 이동",
        ["🏠 홈", "👤 학생 관리", "📅 출결 기록", "👨‍👩‍👧 학부모 연결", "✉️ 자동 문자"],
        index=["🏠 홈", "👤 학생 관리", "📅 출결 기록", "👨‍👩‍👧 학부모 연결", "✉️ 자동 문자"].index(st.session_state.current_page)
    )
    st.session_state.current_page = selected_menu

    st.divider()
    st.info("💡 **도움이 필요하신가요?**\n고객센터: 1588-1234")

# -----------------------------------------------------------------------------
# 4. 페이지별 구현
# -----------------------------------------------------------------------------

# --- [PAGE 1] 🏠 홈 ---
if st.session_state.current_page == "🏠 홈":
    st.title("안녕하세요, 선생님! 👋")
    st.subheader("출결 관리를 더 쉽고 편리하게, 지금 바로 시작해보세요.")
    
    # 상단 검색창
    search_query = st.text_input("🔍 출결 기능을 검색해 보세요.", placeholder="예: 학생 결석 처리, 지각 수정, 출결 통계, 학부모에게 문자 보내기 등")
    
    if search_query:
        st.success(f"'{search_query}' 검색 결과:")
        if "결석" in search_query or "문자" in search_query:
            st.write("👉 **자동 문자 바로가기** 메뉴 또는 **학부모 연결** 메뉴를 이용해보세요!")
        elif "학생" in search_query or "명단" in search_query:
            st.write("👉 **학생 관리** 메뉴에서 학학 명단 및 연락처를 조회할 수 있습니다.")
        else:
            st.write("👉 왼쪽 사이드바의 해당 메뉴를 선택하시면 기능을 사용하실 수 있습니다.")

    st.write("---")

    # 4가지 핵심 기능 카드 레이아웃
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="feature-card card-blue">
            <div class="card-title">👤 학생 관리</div>
            <div class="card-desc">학생 명단 및 반/그룹을 관리하고 학부모 연락처를 등록합니다.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("바로가기 ➔", key="btn_go_list"):
            st.session_state.current_page = "👤 학생 관리"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="feature-card card-green">
            <div class="card-title">📅 출결 기록</div>
            <div class="card-desc">출석, 지각, 결석 등 일별 출결 상태를 기록하고 확인합니다.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("바로가기 ➔", key="btn_go_record"):
            st.session_state.current_page = "📅 출결 기록"
            st.rerun()

    with col3:
        st.markdown("""
        <div class="feature-card card-purple">
            <div class="card-title">👨‍👩‍👧 학부모 연결</div>
            <div class="card-desc">미연락 결석 학생 학부모 연락처를 즉시 조회하고 연결합니다.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("바로가기 ➔", key="btn_go_parent"):
            st.session_state.current_page = "👨‍👩‍👧 학부모 연결"
            st.rerun()

    with col4:
        st.markdown("""
        <div class="feature-card card-orange">
            <div class="card-title">✉️ 자동 문자</div>
            <div class="card-desc">결석 학생 관련 학부모 안내 문자를 자동 발송 및 예약합니다.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("바로가기 ➔", key="btn_go_sms"):
            st.session_state.current_page = "✉️ 자동 문자"
            st.rerun()

    st.write("---")

    # 하단 2단 레이아웃 (최근 사용한 기능 / 사이트 사용 가이드)
    bot_col1, bot_col2 = st.columns(2)

    with bot_col1:
        st.markdown("### 💡 최근 사용한 기능")
        with st.container():
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            for item in st.session_state.recent_activities:
                st.write(f"⏱️ **{item['time']}** | {item['activity']}")
            st.markdown('</div>', unsafe_allow_html=True)

    with bot_col2:
        st.markdown("### 📖 사이트 사용 가이드")
        with st.container():
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown("🔗 **[학생 관리 사용방법]** 학생 추가, 수정, 반 배정 방법 안내")
            st.markdown("🔗 **[출결 기록 사용방법]** 출석 처리, 지각/결석 변경 및 통계 확인")
            st.markdown("🔗 **[학부모 연결 사용방법]** 무단 결석 학생 대상 원클릭 연결")
            st.markdown("🔗 **[자동 문자 사용방법]** Gemini AI 맞춤 안내 문자 작성 및 발송")
            st.markdown('</div>', unsafe_allow_html=True)


# --- [PAGE 2] 👤 학생 관리 ---
elif st.session_state.current_page == "👤 학생 관리":
    st.title("👤 학생 명단 관리")
    st.caption("학급 학생들의 정보 및 학부모 연락처를 관리합니다.")

    tab1, tab2 = st.tabs(["📋 학생 목록 조회", "➕ 신규 학생 추가"])

    with tab1:
        st.dataframe(st.session_state.students, use_container_width=True)

    with tab2:
        with st.form("add_student_form"):
            num = st.number_input("학번", min_value=1, step=1, value=len(st.session_state.students)+1)
            name = st.text_input("학생 이름")
            cls = st.text_input("반/그룹", value="1반")
            parent_phone = st.text_input("학부모 연락처", placeholder="010-0000-0000")
            note = st.text_input("비고 (특이사항)")
            
            submit = st.form_submit_button("학생 추가 완료")
            if submit:
                if name and parent_phone:
                    new_student = {"학번": num, "이름": name, "반": cls, "학부모연락처": parent_phone, "비고": note}
                    st.session_state.students = pd.concat([st.session_state.students, pd.DataFrame([new_student])], ignore_index=True)
                    log_activity(f"신규 학생 추가 ({name})")
                    st.success(f"{name} 학생이 성공적으로 등록되었습니다.")
                    st.rerun()
                else:
                    st.error("학생 이름과 학부모 연락처를 반드시 입력해주세요.")


# --- [PAGE 3] 📅 출결 기록 ---
elif st.session_state.current_page == "📅 출결 기록":
    st.title("📅 일별 출결 기록 관리")
    
    selected_date = st.date_input("조회/기록 날짜 선택", value=date.today())
    date_key = str(selected_date)

    if date_key not in st.session_state.attendance_records:
        # 해당 날짜 기록 없으면 초기 데이터 생성
        st.session_state.attendance_records[date_key] = {
            row["이름"]: {"status": "출석", "reason": ""} for _, row in st.session_state.students.iterrows()
        }

    st.subheader(f"📌 {date_key} 출결 현황")

    current_records = st.session_state.attendance_records[date_key]
    updated_records = {}

    with st.form("attendance_form"):
        for _, row in st.session_state.students.iterrows():
            s_name = row["이름"]
            default_val = current_records.get(s_name, {"status": "출석", "reason": ""})
            
            c1, c2, c3 = st.columns([1, 1, 2])
            with c1:
                st.write(f"**{row['학번']}번 {s_name}**")
            with c2:
                status = st.selectbox(f"상태_{s_name}", ["출석", "지각", "미락결석", "병결", "조퇴"], 
                                      index=["출석", "지각", "미락결석", "병결", "조퇴"].index(default_val["status"]),
                                      label_visibility="collapsed")
            with c3:
                reason = st.text_input(f"사유_{s_name}", value=default_val["reason"], 
                                       placeholder="결석/지각 사유 입력", label_visibility="collapsed")
            
            updated_records[s_name] = {"status": status, "reason": reason}

        save_btn = st.form_submit_button("💾 출결 기록 저장")
        if save_btn:
            st.session_state.attendance_records[date_key] = updated_records
            log_activity(f"{date_key} 출결 저장 완료")
            st.success("출결 상태가 변경 및 저장되었습니다!")


# --- [PAGE 4] 👨‍👩‍👧 학부모 연결 ---
elif st.session_state.current_page == "👨‍👩‍👧 학부모 연결":
    st.title("👨‍👩‍👧 무단/미연락 결석 학부모 연동")
    st.caption("말 없이 결석한 학생들을 일괄 감지하여 학부모에게 빠르게 연락합니다.")

    today_key = str(date.today())
    records = st.session_state.attendance_records.get(today_key, {})

    # 미연락 결석 대상 추출
    uncontacted = [name for name, data in records.items() if data["status"] == "미락결석"]

    st.subheader(f"🚨 오늘({today_key}) 미연락 결석 학생 목록: {len(uncontacted)}명")

    if uncontacted:
        df_students = st.session_state.students
        uncontacted_df = df_students[df_students["이름"].isin(uncontacted)]

        st.warning("⚠️ 아래 학생들은 사전 연락 없이 결석 상태입니다. 확인 후 연락을 진행해 주세요.")
        st.table(uncontacted_df[["학번", "이름", "반", "학부모연락처", "비고"]])

        if st.button("✉️ 미연락 학부모 일괄 문자 생성 페이지로 이동"):
            st.session_state.current_page = "✉️ 자동 문자"
            st.rerun()
    else:
        st.success("🎉 오늘 미연락 결석 학생이 없습니다. 모든 학생의 출결이 확인되었습니다!")


# --- [PAGE 5] ✉️ 자동 문자 ---
elif st.session_state.current_page == "✉️ 자동 문자":
    st.title("✉️ 학부모 안내 문자 자동 생성 및 발송")
    st.caption("AI를 이용하거나 템플릿을 선택하여 상황에 맞는 안내 문자를 신속하게 작성합니다.")

    today_key = str(date.today())
    records = st.session_state.attendance_records.get(today_key, {})
    absent_students = [name for name, data in records.items() if data["status"] in ["미락결석", "지각", "병결"]]

    selected_student = st.selectbox("문자 보낼 학생 선택", absent_students if absent_students else st.session_state.students["이름"].tolist())
    
    # 해당 학생 학부모 연락처 찾기
    student_info = st.session_state.students[st.session_state.students["이름"] == selected_student]
    parent_phone = student_info["학부모연락처"].values[0] if not student_info.empty else "연락처 미등록"

    st.write(f"📱 **수신인:** {selected_student} 학생 학부모님 ({parent_phone})")

    mode = st.radio("문자 작성 방식", ["🤖 Gemini AI 자동 생성", "📝 기본 템플릿 사용"])

    sms_content = ""

    if mode == "🤖 Gemini AI 자동 생성":
        st.info("Gemini AI가 상황에 맞춰 친절하고 정중한 안내 문구를 자동으로 작성합니다.")
        reason_input = st.text_input("추가 상황 정보 (선택)", placeholder="예: 아침 9시까지 미입실, 전화 미응답 등")
        
        if st.button("✨ AI 문자 문구 생성"):
            with st.spinner("AI가 문구를 생성 중입니다..."):
                prompt = f"""
                당신은 초/중/고등학교 담임선생님입니다. 
                오늘 학생 '{selected_student}'가 말 없이 등교하지 않았거나 지각했습니다.
                상황 정보: {reason_input if reason_input else '아침 조회 시각까지 미등교 및 연락 없음'}
                학부모님께 보낼 친절하면서도 정중한 안부 및 출결 확인 문자를 200자 이내로 작성해 주세요.
                """
                sms_content = get_gemini_response(prompt)
                st.session_state.generated_sms = sms_content
        
        if "generated_sms" in st.session_state:
            sms_content = st.text_area("생성된 문자 내용 (수정 가능)", value=st.session_state.generated_sms, height=150)

    else:
        template_choice = st.selectbox("템플릿 선택", [
            "미연락 결석 확인 문자",
            "지각 확인 안내 문자",
            "건강상 결석(병결) 안부 문자"
        ])
        
        if template_choice == "미연락 결석 확인 문자":
            sms_content = f"[00학교] 안녕하세요, {selected_student} 보호자님. 오늘 {selected_student} 학생이 아직 등교하지 않아 연락드립니다. 학생의 안전 확인을 위해 확인 후 담임교사에게 연락 부탁드립니다."
        elif template_choice == "지각 확인 안내 문자":
            sms_content = f"[00학교] 안녕하세요, {selected_student} 보호자님. {selected_student} 학생이 오늘 지각 처리되었습니다. 혹시 건강상의 사유가 있다면 편하게 연락 주시기 바랍니다."
        else:
            sms_content = f"[00학교] 안녕하세요, {selected_student} 보호자님. {selected_student} 학생의 쾌유를 바랍니다. 제출하실 증빙 서류는 등교 시 편하게 보내주시면 됩니다."

        sms_content = st.text_area("문자 내용", value=sms_content, height=150)

    if st.button("🚀 문자 발송 (모의 전송)"):
        if sms_content:
            log_activity(f"{selected_student} 학부모에게 문자 발송 완료")
            st.success(f"✅ {selected_student} 학부모님({parent_phone})께 문자가 성공적으로 전송되었습니다!")
            st.balloons()
        else:
            st.warning("문자 내용을 작성해주세요.")
