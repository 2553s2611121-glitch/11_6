import time
import pandas as pd
import streamlit as st

# ==========================================
# 1. 페이지 기본 설정 및 세션 초기화
# ==========================================
st.set_page_config(
    page_title="학생 결석 사유 관리 System",
    page_icon="🏫",
    layout="wide",
)

# 기본 학생 데이터 초기화
if "students" not in st.session_state:
    st.session_state.students = [
        {
            "id": "10101",
            "name": "김철수",
            "phone": "010-1234-5678",
            "status": "미응답",
            "sent_time": None,
            "reason": "",
        },
        {
            "id": "10102",
            "name": "이영희",
            "phone": "010-8765-4321",
            "status": "미응답",
            "sent_time": None,
            "reason": "",
        },
        {
            "id": "10103",
            "name": "박민수",
            "phone": "010-5555-7777",
            "status": "미응답",
            "sent_time": None,
            "reason": "",
        },
    ]


# 20분(1200초) 초과 시 무단결과 처리
def update_statuses():
    current_time = time.time()
    for student in st.session_state.students:
        if student["status"] == "문자발송 완료" and student["sent_time"] is not None:
            elapsed = current_time - student["sent_time"]
            if elapsed >= 1200:  # 20분 초과
                student["status"] = "무단결과"


# 상태 체크
update_statuses()

# ==========================================
# 2. 메인 화면 타이틀 및 사이드바
# ==========================================
st.title("🏫 미통보 결석 학생 사유 확인 시스템")
st.caption("안내 문자 발송 후 **20분 이내**에 결석 사유를 제출하지 않으면 자동으로 **무단결과** 처리됩니다.")
st.markdown("---")

# 사이드바: 신규 학생 등록 및 실시간 타이머 토글
with st.sidebar:
    st.header("➕ 결석 학생 등록")
    with st.form("add_student_form", clear_on_submit=True):
        input_id = st.text_input("학번", placeholder="예: 10104")
        input_name = st.text_input("이름", placeholder="예: 홍길동")
        input_phone = st.text_input("연락처", placeholder="010-0000-0000")
        submit_add = st.form_submit_button("학생 추가", use_container_width=True)

        if submit_add:
            if input_id and input_name and input_phone:
                st.session_state.students.append(
                    {
                        "id": input_id,
                        "name": input_name,
                        "phone": input_phone,
                        "status": "미응답",
                        "sent_time": None,
                        "reason": "",
                    }
                )
                st.success(f"{input_name} 학생이 추가되었습니다.")
                st.rerun()
            else:
                st.error("학번, 이름, 연락처를 모두 입력해주세요.")

    st.markdown("---")
    st.header("⏱️ 타이머 설정")
    auto_refresh = st.checkbox("타이머 실시간 1초 자동 갱신", value=True)
    if st.button("🔄 수동 새로고침", use_container_width=True):
        st.rerun()

# ==========================================
# 3. 메인 탭 구성
# ==========================================
tab_teacher, tab_student = st.tabs(["📱 교사용 - 학생별 타이머 관리", "📩 학생용 - 사유 제출 페이지"])

# ------------------------------------------
# TAB 1: 교사용 화면 (개별 타이머 포함)
# ------------------------------------------
with tab_teacher:
    st.subheader("📋 결석 학생 명단 및 개별 타이머")

    if not st.session_state.students:
        st.info("현재 등록된 결석 학생이 없습니다.")
    else:
        # 요약 메트릭
        total_cnt = len(st.session_state.students)
        pending_cnt = sum(1 for s in st.session_state.students if s["status"] == "문자발송 완료")
        done_cnt = sum(1 for s in st.session_state.students if s["status"] == "사유제출 완료")
        absent_cnt = sum(1 for s in st.session_state.students if s["status"] == "무단결과")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("총 결석 인원", f"{total_cnt}명")
        m2.metric("답변 대기 (20분)", f"{pending_cnt}명")
        m3.metric("사유 제출 완료", f"{done_cnt}명")
        m4.metric("🚨 무단결과 처리", f"{absent_cnt}명")

        st.markdown("---")

        # 학생별 카드가 들어갈 컨테이너 생성
        student_list_container = st.container()

        with student_list_container:
            for idx, student in enumerate(st.session_state.students):
                col_info, col_timer, col_action, col_delete = st.columns([2.5, 3.5, 2, 1])

                # 1. 학생 기본 정보
                col_info.markdown(f"### {student['name']}\n`{student['id']}` | 📱 `{student['phone']}`")

                # 2. 학생 칸마다 개별 타이머 및 상태 표시
                if student["status"] == "미응답":
                    col_timer.info("⚪ **문자 미발송**\n\n문자 발송 시 20분 타이머가 시작됩니다.")
                
                elif student["status"] == "문자발송 완료":
                    elapsed = int(time.time() - student["sent_time"])
                    remain = max(0, 1200 - elapsed)
                    min_left = remain // 60
                    sec_left = remain % 60
                    
                    # 프로그레스 바 비율 계산 (1200초 기준)
                    progress_val = min(1.0, max(0.0, remain / 1200))
                    
                    if remain > 0:
                        col_timer.warning(
                            f"⏳ **답변 대기 중 (남은 시간)**\n\n"
                            f"### ⏱️ `{min_left:02d}분 {sec_left:02d}초`"
                        )
                        col_timer.progress(progress_val)
                    else:
                        col_timer.error("🚨 **20분 초과: 무단결과 전환 중...**")
                
                elif student["status"] == "사유제출 완료":
                    col_timer.success(f"✅ **사유 제출 완료**\n\n**사유:** {student['reason']}")
                
                elif student["status"] == "무단결과":
                    col_timer.error("🚨 **무단결과 처리됨**\n\n20분 동안 사유를 제출하지 않았습니다.")

                # 3. 행동 버튼
                if student["status"] == "미응답":
                    if col_action.button("📱 문자 발송", key=f"send_btn_{idx}", use_container_width=True):
                        student["status"] = "문자발송 완료"
                        student["sent_time"] = time.time()
                        st.toast(f"{student['name']} 학생에게 문자를 보냈습니다.")
                        st.rerun()
                else:
                    if student["sent_time"]:
                        formatted_time = time.strftime("%H:%M:%S", time.localtime(student["sent_time"]))
                        col_action.caption(f"발송시각:\n{formatted_time}")

                # 4. 삭제 버튼
                if col_delete.button("🗑️", key=f"del_btn_{idx}"):
                    st.session_state.students.pop(idx)
                    st.rerun()

                st.divider()

        # CSV 다운로드 기능
        df = pd.DataFrame(st.session_state.students)
        if not df.empty:
            df_export = df[["id", "name", "phone", "status", "reason"]].copy()
            df_export.columns = ["학번", "이름", "연락처", "처리상태", "결석사유"]
            csv_data = df_export.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="📥 출석 결과 CSV 다운로드",
                data=csv_data,
                file_name="결석_사유_확인_결과.csv",
                mime="text/csv",
            )

# ------------------------------------------
# TAB 2: 학생용 사유 제출 화면
# ------------------------------------------
with tab_student:
    st.subheader("📩 학생용 결석 사유 제출")

    waiting_list = [s for s in st.session_state.students if s["status"] == "문자발송 완료"]

    if not waiting_list:
        st.info("현재 결석 사유를 제출할 대기 학생이 없습니다. (교사용 탭에서 문자를 먼저 발송해 주세요.)")
    else:
        student_options = [f"{s['id']} {s['name']} ({s['phone']})" for s in waiting_list]
        selected_option = st.selectbox("학생 선택", student_options)

        if selected_option:
            selected_id = selected_option.split()[0]
            curr_student = next(s for s in st.session_state.students if s["id"] == selected_id)

            elapsed = int(time.time() - curr_student["sent_time"])
            remain = max(0, 1200 - elapsed)

            if remain <= 0:
                st.error("⚠️ 제출 가능 시간(20분)이 지나 무단결과 처리되었습니다. 담임교사에게 문의해 주세요.")
            else:
                st.warning(
                    f"⏰ 제출 남은 시간: **{remain // 60}분 {remain % 60}초** (시간 초과 시 자동으로 무단결과 처리됨)"
                )
                st.progress(remain / 1200)

                with st.form("student_reason_form"):
                    user_reason = st.text_area(
                        "결석 사유를 입력하세요",
                        placeholder="예: 독감 증세로 병원 진료 후 등교 예정입니다.",
                    )
                    submit_reason = st.form_submit_button("사유 제출하기", use_container_width=True)

                    if submit_reason:
                        if user_reason.strip():
                            curr_student["status"] = "사유제출 완료"
                            curr_student["reason"] = user_reason.strip()
                            st.success("결석 사유가 제출되었습니다.")
                            st.rerun()
                        else:
                            st.error("사유를 입력해 주세요.")

# ==========================================
# 4. 1초 자동 새로고침 (타이머 실시간 작동)
# ==========================================
if auto_refresh and any(s["status"] == "문자발송 완료" for s in st.session_state.students):
    time.sleep(1)
    st.rerun()
