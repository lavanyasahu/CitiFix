import streamlit as st

# --- Ensure default admin exists ---
try:
    from auth import create_admin_user
    create_admin_user("admin", "admin@example.com", "AdminPass123!")
except Exception as e:
    print("Admin seeding failed:", e)

from database import Database
from auth import Authentication
from datetime import datetime
import base64, os

DB = Database()
AUTH = Authentication()

st.set_page_config(page_title='CitiFix', layout='wide', initial_sidebar_state='expanded')

STYLE = '''
<style>
:root{
  --accent: #0b74ff;
  --muted: #6b7280;
  --bg: #f7f9fc;
  --card: #ffffff;
  --soft: #eef6ff;
}
body { font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; background: var(--bg); }
.app-header { display:flex; align-items:center; gap:14px; }
.app-title { font-size:20px; font-weight:700; color: #0b2545; }
.app-sub { color: var(--muted); font-size:13px; margin-top:-4px; }
.sidebar { background: var(--card); padding:12px; border-radius:8px; }
.issue-card { background: var(--card); padding:16px; border-radius:12px; box-shadow: 0 4px 14px rgba(16,24,40,0.06); margin-bottom:12px; }
.badge { padding:6px 10px; border-radius:999px; font-weight:600; font-size:12px; color:white; }
.badge-pending{ background:#f59e0b }
.badge-in_progress{ background:#2563eb }
.badge-resolved{ background:#10b981 }
.small-muted { color: var(--muted); font-size:13px; }
.login-box { background: linear-gradient(180deg,#ffffff,#fbfdff); padding:14px; border-radius:10px; box-shadow: 0 6px 18px rgba(12,24,40,0.04); }
.header-logo { width:56px; height:56px; border-radius:8px; background: linear-gradient(180deg,#0b74ff,#2f9bff); display:flex; align-items:center; justify-content:center; color:white; font-weight:700; }
.btn-primary{ background: linear-gradient(180deg,#0b74ff,#2f9bff); color: white; padding:8px 14px; border-radius:10px; border:none; }
</style>
'''

st.markdown(STYLE, unsafe_allow_html=True)

def get_logo_base64():
    svg = '<svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="0" y="0" width="24" height="24" rx="4" fill="#0b74ff"/><path d="M6 13l3 3 7-9" stroke="white" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    return 'data:image/svg+xml;base64,' + base64.b64encode(svg.encode('utf-8')).decode('utf-8')

def show_header():
    cols = st.columns([1,6,1])
    with cols[0]:
        st.image(get_logo_base64(), width=56)
    with cols[1]:
        st.markdown(f'<div class="app-header"><div class="app-title">CitiFix</div><div class="app-sub">Fixing city problems together</div></div>', unsafe_allow_html=True)
    with cols[2]:
        if st.session_state.get('user'):
            u = st.session_state['user']
            st.markdown(f"**{u['username']}** • {u['role'].capitalize()}")
            if st.button("Logout"):
                st.session_state.pop('user', None)
                st.rerun()

def render_issue_card(issue):
    status = issue.get('status','pending')
    badge_class = f"badge-{status}"
    st.markdown(f'<div class="issue-card">', unsafe_allow_html=True)
    cols = st.columns([4,1,1])
    with cols[0]:
        st.markdown(f"### {issue.get('title')}")
        st.write(issue.get('description')[:300])
        st.markdown(f'<div class="small-muted">Reported: {issue.get("created_at")}</div>', unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f'<div class="small-muted">Category</div><div class="badge {badge_class}" style="margin-top:8px">{status}</div>', unsafe_allow_html=True)
    with cols[2]:
        if st.button("View", key=f"view_{issue['id']}"):
            st.session_state['view_issue'] = issue['id']
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def show_issue_detail(issue):
    st.markdown(f'<div class="issue-card">', unsafe_allow_html=True)
    st.markdown(f"## {issue['title']}")
    st.write(issue['description'])
    st.markdown(f"**Category:** {issue['category']}  •  **Status:** {issue['status']}")
    st.markdown(f"**Reported at:** {issue.get('created_at')}")
    if issue.get('resolved_at'):
        resolver = DB.get_user_by_id(issue.get('resolved_by')) if issue.get('resolved_by') else None
        resolver_name = resolver['username'] if resolver else issue.get('resolved_by')
        st.success(f"Resolved by {resolver_name} at {issue.get('resolved_at')}")
    st.markdown("### Authority Signatures")
    sigs = DB.get_signatures_for_issue(issue['id'])
    if not sigs:
        st.info("No authority signatures yet.")
    else:
        for s in sigs:
            u = DB.get_user_by_id(s['authority_id'])
            name = u['username'] if u else s['authority_id']
            st.write(f"- **{name}** at {s['signed_at']} — {s.get('note','')}")
    user = st.session_state.get('user')
    if user and user.get('role') in ('authority','admin'):
        st.markdown("### Authority Actions")
        note = st.text_input("Note (optional)", key=f"note_{issue['id']}")
        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("Sign", key=f"sign_{issue['id']}"):
                DB.add_authority_signature(issue['id'], user['id'], note or f"Signed by {user['username']}")
                st.success("Signed successfully.")
                st.rerun()
        with col2:
            if st.button("Mark Resolved", key=f"resolve_{issue['id']}"):
                DB.mark_issue_resolved(issue['id'], user['id'], note or f"Resolved by {user['username']}")
                st.success("Issue marked as resolved.")
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def page_home():
    st.title("Public Issues")
    issues = DB.get_all_issues()
    if not issues:
        st.info("No issues reported yet.")
        return
    for issue in issues:
        render_issue_card(issue)

def page_report():
    st.title("Report an Issue")
    with st.form("report_form", clear_on_submit=True):
        title = st.text_input("Title")
        category = st.selectbox("Category", ["Road", "Water Supply", "Electricity", "Garbage", "Other"])
        description = st.text_area("Description")
        lat = st.text_input("Latitude (optional)")
        lon = st.text_input("Longitude (optional)")
        submitted = st.form_submit_button("Submit Issue")
        if submitted:
            issue = {
                "title": title,
                "category": category,
                "description": description,
                "latitude": float(lat) if lat else None,
                "longitude": float(lon) if lon else None,
                "user_id": st.session_state.get('user', {}).get('id') if st.session_state.get('user') else None
            }
            DB.create_issue(issue)
            st.success("Issue submitted successfully.")
            st.rerun()

def page_citizen_register():
    st.title("Citizen Register")
    with st.form("cit_reg", clear_on_submit=True):
        uname = st.text_input("Username")
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")
        phone = st.text_input("Phone (optional)")
        create = st.form_submit_button("Create Account")
        if create:
            uid = AUTH.register_citizen(uname, email, pwd, phone)
            if uid:
                st.success("Account created. You can now login.")
            else:
                st.error("Failed to create account (username/email may already exist).")

def page_citizen_login():
    st.title("Citizen Login")
    with st.form("cit_login"):
        uname = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        if submit:
            user = AUTH.login_user(uname, pwd)
            if not user or user.get('role') != 'citizen':
                st.error("Invalid credentials for citizen.")
            else:
                st.session_state['user'] = user
                st.success(f"Signed in as {user['username']} (citizen)")
                st.rerun()

def page_authority_login():
    st.title("Authority / Admin Login")
    with st.form("auth_login"):
        uname = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        if submit:
            user = AUTH.login_user(uname, pwd)
            if not user or user.get('role') not in ('authority','admin'):
                st.error("Invalid credentials for authority/admin.")
            else:
                st.session_state['user'] = user
                st.success(f"Signed in as {user['username']} ({user['role']})")
                st.rerun()

def page_admin_panel():
    st.title("Admin Panel")
    user = st.session_state.get('user')
    if not user or user.get('role') != 'admin':
        st.error("You must be signed in as an admin to view this page.")
        return
    st.subheader("Create Authority Account")
    with st.form("create_authority_form"):
        uname = st.text_input("Username")
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")
        phone = st.text_input("Phone (optional)")
        create = st.form_submit_button("Create Authority")
        if create:
            uid = AUTH.create_authority(uname, email, pwd, phone)
            if uid:
                st.success(f"Authority user {uname} created (id: {uid})")
            else:
                st.error("Failed to create user (maybe username/email already exists).")
    st.markdown("---")
    st.subheader("All users")
    users = DB.get_all_users()
    st.dataframe(users)

def main():
    show_header()
    st.sidebar.markdown("## Navigate")
    menu = ["Home", "Report", "Citizen Login", "Citizen Register", "Authority Login", "Admin Panel"]
    choice = st.sidebar.radio("", menu)
    st.sidebar.markdown("---")
    if choice == "Home":
        if st.session_state.get('view_issue'):
            issue_id = st.session_state.get('view_issue')
            issue = DB.get_issue_by_id(issue_id)
            if issue:
                show_issue_detail(issue)
            else:
                st.info("Issue not found.")
        else:
            page_home()
    elif choice == "Report":
        page_report()
    elif choice == "Citizen Login":
        page_citizen_login()
    elif choice == "Citizen Register":
        page_citizen_register()
    elif choice == "Authority Login":
        page_authority_login()
    elif choice == "Admin Panel":
        page_admin_panel()

if __name__ == '__main__':
    main()