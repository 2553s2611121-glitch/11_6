import streamlit as st
import pandas as pd
from datetime import datetime, date
import google.generativeai as genai

# -----------------------------------------------------------------------------
# 1. 페이지 설정 및 Custom CSS (첨부 이미지 스타일 반영)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="출결 관리 시스템",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 이미지의 카드 스타일 및 배경 재현
st.markdown("""
    <style>
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* 기능 카드 스타일 */
    .card-box {
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #E2E8F0;
        height: 180px;
    }
    .card-blue { background-color: #EFF6FF; border-top: 4px solid #2563EB; }
    .card-green { background-color: #ECFDF5; border-top: 4px solid #10B981; }
    .card-purple { background-color: #F3E8FF; border-top: 4px solid #9333EA; }
    .card-orange { background-color: #FFF7ED; border-top: 4px solid #F97316; }

    .card-title {
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 8px;
        color: #1E293B;
    }
    .card-desc {
        font-size: 0.88rem;
        color: #64748B;
        min-height: 48px;
    }
    
    /* 최근 기능 및 정보 박스 */
    .info-container {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #E2E8F0;
        min-height: 220px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 세션 상태(Session State) 초기화
# -----------------------------------------------------------------------------
if "students" not in st.session_state:
    st.session_state.students = pd.DataFrame([
        {"학번": 1, "이름": "김민수", "반": "1반", "학부모연락처": "010-1234-5678", "비고": "특이사항 없음"},
        {"학번": 2, "이름": "이서연", "반": "1반", "학부모연락처": "010-2345-6789", "비고": "체육 특기생"},
        {"학번": 3, "이름": "박지훈", "반": "1반", "학부모연락처": "010-3456-7890", "비고": "알레르기 보유"},
        {"학번": 4, "이름": "최유진", "반": "1반", "학부모연락처": "010-4567-8901", "비고": "특이사항 없음"},
        {"학번": 5, "이름": "정현우", "반": "1반", "학부모연락처": "010-5678-9012", "비고": "특이사항 없음"},
    ])

today_str = str(date.today())
if "attendance_records" not in st.session_state:
    st.session_state.attendance_records = {
        today_str: {
            "김민수": {"status": "출석", "reason": ""},
            "이서연": {"status": "미락결석", "reason": "말없이 결석 (확인 필요)"},
            "박지훈": {"status": "지각", "reason": "병원 진료"},
            "최유진": {"status": "출석", "reason": ""},
            "정현우": {"status": "미락결석", "reason": "말없이 결석 (확인 필요)"},
        }
    }

if "recent_activities" not in st.session_state:
    st.session_state.recent_activities = [
        {"time": "오늘 10:24", "title": "오늘 출결 기록", "desc": "오늘의 출석 현황을 확인했습니다."},
        {"time": "어제 16:32", "title": "결석 학생 확인", "desc": "결석한 학생 목록을 확인했습니다."},
        {"time": "어제 14:17", "title": "학부모 문자 발송", "desc": "출결 관련 문자를 발송했습니다."}
    ]

if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 홈"

# -----------------------------------------------------------------------------
# 3. 유틸리티 함수 (활동 기록, Gemini AI, 사용 방법 Dialog)
# -----------------------------------------------------------------------------
def log_activity(title, desc):
    now_str = datetime.now().strftime("%H:%M")
    st.session_state.recent_activities.insert(0, {
        "time": f"오늘 {now_str}", "title": title, "desc": desc
    })
    if len(st.session_state.recent_activities) > 5:
        st.session_state.recent_activities.pop()

def generate_ai_sms(student_name, reason):
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        prompt = f"""
        당신은 초/중/고등학교 담임선생님입니다.
        오늘 학생 '{student_name}'이(가) 연락 없이 결석했거나 지각했습니다.
        상황/사유: {reason if reason else '사전 연락 없음'}
        
        학부모님께 보낼 정중하고 친절한 안부 확인 문자 메시지를 작성해주세요.
        - 공손한 어조
        - 학생의 안전 확인 목적 명시
        - 150자 내외로 작성
        """
        response = model.generate_content(prompt)
        return response.text
    except KeyError:
        return "⚠️ [안내] GEMINI_API_KEY가 설정되지 않았습니다. 기본 템플릿 문구를 활용해 주세요."
    except Exception as e:
        return f"⚠️ [오류] AI 문자 생성 중 문제가 발생했습니다: {str(e)}"

@st.dialog("📖 사용 방법 안내")
def show_guide_dialog(guide_type):
    guides = {
        "리스트": "### 👤 학생 관리 사용 방법\n1. 학생 목록을 확인하거나 새로운 학생을 추가할 수 있습니다.\n2. 학부모 연락처 및 비고 사항을 최신 상태로 유지하세요.",
        "출결 기록": "### 📅 출결 기록 사용 방법\n1. 날짜를 선택한 후 학생별 출석/지각/미락결석/병결 상태를 변경합니다.\n2. 사유를 입력하고 하단의 '저장' 버튼을 클릭하세요.",
        "학부모 연결": "### 👨‍👩‍👧 학부모 연결 사용 방법\n1. 오늘 사전 연락 없이 결석한 학생만 자동으로 분류됩니다.\n2. '문자 생성' 버튼을 클릭하면 해당 학부모에게 발송할 메시지로 이동합니다.",
        "자동 문자": "### ✉️ 자동 문자 사용 방법\n1. 문자를 발송할 학생을 선택합니다.\n2. Gemini AI 자동 생성 기능이나 기본 템플릿을 사용하여 문구를 완성한 뒤 발송합니다."
    }
    st.markdown(guides.get(guide_type, "안내 내용이 없습니다."))

# -----------------------------------------------------------------------------
# 4. 사이드바 네비게이션
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("🛡️ 출결 관리")
    st.caption("선생님 전용 출결 도우미")
    st.divider()

    menu_list = ["🏠 홈", "👤 학생 관리", "📅 출결 기록", "👨‍👩‍👧 학부모 연결", "✉️ 자동 문자"]
    
    # 페이지 변경 함수
    def on_menu_change():
        st.session_state.current_page = st.session_state.selected_menu_radio

    st.radio(
        "메뉴 이동",
        menu_list,
        key="selected_menu_radio",
        index=menu_list.index(st.session_state.current_page),
        on_change=on_menu_change
    )

    st.divider()
    st.caption("❓ 도움이 필요하신가요?")
    st.caption("고객센터: 1588-1234")

# -----------------------------------------------------------------------------
# 5. 메인 화면 (페이지별 구성)
# -----------------------------------------------------------------------------

# --- [PAGE 1] 🏠 홈 ---
if st.session_state.current_page == "🏠 홈":
    st.title("안녕하세요! 👋")
    st.subheader("출결 관리를 더 쉽고 편리하게, 지금 바로 시작해보세요.")

    # 기능 검색창
    search_term = st.text_input("🔍 출결 기능을 검색해 보세요.", placeholder="예: 학생 결석 처리, 지각 수정, 학부모에게 문자 보내기 등")
    
    if search_term:
        st.info(f"🔎 '{search_term}' 검색 관련 매칭 메뉴:")
        if any(keyword in search_term for keyword in ["결석", "문자", "자동", "학부모"]):
            st.write("👉 **[✉️ 자동 문자]** 또는 **[👨‍👩‍👧 학부모 연결]** 메뉴를 활용해보세요.")
        elif any(keyword in search_term for keyword in ["학생", "명단", "리스트"]):
            st.write("👉 **[👤 학생 관리]** 메뉴에서 학생 명단을 수정할 수 있습니다.")
        else:
            st.write("👉 **[📅 출결 기록]** 메뉴에서 일단위 출석/지각 현황을 변경할 수 있습니다.")

    st.write("")

    # 4개 카드 컬럼 (이미지 배치 동일)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="card-box card-blue">
            <div class="card-title">👤 리스트</div>
            <div class="card-desc">학생 명단 및 반/그룹을 관리할 수 있어요.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("바로가기 ➔", key="go_list", use_container_width=True):
            st.session_state.current_page = "👤 학생 관리"
            st.rerun()
        if st.button("🔗 사용 방법 보기", key="guide_list"):
            show_guide_dialog("리스트")

    with col2:
        st.markdown("""
        <div class="card-box card-green">
            <div class="card-title">📅 출결 기록</div>
            <div class="card-desc">출석, 지각, 결석 등 출결 상태를 기록하고 관리해요.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("바로가기 ➔", key="go_record", use_container_width=True):
            st.session_state.current_page = "📅 출결 기록"
            st.rerun()
        if st.button("🔗 사용 방법 보기", key="guide_record"):
            show_guide_dialog("출결 기록")

    with col3:
        st.markdown("""
        <div class="card-box card-purple">
            <div class="card-title">👨‍👩‍👧 학부모 연결</div>
            <div class="card-desc">학부모 연락처를 관리하고 소통할 수 있어요.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("바로가기 ➔", key="go_parent", use_container_width=True):
            st.session_state.current_page = "👨‍👩‍👧 학부모 연결"
            st.rerun()
        if st.button("🔗 사용 방법 보기", key="guide_parent"):
            show_guide_dialog("학부모 연결")

    with col4:
        st.markdown("""
        <div class="card-box card-orange">
            <div class="card-title">✉️ 자동 문자</div>
            <div class="card-desc">출결 상황에 따른 문자 발송 및 예약을 할 수 있어요.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("바로가기 ➔", key="go_sms", use_container_width=True):
            st.session_state.current_page = "✉️ 자동 문자"
            st.rerun()
        if st.button("🔗 사용 방법 보기", key="guide_sms"):
            show_guide_dialog("자동 문자")

    st.write("---")

    # 하단 2열 배치 (최근 사용한 기능 / 사이트 사용 가이드)
    b_col1, b_col2 = st.columns(2)

    with b_col1:
        st.markdown("### 💡 최근 사용한 기능")
        st.markdown('<div class="info-container">', unsafe_allow_html=True)
        for act in st.session_state.recent_activities:
            st.write(f"⏱️ **{act['time']}** | **{act['title']}** - {act['desc']}")
        st.markdown('</div>', unsafe_allow_html=True)

    with b_col2:
        st.markdown("### 📖 사이트 사용 가이드")
        st.markdown('<div class="info-container">', unsafe_allow_html=True)
        if st.button("🔗 리스트 사용 방법 보기 (학생 추가, 반 배정 등)", key="g1"):
            show_guide_dialog("리스트")
        if st.button("🔗 출결 기록 사용 방법 보기 (출석 처리, 통계 등)", key="g2"):
            show_guide_dialog("출결 기록")
        if st.button("🔗 학부모 연결 사용 방법 보기 (연락처 연동 등)", key="g3"):
            show_guide_dialog("학부모 연결")
        if st.button("🔗 자동 문자 사용 방법 보기 (AI 문구 작성, 발송 등)", key="g4"):
            show_guide_dialog("자동 문자")
        st.markdown('</div>', unsafe_allow_html=True)


# --- [PAGE 2] 👤 학생 관리 ---
elif st.session_state.current_page == "👤 학생 관리":
    st.title("👤 학생 명단 관리")
    st.caption("학급 학생 정보 및 학부모 연락처를 관리합니다.")

    tab1, tab2 = st.tabs(["📋 등록된 학생 목록", "➕ 신규 학생 등록"])

    with tab1:
        st.dataframe(st.session_state.students, use_container_width=True)

    with tab2:
        with st.form("add_student_form"):
            s_num = st.number_input("학번", min_value=1, value=len(st.session_state.students)+1)
            s_name = st.text_input("학생 이름")
            s_class = st.text_input("반/그룹", value="1반")
            s_parent_phone = st.text_input("학부모 연락처", placeholder="010-0000-0000")
            s_note = st.text_input("비고 (특이사항)")

            submitted = st.form_submit_button("학생 추가하기")
            if submitted:
                if s_name and s_parent_phone:
                    new_row = {"학번": s_num, "이름": s_name, "반": s_class, "학부모연락처": s_parent_phone, "비고": s_note}
                    st.session_state.students = pd.concat([st.session_state.students, pd.DataFrame([new_row])], ignore_index=True)
                    log_activity("학생 추가 완료", f"신규 학생 {s_name} 등록")
                    st.success(f"✅ {s_name} 학생이 성공적으로 추가되었습니다.")
                    st.rerun()
                else:
                    st.error("학생 이름과 학부모 연락처는 필수 항목입니다.")


# --- [PAGE 3] 📅 출결 기록 ---
elif st.session_state.current_page == "📅 출결 기록":
    st.title("📅 일별 출결 기록")
    
    sel_date = st.date_input("출결 관리 날짜 선택", value=date.today())
    d_key = str(sel_date)

    if d_key not in st.session_state.attendance_records:
        st.session_state.attendance_records[d_key] = {
            row["이름"]: {"status": "출석", "reason": ""} for _, row in st.session_state.students.iterrows()
        }

    st.subheader(f"📌 {d_key} 출결 현황 기록")
    curr_rec = st.session_state.attendance_records[d_key]
    new_rec = {}

    with st.form("att_form"):
        for _, row in st.session_state.students.iterrows():
            st_name = row["이름"]
            prev_val = curr_rec.get(st_name, {"status": "출석", "reason": ""})

            c1, c2, c3 = st.columns([1, 1, 2])
            with c1:
                st.write(f"**{row['학번']}번 {st_name}**")
            with c2:
                status_opt = ["출석", "지각", "미락결석", "병결", "조퇴"]
                idx = status_opt.index(prev_val["status"]) if prev_val["status"] in status_opt else 0
                st_status = st.selectbox(f"상태_{st_name}", status_opt, index=idx, label_visibility="collapsed")
            with c3:
                st_reason = st.text_input(f"사유_{st_name}", value=prev_val["reason"], placeholder="사유 입력", label_visibility="collapsed")

            new_rec[st_name] = {"status": st_status, "reason": st_reason}

        if st.form_submit_button("💾 출결 저장하기"):
            st.session_state.attendance_records[d_key] = new_rec
            log_activity("오늘 출결 기록", f"{d_key} 출결 정보가 저장되었습니다.")
            st.success("출결 정보가 성공적으로 업데이트되었습니다.")


# --- [PAGE 4] 👨‍👩‍👧 학부모 연결 ---
elif st.session_state.current_page == "👨‍👩‍👧 학부모 연결":
    st.title("👨‍👩‍👧 미연락 결석 학생 감지 및 연결")
    st.caption("사전 연락 없이 결석한 학생을 자동 감지합니다.")

    curr_today_key = str(date.today())
    records = st.session_state.attendance_records.get(curr_today_key, {})

    uncontacted_list = [name for name, data in records.items() if data["status"] == "미락결석"]

    st.subheader(f"🚨 오늘({curr_today_key}) 미연락 결석 학생: {len(uncontacted_list)}명")

    if uncontacted_list:
        df_all = st.session_state.students
        uncontacted_df = df_all[df_all["이름"].isin(uncontacted_list)]

        st.warning("⚠️ 미연락 결석 학생입니다. 즉시 학부모님께 연락하여 안전 상태를 확인해주세요.")
        st.dataframe(uncontacted_df[["학번", "이름", "반", "학부모연락처", "비고"]], use_container_width=True)

        if st.button("✉️ 미연락 학생 학부모 문자 작성하러 가기", type="primary"):
            st.session_state.current_page = "✉️ 자동 문자"
            st.rerun()
    else:
        st.success("🎉 오늘 미연락 결석 학생이 없습니다! 모든 학생의 등교 및 사유가 확인되었습니다.")


# --- [PAGE 5] ✉️ 자동 문자 ---
elif st.session_state.current_page == "✉️ 자동 문자":
    st.title("✉️ 학부모 안내 문자 자동 발송")
    st.caption("Gemini AI를 활용해 학부모님께 전달할 안부 및 출결 확인 문구를 작성합니다.")

    curr_today_key = str(date.today())
    records = st.session_state.attendance_records.get(curr_today_key, {})
    
    # 결석/지각 학생 추출
    target_students = [name for name, data in records.items() if data["status"] in ["미락결석", "지각", "병결"]]
    if not target_students:
        target_students = st.session_state.students["이름"].tolist()

    selected_st = st.selectbox("수신 학생 선택", target_students)

    st_info = st.session_state.students[st.session_state.students["이름"] == selected_st]
    p_phone = st_info["학부모연락처"].values[0] if not st_info.empty else "연락처 미등록"

    st.write(f"📱 **수신자 정보**: {selected_st} 학생 학부모님 ({p_phone})")

    mode = st.radio("문자 작성 방식 선택", ["🤖 Gemini AI 자동 생성", "📝 표준 템플릿 선택"])

    sms_text = ""

    if mode == "🤖 Gemini AI 자동 생성":
        extra_reason = st.text_input("추가 상황 메모 (선택)", placeholder="예: 1교시 수업 시작 전 미입실 및 전화 미응답")
        
        if st.button("✨ Gemini AI 문구 작성"):
            with st.spinner("AI가 정중한 문구를 작성하고 있습니다..."):
                sms_text = generate_ai_sms(selected_st, extra_reason)
                st.session_state.generated_text = sms_text

        if "generated_text" in st.session_state:
            sms_text = st.text_area("생성된 문자 내용 (수정 가능)", value=st.session_state.generated_text, height=150)

    else:
        tmpl = st.selectbox("템플릿 선택", [
            "미연락 결석 확인 안내",
            "지각 확인 및 안부 안내",
            "병결 관련 서류 안내"
        ])
        
        if tmpl == "미연락 결석 확인 안내":
            sms_text = f"[학교 안내] 안녕하세요, {selected_st} 보호자님. 오늘 {selected_st} 학생이 사전 연락 없이 등교하지 않아 확인차 연락드립니다. 확인 후 담임교사에게 연락 부탁드립니다."
        elif tmpl == "지각 확인 및 안부 안내":
            sms_text = f"[학교 안내] 안녕하세요, {selected_st} 보호자님. 오늘 {selected_st} 학생이 지각 처리되었습니다. 혹시 신체적 불편함이나 사유가 있으시다면 편하게 말씀 부탁드립니다."
        else:
            sms_text = f"[학교 안내] 안녕하세요, {selected_st} 보호자님. {selected_st} 학생의 빠른 쾌유를 바랍니다. 결석 계원 서류는 등교 시 편하게 전달해주시면 됩니다."

        sms_text = st.text_area("문자 내용", value=sms_text, height=150)

    if st.button("🚀 문자 발송하기 (모의 전송)", type="primary"):
        if sms_text:
            log_activity("학부모 문자 발송", f"{selected_st} 학생 학부모님께 문자 발송 완료")
            st.success(f"✅ {selected_st} 학생 학부모님({p_phone})께 문자가 성공적으로 전송되었습니다.")
            st.balloons()
        else:
            st.warning("발송할 문자 내용을 작성해 주세요.")
