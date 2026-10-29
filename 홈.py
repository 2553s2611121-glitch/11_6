    else:
        st.dataframe(pending[["학생 이름", "학급", "출결 상태", "연락 상태"]], use_container_width=True, hide_index=True)
        if st.button("학부모 연락 화면 열기", type="primary"):
            navigate("학부모 연결")
            st.rerun()
    st.markdown("### 🔗 사이트 사용 가이드")
    for service in SERVICES:
        st.markdown(f"- [{service['name']} 사용 방법 보기]({service['url']}) — {service['role']}")

elif page == "학생 관리":
    st.title("👥 학생 관리")
    st.write("학생 이름, 학급, 보호자 연락처를 관리합니다. 데모 데이터는 가상 학생입니다.")
    edited = st.data_editor(
        data[["학생 이름", "학급", "보호자 연락처"]].copy(),
        num_rows="dynamic", use_container_width=True, hide_index=True,
        column_config={"학생 이름": st.column_config.TextColumn(required=True), "학급": st.column_config.TextColumn(required=True), "보호자 연락처": st.column_config.TextColumn(help="공개 환경에서는 실제 연락처를 입력하지 마세요.")},
        key="student_editor",
    )
    if st.button("학생 정보 저장", type="primary"):
        updated = data.copy()
        updated["학생 이름"] = ""
        updated["학급"] = ""
        updated["보호자 연락처"] = ""
        # Keep existing attendance columns aligned by row order; newly added rows start as unconfirmed.
        rows = []
        for i, row in edited.fillna("").iterrows():
            old = data.iloc[i].to_dict() if i < len(data) else {"출결 상태": "미확인", "연락 상태": "연락 전", "날짜": today}
            rows.append({
                "학생 이름": str(row.get("학생 이름", "")), "학급": str(row.get("학급", "")),
                "보호자 연락처": str(row.get("보호자 연락처", "")),
                "출결 상태": old.get("출결 상태", "미확인"), "연락 상태": old.get("연락 상태", "연락 전"),
                "날짜": old.get("날짜", today)
            })
        set_data(pd.DataFrame(rows, columns=data.columns))
        st.success("학생 정보를 저장했습니다.")
        st.rerun()

elif page == "출결 기록":
    st.title("🗓️ 출결 기록")
    st.write("날짜별 출결을 수정하고 기록을 내려받을 수 있습니다.")
    edited = st.data_editor(
        data.copy(), num_rows="dynamic", use_container_width=True, hide_index=True,
        column_config={
            "출결 상태": st.column_config.SelectboxColumn(options=STATUSES, required=True),
            "연락 상태": st.column_config.SelectboxColumn(options=CONTACT_STATUSES, required=True),
            "날짜": st.column_config.TextColumn(help="YYYY-MM-DD 형식으로 입력"),
        }, key="attendance_editor"
    )
    if st.button("출결 기록 저장", type="primary"):
        edited = edited.fillna("")
        valid = edited["날짜"].astype(str).str.fullmatch(r"\d{4}-\d{2}-\d{2}").all()
        if not valid:
            st.error("날짜는 YYYY-MM-DD 형식으로 입력해 주세요.")
        elif (edited["학생 이름"].astype(str).str.strip() == "").any():
            st.error("학생 이름이 비어 있는 행을 확인해 주세요.")
        else:
            set_data(edited)
            st.success("출결 기록을 저장했습니다.")
            st.rerun()
    st.download_button("⬇️ 전체 출결 CSV 다운로드", data=data.to_csv(index=False).encode("utf-8-sig"), file_name=f"ongyeol_attendance_{today}.csv", mime="text/csv")
    st.info("Cloud 환경의 로컬 CSV는 재배포·재시작 시 영구 보관이 보장되지 않습니다. 중요한 기록은 정기적으로 다운로드해 안전한 학교 저장소에 보관하세요.")

elif page == "학부모 연결":
    st.title("👨‍👩‍👧 학부모 연결")
    st.write("결석 또는 출결 미확인 학생을 모아 보고, 연락 상태를 기록합니다.")
    pending = data[data["출결 상태"].isin(["결석", "미확인"])]
    if pending.empty:
        st.success("현재 결석 또는 미확인 학생이 없습니다.")
    else:
        st.dataframe(pending[["학생 이름", "학급", "보호자 연락처", "출결 상태", "연락 상태"]], use_container_width=True, hide_index=True)
    if data.empty:
        st.info("먼저 학생 관리 메뉴에서 학생을 추가하세요.")
    else:
        student = st.selectbox("연락할 학생 선택", data["학생 이름"].astype(str).tolist())
        idx = data.index[data["학생 이름"].astype(str) == student][0]
        row = data.loc[idx]
        st.write(f"**학급:** {row['학급'] or '미입력'}　 **보호자 연락처:** {row['보호자 연락처'] or '미입력'}")
        msg = make_message(student, row["날짜"] or today, row["출결 상태"])
        st.text_area("연락 문구 (선택해 복사할 수 있습니다)", value=msg, height=140, key="parent_message")
        st.caption("브라우저 클립보드 자동 접근은 사용하지 않습니다. 문구를 선택해 복사한 후 승인된 연락 서비스에 붙여 넣으세요.")
        current = row["연락 상태"] if row["연락 상태"] in CONTACT_STATUSES else "연락 전"
        status = st.selectbox("연락 처리 상태", CONTACT_STATUSES, index=CONTACT_STATUSES.index(current))
        if st.button("연락 상태 저장", type="primary"):
            updated = data.copy()
            updated.loc[idx, "연락 상태"] = status
            set_data(updated)
            st.success("연락 상태를 저장했습니다.")
            st.rerun()
        st.markdown("#### 관련 서비스")
        st.link_button("나이스(NEIS) 열기", "https://www.neis.go.kr/")
        st.link_button("학교 문자 서비스 찾기", SERVICES[1]["url"])

elif page == "자동 문자":
    st.title("✉️ 자동 문자")
    st.warning("이 앱은 문자를 자동 발송하지 않습니다. 학교에서 승인한 문자 서비스로 이동하고, 문구를 복사해 발송 전 직접 확인하는 방식입니다.")
    if data.empty:
        st.info("학생 관리에서 학생을 추가해 주세요.")
    else:
        student = st.selectbox("학생 선택", data["학생 이름"].astype(str).tolist(), key="sms_student")
        row = data[data["학생 이름"].astype(str) == student].iloc[0]
        msg = make_message(student, row["날짜"] or today, row["출결 상태"])
        st.text_area("문자 내용", value=msg, height=160, key="sms_message")
        st.markdown("#### 문자 서비스 바로가기")
        st.link_button("학교 문자 발송 서비스 찾기", SERVICES[1]["url"])
        st.caption("학교에서 실제로 사용하는 문자 서비스 주소가 있다면 위 링크 대신 해당 주소를 사용하세요. 발송 전 학생, 수신자, 날짜, 문구를 반드시 확인하세요.")
    st.markdown("#### 사용 방법")
    st.markdown("1. 학생을 선택하고 문구를 확인합니다.\\n2. 문구를 선택해 복사합니다.\\n3. 학교에서 승인한 문자 발송 사이트에 접속합니다.\\n4. 보호자 수신자와 내용을 확인한 뒤 발송합니다.\\n5. 학부모 연결 메뉴에서 처리 상태를 기록합니다.")

elif page == "사이트 사용 가이드":
    st.title("🔗 사이트 사용 가이드")
    st.write("각 사이트의 역할과 기본 사용 방법입니다. 실제 사용은 학교의 권한과 내부 지침을 우선하세요.")
    for service in SERVICES:
        with st.container(border=True):
            st.subheader(service["name"])
            st.write("**역할:** " + service["role"])
            st.write("**사용 방법:** " + service["how"])
            st.link_button(service["label"], service["url"])
    st.divider()
    st.subheader("개인정보 보호 안내")
    st.markdown("- 공개 GitHub 저장소에는 가상 학생 데이터만 올리세요.\\n- 실제 학생 정보는 학교의 승인된 환경에서만 처리하세요.\\n- 이 프로토타입에는 사용자 로그인, 교사별 권한 분리, 데이터베이스 동기화가 없습니다.")

st.divider()
st.caption("온결은 교사의 출결 확인을 돕는 보조 도구입니다. 최종 출결 판단과 보호자 연락은 담당 교사가 확인해야 합니다.")
