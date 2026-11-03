import time
import pandas as pd
import streamlit as st

# ==========================================
# 1. 페이지 기본 설정 및 세션 초기화
# ==========================================
st.set_page_config(
    page_title="단계별 결석 사유 관리 System",
    page_icon="🏫",
    layout="wide",
)

# 기본 학생 데이터 구조
if "students" not in st.session_state:
    st.session_state.students = [
        {
            "id": "10101",
            "name": "김철수",
            "phone": "010-1234-5678",
            "parent_phone": "010-1111-2222",
            "status": "미응답",  # 미응답, 학생대기중, 학부모대기중, 사유제출 완료, 무단결과
            "stu_sent_time": None,
            "par_sent_time": None,
            "reason": "",
            "submitted_by": "",
        },
        {
            "id": "10102",
            "name": "이영희",
            "phone": "010-8765-4321",
            "parent_phone": "010-3333-4444",
            "status": "미응답",
            "stu_sent_time": None,
            "par_sent_time": None,
            "reason": "",
            "submitted_by": "",
        },
    ]


# 자동 상태 업데이트 함수 (20분 타이머 체크)
def update_statuses():
    current_time = time.time()
    for student in st.session_state.students:
        # 학부모에게 문자를 보낸 후 20분이 지난 경우 -> 무단결과 처리
        if student["status"] == "학부모대기중" and student["par_sent_time"] is not None:
            if current_time - student["par_sent_time"] >= 1200:  # 20분 (1200초)
                student["status"] = "무단결과"


update_statuses()

# ==========================================
# 2. 메인 화면 타이틀 및 사이드바
# ==========================================
st.title("🏫 단계별 학생/학부모 결석 사유 확인 시스템")
st.caption(
    "1차로 학생에게 문자를 보낸 후, 미응답 시 학부모에게 2차 문자를 발송할 수 있습니다. **학부모 문자 발송 후 20분 동안 미응답 시 최종 무단결과** 처리됩니다."
)
st.markdown("---")

# 사이드바: 신규 학생 등록 및 타이머 설정
with st.sidebar:
    st.header("➕ 결석 학생/학부모 등록")
    with st.form("add_student_form", clear_on_submit=True):
        input_id = st.text_input("학번", placeholder="예: 10103")
        input_name = st.text_input("학생 이름", placeholder="예: 박민수")
        input_phone = st.text_input("학생 연락처", placeholder="010-0000-0000")
        input_parent_phone = st.text_input("학부모 연락처", placeholder="010-0000-0000")
        submit_add = st.form_submit_button("등록하기", use_container_width=True)

        if submit_add:
            if input_id and input_name and input_phone and input_parent_phone:
                st.session_state.students.append(
                    {
                        "id": input_id,
                        "name": input_name,
                        "phone": input_phone,
                        "parent_phone": input_parent_phone,
                        "status": "미응답",
                        "stu_sent_time": None,
                        "par_sent_time": None,
                        "reason": "",
                        "submitted_by": "",
                    }
                )
                st.success(f"{input_name} 학생 정보가 추가되었습니다.")
                st.rerun()
            else:
                st.error("학번, 이름, 학생/학부모 연락처를 모두 입력해 주세요.")

    st.markdown("---")
    st.header("⏱️ 타이머 설정")
    auto_refresh = st.checkbox("1초 자동 화면 갱신", value=True)
    if st.button("🔄 수동 새로고침", use_container_width=True):
        st.rerun()

# ==========================================
# 3. 메인 탭 구성
# ==========================================
tab_teacher, tab_submit = st.tabs(["📱 교사용 - 단계별 발송 관리", "📩 학생·학부모용 - 사유 제출"])

# ------------------------------------------
# TAB 1: 교사용 화면
# ------------------------------------------
with tab_teacher:
    st.subheader("📋 학생 1차 & 학부모 2차 발송 및 타이머")

    if not st.session_state.students:
        st.info("현재 등록된 결석 학생이 없습니다.")
    else:
        # 요약 지표
        total_cnt = len(st.session_state.students)
        stu_wait_cnt = sum(1 for s in st.session_state.students if s["status"] == "학생대기중")
        par_wait_cnt = sum(1 for s in st.session_state.students if s["status"] == "학부모대기중")
        done_cnt = sum(1 for s in st.session_state.students if s["status"] == "사유제출 완료")
        absent_cnt = sum(1 for s in st.session_state.students if s["status"] == "무단결과")

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("총 결석 인원", f"{total_cnt}명")
        m2.metric("학생 답변대기", f"{stu_wait_cnt}명")
        m3.metric("학부모 답변대기", f"{par_wait_cnt}명")
        m4.metric("사유제출 완료", f"{done_cnt}명")
        m5.metric("🚨 무단결과", f"{absent_cnt}명")

        st.markdown("---")

        # 학생별 카드리스트
        for idx, student in enumerate(st.session_state.students):
            col_info, col_status, col_action, col_delete = st.columns([2.5, 3.5, 3, 0.8])

            # 1. 정보 표시
            col_info.markdown(
                f"### {student['name']} (`{student['id']}`)\n"
                f"📱 **학생:** `{student['phone']}`\n\n"
                f"👨‍👩‍👧 **학부모:** `{student['parent_phone']}`"
            )

            # 2. 상태 및 타이머
            if student["status"] == "미응답":
                col_status.info("⚪ **문자 미발송**\n\n학생에게 1차 문자를 발송해 보세요.")

            elif student["status"] == "학생대기중":
                elapsed = int(time.time() - student["stu_sent_time"])
                remain = max(0, 1200 - elapsed)
                min_left = remain // 60
                sec_left = remain % 60
                progress_val = min(1.0, max(0.0, remain / 1200))

                if remain > 0:
                    col_status.warning(
                        f"⏳ **[학생 1차] 답변 대기 중**\n\n"
                        f"### ⏱️ `{min_left:02d}분 {sec_left:02d}초`"
                    )
                    col_status.progress(progress_val)
                else:
                    col_status.error("⚠️ **학생 20분 무응답!**\n\n아래 버튼으로 학부모에게 2차 문자를 보내세요.")

            elif student["status"] == "학부모대기중":
                elapsed = int(time.time() - student["par_sent_time"])
                remain = max(0, 1200 - elapsed)
                min_left = remain // 60
                sec_left = remain % 60
                progress_val = min(1.0, max(0.0, remain / 1200))

                if remain > 0:
                    col_status.warning(
                        f"⏳ **[학부모 2차] 답변 대기 중**\n\n"
                        f"### ⏱️ `{min_left:02d}분 {sec_left:02d}초`"
                    )
                    col_status.progress(progress_val)
                else:
                    col_status.error("🚨 **20분 초과: 무단결과 전환 중...**")

            elif student["status"] == "사유제출 완료":
                col_status.success(
                    f"✅ **사유 제출 완료** (`{student['submitted_by']}` 제출)\n\n"
                    f"**사유:** {student['reason']}"
                )

            elif student["status"] == "무단결과":
                col_status.error("🚨 **무단결과 처리됨**\n\n학생 및 학부모 모두 20분 내 무응답")

            # 3. 단계별 문자 발송 버튼
            if student["status"] == "미응답":
                if col_action.button("📱 [1차] 학생에게 문자 발송", key=f"send_stu_{idx}", use_container_width=True):
                    student["status"] = "학생대기중"
                    student["stu_sent_time"] = time.time()
                    st.toast(f"{student['name']} 학생에게 1차 문자를 보냈습니다.")
                    st.rerun()

            elif student["status"] == "학생대기중":
                col_action.caption("✅ 학생 1차 문자 발송 완료")
                if col_action.button("👨‍👩‍👧 [2차] 학부모에게 문자 발송", key=f"send_par_{idx}", use_container_width=True):
                    student["status"] = "학부모대기중"
                    student["par_sent_time"] = time.time()  # 학부모 20분 타이머 시작
                    st.toast(f"{student['name']} 학부모님께 2차 문자를 보냈습니다.")
                    st.rerun()

            elif student["status"] == "학부모대기중":
                col_action.caption("✅ 학생 1차 발송 완료\n✅ 학부모 2차 발송 완료")

            else:
                col_action.caption("처리 완료된 항목입니다.")

            # 4. 삭제 버튼
            if col_delete.button("🗑️", key=f"del_btn_{idx}"):
                st.session_state.students.pop(idx)
                st.rerun()

            st.divider()

        # CSV 다운로드
        df = pd.DataFrame(st.session_state.students)
        if not df.empty:
            df_export = df[
                ["id", "name", "phone", "parent_phone", "status", "submitted_by", "reason"]
            ].copy()
            df_export.columns = [
                "학번",
                "이름",
                "학생연락처",
                "학부모연락처",
                "처리상태",
                "제출자",
                "결석사유",
            ]
            csv_data = df_export.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="📥 출석 결과 CSV 다운로드",
                data=csv_data,
                file_name="결석_사유_확인_결과.csv",
                mime="text/csv",
            )

# ------------------------------------------
# TAB 2: 학생/학부모 제출 시뮬레이션
# ------------------------------------------
with tab_submit:
    st.subheader("📩 결석 사유 제출 (학생/학부모 수신용)")

    waiting_list = [
        s for s in st.session_state.students 
        if s["status"] in ["학생대기중", "학부모대기중"]
    ]

    if not waiting_list:
        st.info("현재 사유를 제출할 대기 대상이 없습니다. (교사용 탭에서 문자를 발송해 주세요.)")
    else:
        student_options = [
            f"{s['id']} {s['name']} (현재 상태: {s['status']})"
            for s in waiting_list
        ]
        selected_option = st.selectbox("제출 대상 학생 선택", student_options)

        if selected_option:
            selected_id = selected_option.split()[0]
            curr_student = next(s for s in st.session_state.students if s["id"] == selected_id)

            # 현재 단계에 따른 남은 시간 계산
            ref_time = (
                curr_student["par_sent_time"]
                if curr_student["status"] == "학부모대기중"
                else curr_student["stu_sent_time"]
            )
            elapsed = int(time.time() - ref_time)
            remain = max(0, 1200 - elapsed)

            if remain <= 0 and curr_student["status"] == "학부모대기중":
                st.error("⚠️ 제출 제한시간(20분)이 지나 무단결과 처리되었습니다. 담임교사에게 직접 문의해 주세요.")
            else:
                st.warning(
                    f"⏰ [{curr_student['status']}] 남은 제출 시간: **{remain // 60}분 {remain % 60}초**"
                )
                st.progress(remain / 1200)

                with st.form("reason_submit_form"):
                    submitter_type = st.radio(
                        "제출자 구분",
                        ["학생 본인", "학부모"],
                        horizontal=True,
                    )
                    user_reason = st.text_area(
                        "결석 사유를 작성해 주세요",
                        placeholder="예: 발열 증상으로 인하여 병원 진료 후 등교 예정입니다.",
                    )
                    submit_btn = st.form_submit_button("사유 제출하기", use_container_width=True)

                    if submit_btn:
                        if user_reason.strip():
                            curr_student["status"] = "사유제출 완료"
                            curr_student["reason"] = user_reason.strip()
                            curr_student["submitted_by"] = submitter_type
                            st.success(f"[{submitter_type}] 결석 사유가 정상 등록되었습니다.")
                            st.rerun()
                        else:
                            st.error("결석 사유를 입력해 주세요.")

# ==========================================
# 4. 1초 자동 새로고침 (타이머 작동)
# ==========================================
if auto_refresh and any(
    s["status"] in ["학생대기중", "학부모대기중"] 
    for s in st.session_state.students
):
    time.sleep(1)
    st.rerun()
