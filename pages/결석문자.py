import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import time

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정 및 상태 초기화
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="출결 자동 확인 & 무단결과 처리 시스템",
    page_icon="🔔",
    layout="wide"
)

# 기본 모의 학생 데이터 설정
if "students" not in st.session_state:
    st.session_state.students = pd.DataFrame([
        {
            "id": 10101,
            "name": "김철수",
            "phone": "010-1234-5678",
            "status": "미출석",
            "sent_time": None,
            "deadline": None,
            "reason": None,
            "is_unexcused": False
        },
        {
            "id": 10102,
            "name": "이영희",
            "phone": "010-8765-4321",
            "status": "출석",
            "sent_time": None,
            "deadline": None,
            "reason": None,
            "is_unexcused": False
        },
        {
            "id": 10103,
            "name": "박민수",
            "phone": "010-5555-7777",
            "status": "미출석",
            "sent_time": None,
            "deadline": None,
            "reason": None,
            "is_unexcused": False
        }
    ])

# -----------------------------------------------------------------------------
# 2. 사이드바 - 설정 및 단체 발송 Control
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ 발송 & 타이머 설정")
    
    time_limit_minutes = st.number_input(
        "응답 제한 시간(분)",
        min_value=1,
        max_value=60,
        value=20,
        help="문자 발송 후 이 시간이 지나면 무단결과로 처리됩니다."
    )
    
    st.subheader("📲 SMS 발송 설정")
    use_mock = st.toggle("시뮬레이션 모드 (실제 SMS 미발송)", value=True)
    
    if not use_mock:
        st.caption("Twilio 계정 정보를 입력하세요.")
        account_sid = st.text_input("Account SID", type="password")
        auth_token = st.text_input("Auth Token", type="password")
        from_phone = st.text_input("발신 번호")

    st.divider()
    st.subheader("🚀 일괄 문자 발송")
    if st.button("미출석자 전체에게 문자 발송", use_container_width=True, type="primary"):
        now = datetime.now()
        deadline = now + timedelta(minutes=time_limit_minutes)
        
        updated_count = 0
        for idx, row in st.session_state.students.iterrows():
            if row["status"] == "미출석" and row["sent_time"] is None:
                st.session_state.students.at[idx, "sent_time"] = now.strftime("%H:%M:%S")
                st.session_state.students.at[idx, "deadline"] = deadline
                updated_count += 1
                
                # Twilio SMS 발송 로직 (실제 모드일 때)
                if not use_mock and account_sid and auth_token and from_phone:
                    try:
                        from twilio.rest import Client
                        client = Client(account_sid, auth_token)
                        client.messages.create(
                            body=f"[출결확인] {row['name']}학생, 결석 사유를 20분 내로 답장해주세요. 미답장 시 무단결과 처리됩니다.",
                            from_=from_phone,
                            to=row['phone']
                        )
                    except Exception as e:
                        st.error(f"{row['name']} SMS 발송 실패: {str(e)}")
                        
        if updated_count > 0:
            st.success(f"미출석 학생 {updated_count}명에게 문자를 발송했습니다.")
            st.rerun()
        else:
            st.info("문자를 보낼 미출석 학생이 없습니다.")

# -----------------------------------------------------------------------------
# 3. 타이머 자동 갱신 및 무단결과 자동 판정 로직
# -----------------------------------------------------------------------------
now_dt = datetime.now()

for idx, row in st.session_state.students.iterrows():
    # 문자를 보냈고, 아직 사유를 안 적었고, 이미 무단결과가 아닌 학생 체크
    if row["sent_time"] is not None and (pd.isna(row["reason"]) or not row["reason"]) and not row["is_unexcused"]:
        if row["deadline"] is not None and now_dt > row["deadline"]:
            st.session_state.students.at[idx, "status"] = "무단결과"
            st.session_state.students.at[idx, "is_unexcused"] = True

# -----------------------------------------------------------------------------
# 4. 메인 화면
# -----------------------------------------------------------------------------
st.title("🔔 미출결 학생 자동 확인 및 무단결과 관리")
st.caption("등교시간 내 미출석 학생에게 결석 사유를 요청하고, 20분 초과 시 무단결과로 자동 전환합니다.")

# 현황 요약
col1, col2, col3, col4 = st.columns(4)
total_s = len(st.session_state.students)
attended_s = len(st.session_state.students[st.session_state.students["status"] == "출석"])
waiting_s = len(st.session_state.students[(st.session_state.students["status"] == "미출석") & (st.session_state.students["sent_time"].notnull())])
unexcused_s = len(st.session_state.students[st.session_state.students["status"] == "무단결과"])

col1.metric("전체 학생", f"{total_s}명")
col2.metric("정상 출석", f"{attended_s}명")
col3.metric("사유 대기 중", f"{waiting_s}명")
col4.metric("🚨 무단결과", f"{unexcused_s}명")

st.divider()

# 메인 탭 구획
tab1, tab2, tab3 = st.tabs(["📋 실시간 모니터링 & 답장 입력", "📊 통계 현황", "➕ 학생 추가"])

with tab1:
    st.subheader("실시간 출결 모니터링")
    
    # 표에 보여줄 데이터 정제
    display_df = st.session_state.students.copy()
    
    # 남은 시간 계산
    remaining_times = []
    for idx, row in display_df.iterrows():
        if row["sent_time"] is not None and not row["is_unexcused"] and (pd.isna(row["reason"]) or not row["reason"]):
            rem = row["deadline"] - datetime.now()
            seconds = rem.total_seconds()
            if seconds > 0:
                mins, secs = divmod(int(seconds), 60)
                remaining_times.append(f"{mins}분 {secs}초")
            else:
                remaining_times.append("시간 초과")
        elif row["is_unexcused"]:
            remaining_times.append("무단결과 처리됨")
        elif row["reason"]:
            remaining_times.append("답장 완료")
        else:
            remaining_times.append("문자 미발송")
            
    display_df["남은 시간"] = remaining_times
    
    st.dataframe(
        display_df[["id", "name", "phone", "status", "sent_time", "남은 시간", "reason"]],
        column_config={
            "id": "학번",
            "name": "이름",
            "phone": "연락처",
            "status": "현재 상태",
            "sent_time": "문자 발송 시각",
            "남은 시간": "20분 타이머",
            "reason": "입력된 결석 사유"
        },
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()
    st.subheader("📱 결석 사유 수신 (답장 시뮬레이션)")
    st.caption("학생이 답장 문자를 보내오면 교사가 직접 등록하거나 테스트할 수 있습니다.")
    
    col_sel, col_input, col_btn = st.columns([2, 3, 1])
    
    unanswered_students = st.session_state.students[
        (st.session_state.students["sent_time"].notnull()) & 
        (st.session_state.students["reason"].isna() | (st.session_state.students["reason"] == ""))
    ]
    
    if not unanswered_students.empty:
        student_choice = col_sel.selectbox(
            "학생 선택", 
            options=unanswered_students["id"].tolist(),
            format_func=lambda x: f"{x} {unanswered_students[unanswered_students['id']==x]['name'].values[0]}"
        )
        reason_text = col_input.text_input("수신된 결석 사유", placeholder="예: 병원 진료 후 2교시 등교 예정")
        
        if col_btn.button("사유 등록", use_container_width=True):
            if reason_text.strip():
                s_idx = st.session_state.students[st.session_state.students["id"] == student_choice].index[0]
                st.session_state.students.at[s_idx, "reason"] = reason_text
                st.session_state.students.at[s_idx, "status"] = "사유제출(인정)"
                st.success("결석 사유가 정상 등록되었습니다.")
                st.rerun()
            else:
                st.warning("사유를 입력해주세요.")
    else:
        st.info("현재 사유 입력 대기 중인 학생이 없습니다.")

with tab2:
    st.subheader("출결 상태 비율")
    status_counts = st.session_state.students["status"].value_counts().reset_index()
    status_counts.columns = ["상태", "인원수"]
    
    fig = px.pie(
        status_counts, 
        names="상태", 
        values="인원수", 
        color="상태",
        color_discrete_map={
            "출석": "#2ECC71",
            "미출석": "#F39C12",
            "사유제출(인정)": "#3498DB",
            "무단결과": "#E74C3C"
        }
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("새 학생 등록")
    with st.form("add_student"):
        new_id = st.number_input("학번", min_value=10000, max_value=99999, value=10104)
        new_name = st.text_input("이름")
        new_phone = st.text_input("연락처", value="010-0000-0000")
        submitted = st.form_submit_button("학생 추가")
        
        if submitted:
            if new_name:
                new_row = pd.DataFrame([{
                    "id": new_id,
                    "name": new_name,
                    "phone": new_phone,
                    "status": "미출석",
                    "sent_time": None,
                    "deadline": None,
                    "reason": None,
                    "is_unexcused": False
                }])
                st.session_state.students = pd.concat([st.session_state.students, new_row], ignore_index=True)
                st.success(f"{new_name} 학생이 추가되었습니다.")
                st.rerun()
