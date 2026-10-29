import time
import pandas as pd
import streamlit as st

# ==========================================
# 1. 페이지 기본 설정 및 디자인 테마 적용
# ==========================================
st.set_page_config(
    page_title="스마트 결석 사유 확인 & 무단결석 관리 시스템",
    page_icon="🏫",
    layout="wide",
)

# Custom CSS로 세련된 커스텀 UI/UX 디자인 적용
st.markdown(
    """
    <style>
    /* 메인 카드 스타일 */
    .student-card {
        background-color: #1e222d;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #2e3545;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    /* 타이머 박스 강조 */
    .timer-badge {
        font-family: 'Courier New', Courier, monospace;
        background-color: #2b1f0d;
        color: #ffaa00;
        padding: 8px 12px;
        border-radius: 8px;
        border: 1px solid #664400;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    /* 무단결석 경고 박스 */
    .absent-badge {
        background-color: #3d1418;
        color: #ff4d4d;
        padding: 8px 12px;
        border-radius: 8px;
        border: 1px solid #801a24;
        font-weight: bold;
    }
    
    /* 성공 박스 */
    .success-badge {
        background-color: #0d331e;
        color: #00e676;
        padding: 8px 12px;
        border-radius: 8px;
        border: 1px solid #006633;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_gradient=True,
)

# 세션 데이터 초기화
if "students" not in st.session_state:
    st.session_state.students = [
        {
            "id": "10101",
            "name": "김철수",
            "phone": "010-1234-5678",
            "parent_phone": "010-1111-2222",
            "status": "미응답",
            "student_sent_time": None,
            "parent_sent_time": None,
            "reason": "",
            "submitted_by": "",
        },
        {
            "id": "10102",
            "name": "이영희",
            "phone": "010-8765-4321",
            "parent_phone": "010-3333-4444",
            "status": "미응답",
            "student_sent_time": None,
            "parent_sent_time": None,
            "reason": "",
            "submitted_by": "",
        },
    ]


# 20분(1200초) 카운트다운 및 자동 무단결석 처리
def update_statuses():
    current_time = time.time()
    for student in st.session_state.students:
        # 사유가 아직 안 나왔고, 문자가 하나라도 발송된 경우
        if student["status"] in ["문자발송 완료", "학생발송 완료", "학부모발송 완료"]:
            # 최초 발송 시점 기준으로 20분 판정
            times = [t for t in [student["student_sent_time"], student["parent_sent_time"]] if t is not None]
            if times:
                first_sent_time = min(times)
                if current_time - first_sent_time >= 1200:  # 20분 초과 시 무단결석
                    student["status"] = "무단결석"


# 자동 업데이트
update_statuses()

# ==========================================
# 2. 대시보드 헤더 & 사이드바
# ==========================================
st.title("🏫 스마트 결석 사유 확인 & 무단결석 처리 시스템")
st.caption("학생/학부모 개별 문자 발송 | **20분 미응답 시 자동 무단결석 처리** | 스마트 실시간 모니터링")
st.markdown("---")

# 사이드바
with st.sidebar:
    st.header("➕ 신규 결석 학생 추가")
    with st.form("add_student_form", clear_on_submit=True):
        input_id = st.text_input("학번", placeholder="예: 10103")
        input_name = st.text_input("학생 이름", placeholder="예: 박민수")
        input_phone = st.text_input("학생 연락처", placeholder="010-0000-0000")
        input_parent_phone = st.text_input("학부모 연락처", placeholder="010-0000-0000")
        submit_add = st.form_submit_button("학생 추가하기", use_container_width=True)

        if submit_add:
            if input_id and input_name and (input_phone or input_parent_phone):
                st.session_state.students.append(
                    {
                        "id": input_id,
                        "name": input_name,
                        "phone": input_phone,
                        "parent_phone": input_parent_phone,
                        "status": "미응답",
                        "student_sent_time": None,
                        "parent_sent_time": None,
                        "reason": "",
                        "submitted_by": "",
                    }
                )
                st.success(f"✨ {input_name} 학생이 등록되었습니다.")
                st.rerun()
            else:
                st.error("학번, 이름 및 연락처를 최소 하나 이상 입력해 주세요.")

    st.markdown("---")
    st.header("⚙️ 모니터링 설정")
    auto_refresh = st.checkbox("1초 실시간 타이머 갱신", value=True)
    if st.button("🔄 즉시 새로고침", use_container_width=True):
        st.rerun()

# ==========================================
# 3. 메인 탭 화면
# ==========================================
tab_teacher, tab_submit = st.tabs(["📱 교사용 대시보드 (발송 & 타이머)", "📩 수신자용 결석 사유 제출"])

# ------------------------------------------
# TAB 1: 교사용 대시보드
# ------------------------------------------
with tab_teacher:
    if not st.session_state.students:
        st.info("현재 등록된 결석 학생이 없습니다.")
    else:
        # 요약 메트릭
        total_cnt = len(st.session_state.students)
        pending_cnt = sum(
            1 for s in st.session_state.students if s["status"] in ["문자발송 완료", "학생발송 완료", "학부모발송 완료"]
        )
        done_cnt = sum(1 for s in st.session_state.students if s["status"] == "사유제출 완료")
        absent_cnt = sum(1 for s in st.session_state.students if s["status"] == "무단결석")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("총 결석 대상", f"{total_cnt} 명")
        col2.metric("⏳ 답변 대기중 (20분)", f"{pending_cnt} 명")
        col3.metric("✅ 사유 제출 완료", f"{done_cnt} 명")
        col4.metric("🚨 무단결석 처리", f"{absent_cnt} 명")

        st.markdown("---")

        # 개별 카드 목록
        for idx, student in enumerate(st.session_state.students):
            st.markdown('<div class="student-card">', unsafe_allow_html=True)
            col_info, col_timer, col_send, col_del = st.columns([2.5, 3.5, 2.8, 0.7])

            # 1. 학생 기본 정보
            col_info.markdown(
                f"### 👤 {student['name']} (`{student['id']}`)\n\n"
                f"📱 **학생:** `{student['phone'] or '미등록'}`\n\n"
                f"👨‍👩‍👧 **부모님:** `{student['parent_phone'] or '미등록'}`"
            )

            # 2. 타이머 & 상태 표시
            if student["status"] == "미응답":
                col_timer.info("⚪ **문자 미발송**\n\n학생 또는 부모님에게 문자를 발송해 주세요.")

            elif student["status"] in ["문자발송 완료", "학생발송 완료", "학부모발송 완료"]:
                times = [t for t in [student["student_sent_time"], student["parent_sent_time"]] if t is not None]
                first_sent = min(times)
                elapsed = int(time.time() - first_sent)
                remain = max(0, 1200 - elapsed)
                min_left, sec_left = remain // 60, remain % 60
                progress_val = min(1.0, max(0.0, remain / 1200))

                if remain > 0:
                    col_timer.markdown(
                        f"⏳ **제한시간 카운트다운**\n\n"
                        f"<div class='timer-badge'>⏱️ {min_left:02d}분 {sec_left:02d}초 남음</div>",
                        unsafe_allow_html=True,
                    )
                    col_timer.progress(progress_val)
                else:
                    col_timer.markdown("<div class='absent-badge'>🚨 무단결석 처리 진행 중</div>", unsafe_allow_html=True)

            elif student["status"] == "사유제출 완료":
                col_timer.markdown(
                    f"<div class='success-badge'>✅ 사유 제출 완료 ({student['submitted_by']})</div>\n\n"
                    f"**제출된 사유:** {student['reason']}",
                    unsafe_allow_html=True,
                )

            elif student["status"] == "무단결석":
                col_timer.markdown(
                    "<div class='absent-badge'>🚨 무단결석 확정</div>\n\n20분 동안 결석 사유가 제출되지 않았습니다.",
                    unsafe_allow_html=True,
                )

            # 3. 학생/부모님 각각 독립 문자 발송 버튼
            if student["status"] != "사유제출 완료":
                col_send.write("**📱 문자 발송 관리**")

                # 학생 발송 버튼
                st_sent = student["student_sent_time"] is not None
                btn_st_label = "✅ 학생 발송 완료" if st_sent else "📱 학생에게 문자 발송"
                if col_send.button(btn_st_label, key=f"btn_st_{idx}", disabled=st_sent, use_container_width=True):
                    student["student_sent_time"] = time.time()
                    if student["status"] == "미응답":
                        student["status"] = "학생발송 완료"
                    st.toast(f"{student['name']} 학생에게 문자를 발송했습니다.")
                    st.rerun()

                # 부모님 발송 버튼 (학생 발송 후에도 언제든 가능)
                pr_sent = student["parent_sent_time"] is not None
                btn_pr_label = "✅ 부모님 발송 완료" if pr_sent else "👨‍👩‍👧 부모님에게 문자 발송"
                if col_send.button(btn_pr_label, key=f"btn_pr_{idx}", disabled=pr_sent, use_container_width=True):
                    student["parent_sent_time"] = time.time()
                    if student["status"] == "미응답":
                        student["status"] = "학부모발송 완료"
                    st.toast(f"{student['name']} 학생 부모님에게 문자를 발송했습니다.")
                    st.rerun()
            else:
                col_send.write("---")
                col_send.caption("제출 완료로 문자 발송 마감")

            # 4. 삭제 버튼
            if col_del.button("🗑️", key=f"del_btn_{idx}"):
                st.session_state.students.pop(idx)
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

        # CSV 다운로드 버튼
        df = pd.DataFrame(st.session_state.students)
        if not df.empty:
            df_export = df[["id", "name", "phone", "parent_phone", "status", "submitted_by", "reason"]].copy()
            df_export.columns = ["학번", "이름", "학생연락처", "학부모연락처", "최종상태", "제출자", "결석사유"]
            csv_data = df_export.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="📥 출석부 확인 결과 CSV 다운로드",
                data=csv_data,
                file_name="결석사유_확인결과.csv",
                mime="text/csv",
            )

# ------------------------------------------
# TAB 2: 수신자용 결석 사유 제출
# ------------------------------------------
with tab_submit:
    st.subheader("📩 결석 사유 제출 페이지 (학생 / 학부모 시뮬레이션)")

    waiting_list = [
        s
        for s in st.session_state.students
        if s["status"] in ["문자발송 완료", "학생발송 완료", "학부모발송 완료", "무단결석"]
    ]

    if not waiting_list:
        st.info("현재 사유를 제출할 수 있는 대상이 없습니다. 교사용 대시보드에서 문자를 발송해 주세요.")
    else:
        student_options = [f"{s['id']} {s['name']}" for s in waiting_list]
        selected_option = st.selectbox("제출 대상 학생 선택", student_options)

        if selected_option:
            selected_id = selected_option.split()[0]
            curr_student = next(s for s in st.session_state.students if s["id"] == selected_id)

            times = [t for t in [curr_student["student_sent_time"], curr_student["parent_sent_time"]] if t is not None]
            first_sent = min(times)
            elapsed = int(time.time() - first_sent)
            remain = max(0, 1200 - elapsed)

            if remain <= 0 or curr_student["status"] == "무단결석":
                st.error("🚨 **제출 가능 시간(20분)이 초과되어 무단결석 처리되었습니다.** 담임 선생님에게 직접 문의해 주세요.")
            else:
                st.warning(f"⏰ 제출 마감까지 **{remain // 60}분 {remain % 60}초** 남았습니다. 시간 초과 시 **무단결석** 처리됩니다.")
                st.progress(remain / 1200)

                with st.form("submit_reason_form"):
                    submitter = st.radio("제출자 선택", ["학생 본인", "학부모님"], horizontal=True)
                    reason_text = st.text_area(
                        "결석 사유 작성",
                        placeholder="예: 독감 증상으로 인하여 병원 진료 후 등교 예정입니다.",
                    )
                    submit_btn = st.form_submit_button("결석 사유 제출하기", use_container_width=True)

                    if submit_btn:
                        if reason_text.strip():
                            curr_student["status"] = "사유제출 완료"
                            curr_student["reason"] = reason_text.strip()
                            curr_student["submitted_by"] = submitter
                            st.success(f"[{submitter}] 결석 사유가 정상적으로 제출되었습니다.")
                            st.rerun()
                        else:
                            st.error("사유를 작성해 주세요.")

# ==========================================
# 4. 실시간 타이머 리런
# ==========================================
if auto_refresh and any(
    s["status"] in ["문자발송 완료", "학생발송 완료", "학부모발송 완료"] for s in st.session_state.students
):
    time.sleep(1)
    st.rerun()
