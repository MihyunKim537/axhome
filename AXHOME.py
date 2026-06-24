import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import calendar
from dateutil.relativedelta import relativedelta

# 1. 페이지 기본 설정
st.set_page_config(page_title="구매그룹 AI Home", layout="wide")

# 2. 상태 초기화
if 'posts' not in st.session_state:
    st.session_state.posts = [
        {
            "id": 0,
            "author": "관리자",
            "title": "[공지] 구매그룹 AI 자유 게시판 오픈",
            "content": "구매그룹 구성원들을 위한 자유 게시판입니다. 업무 관련 질문이나 AX 활용 사례를 공유해주세요.",
            "timestamp": "2026-06-23 09:00",
            "comments": []
        }
    ]

if 'cal_date' not in st.session_state:
    st.session_state.cal_date = date(2026, 6, 1)

# 고정 이벤트 (정기 이벤트는 캘린더 렌더링 시 동적 계산)
if 'events' not in st.session_state:
    initial_events = [
        {"날짜": date(2026, 1, 1), "이벤트": "신정", "유형": "공휴일"},
        {"날짜": date(2026, 2, 17), "이벤트": "설날", "유형": "공휴일"},
        {"날짜": date(2026, 3, 1), "이벤트": "삼일절", "유형": "공휴일"},
        {"날짜": date(2026, 5, 5), "이벤트": "어린이날", "유형": "공휴일"},
        {"날짜": date(2026, 6, 6), "이벤트": "현충일", "유형": "공휴일"},
        {"날짜": date(2026, 8, 3), "이벤트": "공장 비가동","유형": "기타"},
        {"날짜": date(2026, 8, 4), "이벤트": "공장 비가동","유형": "기타"},
        {"날짜": date(2026, 8, 5), "이벤트": "공장 비가동","유형": "기타"},
        {"날짜": date(2026, 8, 6), "이벤트": "공장 비가동","유형": "기타"},
        {"날짜": date(2026, 8, 7), "이벤트": "공장 비가동","유형": "기타"},
        {"날짜": date(2026, 8, 15), "이벤트": "광복절", "유형": "공휴일"},
        {"날짜": date(2026, 9, 25), "이벤트": "추석", "유형": "공휴일"},
        {"날짜": date(2026, 10, 3), "이벤트": "개천절", "유형": "공휴일"},
        {"날짜": date(2026, 10, 9), "이벤트": "한글날", "유형": "공휴일"},
        {"날짜": date(2026, 12, 25), "이벤트": "크리스마스", "유형": "공휴일"},
    ]
    st.session_state.events = pd.DataFrame(initial_events)

# --- 캘린더 정기 일정 계산 함수 ---
def get_recurring_events(year, month):
    recurring_events = []
    
    # 기준일: 2026년 첫 회로 개구회의 (격주 계산의 기준점)
    reference_tuesday = date(2026, 1, 6)
    
    # 1. 격주 화요일 "회로 개구회의"
    # 2. 매월 마지막 목요일 "프로브 개구회의"
    cal = calendar.Calendar()
    for week in cal.monthdatescalendar(year, month):
        for day in week:
            # 현재 달에 속하는 날짜만 계산
            if day.month == month:
                # 격주 화요일
                if day.weekday() == 1: # 0:월, 1:화
                    delta_weeks = (day - reference_tuesday).days // 7
                    if delta_weeks >= 0 and delta_weeks % 2 == 0:
                        recurring_events.append({
                            "날짜": day,
                            "이벤트": "회로 개구회의 (10~11시)",
                            "유형": "기타"
                        })
                # 마지막 목요일
                if day.weekday() == 3: # 3:목
                    # 현재 목요일에 7일을 더했을 때 달이 바뀌면, 이번이 마지막 목요일임
                    if (day + timedelta(days=7)).month != month:
                        recurring_events.append({
                            "날짜": day,
                            "이벤트": "프로브 개구회의 (시간미정)",
                            "유형": "기타"
                        })
    return pd.DataFrame(recurring_events)


LOG_FILE = "board_admin_log.txt"

def save_log(action, author, content):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {action} | 작성자: {author} | 내용: {content}\n")

# 3. 커스텀 CSS 적용
st.markdown("""
    <style>
    /* ... (기존 CSS와 동일) ... */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        padding-top: 20px;
    }
    .sidebar-button {
        display: block; padding: 10px; margin: 5px 0; background-color: #ffffff;
        border: 1px solid #e1e4e8; border-radius: 4px; text-decoration: none;
        color: #0056b3 !important; font-size: 0.9rem; font-weight: 500; transition: all 0.2s;
    }
    .sidebar-button:hover { background-color: #e9ecef; border-color: #0056b3; }
    .section-header-sidebar {
        color: #333; border-bottom: 2px solid #0056b3; padding-bottom: 5px;
        margin-top: 20px; margin-bottom: 10px; font-size: 1.1rem; font-weight: bold;
    }
    .section-header {
        font-size: 1.2rem !important; font-weight: bold; color: #333;
        border-left: 4px solid #0056b3; padding-left: 10px; margin-top: 25px; margin-bottom: 15px;
    }
    .post-container {
        border: 1px solid #e1e4e8; border-radius: 8px; padding: 15px;
        margin-bottom: 15px; background-color: #ffffff;
    }
    .comment-box {
        margin-left: 25px; padding: 8px 12px; background-color: #f8f9fa;
        border-left: 3px solid #dee2e6; border-radius: 4px; margin-top: 5px; font-size: 0.9rem;
    }
    .calendar-container { border: 1px solid #ddd; border-radius: 8px; overflow: hidden; background-color: #fff; }
    .calendar-grid { display: grid; grid-template-columns: repeat(7, 1fr); }
    .calendar-day-head {
        text-align: center; font-weight: bold; padding: 12px; background-color: #f8f9fa;
        color: #5f6368; border-bottom: 1px solid #ddd; font-size: 0.85rem;
    }
    .calendar-cell {
        background-color: white; min-height: 100px; padding: 8px;
        border-right: 1px solid #eee; border-bottom: 1px solid #eee; position: relative;
    }
    .calendar-cell:nth-child(7n) { border-right: none; }
    .event-tag {
        font-size: 0.75rem; padding: 2px 6px; margin-top: 3px; border-radius: 4px;
        color: white; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block;
    }
    .tag-holiday { background-color: #d93025; }
    .tag-work { background-color: #1a73e8; }
    </style>
""", unsafe_allow_html=True)

# 4. 사이드바
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/home.png", width=80)
    st.title("Menu")
    
    st.markdown('<div class="section-header-sidebar">📚 AX 자료 및 가이드</div>', unsafe_allow_html=True)
    st.markdown("""
        <a href="https://docs.google.com/document/d/1rD5S-c9IKBZ_RPewaT_eWpo4_1WA7fcR0mFhBPqfsnk/edit?tab=t.t203jgx741gd" target="_blank" class="sidebar-button">Gemini CLI 설치 가이드</a>
        <a href="https://docs.google.com/document/d/1lxEg6M7WHYedwoJ76RHGnjkE8WwbMsIpAMm1pIjmQ0s/edit?tab=t.j1get26r99yn#heading=h.v6lfecu1y0cv" target="_blank" class="sidebar-button">AX팀 기초 가이드</a>
        <a href="https://docs.google.com/presentation/d/1c2DEAnVmLemlfBoEMJxDvrmZZENafPw8nwhhVYAjjh8/edit?pli=1" target="_blank" class="sidebar-button">Gemini Ent. L1,2 교육</a>
        <a href="https://drive.google.com/a/ai.samsunghealthcare.com/open?id=1CemSAJh6xDf0g29dTMkYt0IxnGnjtlFCUXQWz1ZQWSI" target="_blank" class="sidebar-button">Gemini Ent. L3,4 교육</a>
        <a href="https://docs.google.com/document/d/10DciRxRvwO3jwt5ME7etWz_W1_jVC24o3iVOPTX9pM0/edit?tab=t.0#heading=h.hhkhikqs5ax3" target="_blank" class="sidebar-button">구매 ERP 자동화 가이드 1</a>
        <a href="https://docs.google.com/document/d/17DwDsOPa5-qsw0YmlwqjB97BxzyrVcLOuun5oPvgqq4/edit?tab=t.0#heading=h.89ckgmf56kc2" target="_blank" class="sidebar-button">구매 ERP 자동화 가이드 2</a>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header-sidebar">🤖 필수 AI 플랫폼</div>', unsafe_allow_html=True)
    st.markdown("""
        <a href="https://vertexaisearch.cloud.google.com/home/cid/cff7b324-a4a5-4a4c-ae32-c470f10f806f" target="_blank" class="sidebar-button">Gemini Ent. Portal</a>
        <a href="http://10.50.10.43:8080/main/main.do?movePage=B9B62959-7F6A-4C3F-82E7-C86861D63124" target="_blank" class="sidebar-button">AI 활용사례</a>
        <a href="http://10.50.234.77:3000/?action=cli-install" target="_blank" class="sidebar-button">메디슨 AX HUB (구축중)</a>
        <a href="https://axhub.sec.samsung.net/Home" target="_blank" class="sidebar-button">전사 AX HUB</a>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header-sidebar">🔗 주요 시스템</div>', unsafe_allow_html=True)
    st.markdown("""
        <a href="https://script.google.com/a/macros/ai.samsunghealthcare.com/s/AKfycbwKxZxVAmldaNxyiQaIA6Gs6f66-mZbSRiYutd4JMHKhxyoixalarvQWg7vt8sgfDQdFw" target="_blank" class="sidebar-button">메-SRM</a>
        <a href="#" target="_blank" class="sidebar-button" style="opacity: 0.5;">PSI Simulator</a>
    """, unsafe_allow_html=True)

# 5. 메인 헤더
st.title("구매그룹 AI Home")
st.markdown("**구매 업무 효율화를 위한 AX 가이드 및 AI 툴 통합 포털**")
st.divider()

# 6. 구매 게시판
st.markdown('<div class="section-header">📋 구매 게시판</div>', unsafe_allow_html=True)

# ... (게시판 관련 코드는 기존과 동일) ...
col_user, _ = st.columns([1, 2])
with col_user:
    current_user = st.text_input("본인 성함 입력 (글 관리용)", placeholder="글 삭제 시 필요합니다")

with st.expander("📝 새 게시글 작성"):
    with st.form("new_post_form", clear_on_submit=True):
        p_author = st.text_input("작성자", value=current_user if current_user else "")
        p_title = st.text_input("제목")
        p_content = st.text_area("내용")
        if st.form_submit_button("등록"):
            if p_author and p_title and p_content:
                new_post = {
                    "id": datetime.now().timestamp(), "author": p_author, "title": p_title, "content": p_content,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"), "comments": []
                }
                st.session_state.posts.insert(0, new_post)
                save_log("POST_CREATE", p_author, p_title)
                st.rerun()
            else: st.error("내용을 채워주세요.")

for i, post in enumerate(st.session_state.posts):
    with st.container():
        st.markdown(f"""
            <div class="post-container">
                <div style="font-weight:bold; color:#0056b3; font-size:1.1rem;">{post['title']}</div>
                <div style="font-size:0.8rem; color:#888;">{post['timestamp']} | 익명</div>
                <div style="margin-top:10px; white-space: pre-wrap;">{post['content']}</div>
            </div>
        """, unsafe_allow_html=True)
        if current_user and current_user == post['author']:
            if st.button(f"🗑️ 글 삭제", key=f"del_post_{post['id']}"):
                save_log("POST_DELETE", current_user, post['title'])
                st.session_state.posts.pop(i)
                st.rerun()
        for j, comm in enumerate(post['comments']):
            c_col1, c_col2 = st.columns([9, 1])
            with c_col1:
                st.markdown(f"""
                    <div class="comment-box">
                        <strong>익명</strong>: {comm['content']} <br>
                        <small style="color:#aaa;">{comm['timestamp']}</small>
                    </div>""", unsafe_allow_html=True)
            with c_col2:
                if current_user and current_user == comm['author']:
                    if st.button("❌", key=f"del_comm_{post['id']}_{j}"):
                        save_log("COMM_DELETE", current_user, comm['content'])
                        post['comments'].pop(j)
                        st.rerun()
        with st.expander("댓글 달기"):
            with st.form(f"comm_f_{post['id']}", clear_on_submit=True):
                c_author = st.text_input("작성자", value=current_user if current_user else "", key=f"ca_{post['id']}")
                c_content = st.text_input("내용", key=f"cc_{post['id']}")
                if st.form_submit_button("등록"):
                    if c_author and c_content:
                        post['comments'].append({
                            "author": c_author, "content": c_content,
                            "timestamp": datetime.now().strftime("%m-%d %H:%M")})
                        save_log("COMM_CREATE", c_author, c_content)
                        st.rerun()
st.divider()

# 7. 월별 캘린더 (수정된 부분)
st.markdown('<div class="section-header">📅 2026년 주요 일정</div>', unsafe_allow_html=True)

nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
with nav_col1:
    if st.button("◀ 이전 달"):
        st.session_state.cal_date -= relativedelta(months=1)
        st.rerun()
with nav_col2:
    st.markdown(f"<h3 style='text-align:center;'>{st.session_state.cal_date.strftime('%Y년 %m월')}</h3>", unsafe_allow_html=True)
with nav_col3:
    if st.button("다음 달 ▶"):
        st.session_state.cal_date += relativedelta(months=1)
        st.rerun()

cal_year = st.session_state.cal_date.year
cal_month = st.session_state.cal_date.month

# 고정 + 정기 일정을 합침
static_events = st.session_state.events
recurring_events_df = get_recurring_events(cal_year, cal_month)
all_events_for_month = pd.concat([static_events, recurring_events_df], ignore_index=True)

# 캘린더 그리드 구현
calendar_obj = calendar.Calendar(firstweekday=6) # 6 = Sunday
month_days = calendar_obj.monthdayscalendar(cal_year, cal_month)

st.markdown('<div class="calendar-container">', unsafe_allow_html=True)
st.markdown('<div class="calendar-grid">' + ''.join([f'<div class="calendar-day-head">{d}</div>' for d in ['일','월','화','수','목','금','토']]) + '</div>', unsafe_allow_html=True)

grid_html = '<div class="calendar-grid">'
for week in month_days:
    for day_num in week:
        if day_num == 0:
            grid_html += '<div class="calendar-cell" style="background-color:#f8f9fa;"></div>'
        else:
            curr_d = date(cal_year, cal_month, day_num)
            evs = all_events_for_month[all_events_for_month['날짜'] == curr_d]
            ev_html = ""
            for _, row in evs.iterrows():
                tag_cls = "tag-holiday" if row['유형'] == "공휴일" else "tag-work"
                ev_html += f'<div class="event-tag {tag_cls}" title="{row["이벤트"]}">{row["이벤트"]}</div>'
            
            weekday = curr_d.weekday() # 0=Mon, 6=Sun
            day_color = "#3c4043"
            if weekday == 6: day_color = "#d93025" # 일요일
            elif weekday == 5: day_color = "#1967d2" # 토요일
            
            grid_html += f'<div class="calendar-cell"><b style="color:{day_color}; font-size:0.9rem;">{day_num}</b>{ev_html}</div>'
grid_html += '</div></div>'
st.markdown(grid_html, unsafe_allow_html=True)

st.divider()
st.subheader("🔍 다가오는 주요 일정")
today = date.today()
# 다가오는 일정도 동적으로 계산
upcoming_recurring = pd.concat([
    get_recurring_events(today.year, today.month),
    get_recurring_events(today.year, (today+relativedelta(months=1)).month)
])
all_events_total = pd.concat([static_events, upcoming_recurring], ignore_index=True)

upcoming = all_events_total[all_events_total["날짜"] >= today].sort_values("날짜").drop_duplicates().head(5)
if not upcoming.empty:
    for _, row in upcoming.iterrows():
        color = "#e74c3c" if row["유형"] == "공휴일" else "#3498db"
        st.markdown(f'<span style="color:{color}; font-weight:bold;">[{row["날짜"]}]</span> {row["이벤트"]} ({row["유형"]})', unsafe_allow_html=True)

st.divider()
st.caption("© 2026 구매그룹. Managed by mh501.kim")

