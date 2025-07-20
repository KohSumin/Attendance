
import streamlit as st
import pandas as pd
import datetime
import os

# 데이터 파일 경로
DATA_FILE = "attendance.csv"

# 데이터 파일 로드 또는 생성
if os.path.exists(DATA_FILE):
    attendance_df = pd.read_csv(DATA_FILE)
else:
    attendance_df = pd.DataFrame(columns=["날짜", "이름", "출석 시간"])

# 세션 상태 초기화
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'student_name' not in st.session_state:
    st.session_state.student_name = ""

# --- 공통 헤더 ---
st.title("🏫 비대면 출석 확인 앱")
st.markdown("---")

# --- 화면 전환 ---
if not st.session_state.logged_in:
    # --- 학생 로그인 화면 ---
    st.header("학생 출석 확인")
    student_name = st.text_input("이름을 입력하세요:")

    if st.button("출석 확인"):
        if student_name:
            now = datetime.datetime.now()
            today_date = now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H:%M:%S")

            # 중복 출석 확인
            if not ((attendance_df['날짜'] == today_date) & (attendance_df['이름'] == student_name)).any():
                new_entry = pd.DataFrame([[today_date, student_name, current_time]], columns=["날짜", "이름", "출석 시간"])
                attendance_df = pd.concat([attendance_df, new_entry], ignore_index=True)
                attendance_df.to_csv(DATA_FILE, index=False)
                st.session_state.logged_in = True
                st.session_state.student_name = student_name
                st.success(f"{student_name}님, {current_time}에 출석 처리되었습니다.")
                st.experimental_rerun() # 성공 후 바로 교사 화면으로 넘어가지 않도록 처리
            else:
                st.warning("이미 오늘 출석체크를 완료했습니다.")
        else:
            st.warning("이름을 입력해주세요.")

else:
    # --- 출석 완료 후 학생 화면 ---
    st.header(f"✅ {st.session_state.student_name}님, 환영합니다!")
    st.info("출석이 완료되었습니다. 이 창을 닫아도 됩니다.")
    if st.button("로그아웃"):
        st.session_state.logged_in = False
        st.session_state.student_name = ""
        st.experimental_rerun()


# --- 교사용 화면 ---
st.markdown("---")
st.header("교사용 대시보드")

if not attendance_df.empty:
    # 날짜 선택
    sorted_dates = sorted(attendance_df['날짜'].unique(), reverse=True)
    selected_date = st.selectbox("조회할 날짜를 선택하세요:", sorted_dates)

    # 선택된 날짜의 출석 기록 필터링
    daily_attendance = attendance_df[attendance_df['날짜'] == selected_date]

    if not daily_attendance.empty:
        st.dataframe(daily_attendance.sort_values(by="출석 시간").reset_index(drop=True))

        # CSV 다운로드
        csv = daily_attendance.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="CSV 파일로 다운로드",
            data=csv,
            file_name=f'attendance_{selected_date}.csv',
            mime='text/csv',
        )
    else:
        st.info("해당 날짜의 출석 기록이 없습니다.")

else:
    st.info("아직 출석 기록이 없습니다.")

# 교사용 비밀번호 입력 (간단한 형태)
password = st.text_input("교사용 비밀번호를 입력하세요", type="password")
if password == "teacher123": # 실제 앱에서는 더 안전한 인증 방식 사용 필요
    st.success("교사 인증 완료")
    # 교사만 볼 수 있는 추가 기능 구현 가능
else:
    if password != "":
        st.error("비밀번호가 일치하지 않습니다.")

