import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import io

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Tính Lãi Tiết Kiệm | Fintech Mini App",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# SESSION STATE
# ============================================================
if "history" not in st.session_state:
    st.session_state.history = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "bot",
            "content": "Xin chào! Tôi là trợ lý Fintech. Bạn có thể hỏi về lãi đơn/kép, kỳ hạn, hoặc so sánh kết quả. Hãy hỏi bất kỳ điều gì!"
        }
    ]
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ============================================================
# BANK REFERENCE RATES (tham khảo – cập nhật 2025-2026)
# ============================================================
BANK_RATES = {
    "Vietcombank": {"1": 2.10, "3": 2.40, "6": 3.20, "12": 4.70, "24": 4.90},
    "Techcombank": {"1": 2.35, "3": 2.65, "6": 3.50, "12": 4.85, "24": 5.00},
    "MB Bank":     {"1": 2.50, "3": 2.80, "6": 3.60, "12": 4.90, "24": 5.10},
    "VPBank":      {"1": 2.60, "3": 2.90, "6": 3.70, "12": 5.00, "24": 5.20},
    "ACB":         {"1": 2.40, "3": 2.70, "6": 3.40, "12": 4.80, "24": 5.00},
    "TPBank":      {"1": 2.55, "3": 2.85, "6": 3.65, "12": 4.95, "24": 5.15},
}

# ============================================================
# CUSTOM CSS
# ============================================================
def get_css(dark: bool) -> str:
    if dark:
        return """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #e2e8f0; }
        .stApp { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); }
        #MainMenu, footer, header {visibility: hidden;}
        .hero {
            background: linear-gradient(135deg, #0f766e 0%, #0d9488 50%, #14b8a6 100%);
            padding: 2.1rem 2.3rem; border-radius: 18px; color: white;
            margin-bottom: 1.6rem; box-shadow: 0 12px 40px rgba(15,118,110,0.35);
            position: relative; overflow: hidden;
        }
        .hero h1 { font-size: 1.95rem; font-weight: 800; margin: 0 0 0.3rem 0; letter-spacing: -0.5px; }
        .hero p { font-size: 0.98rem; opacity: 0.92; margin: 0; }
        .hero-badge {
            display: inline-block; background: rgba(255,255,255,0.15);
            border: 1px solid rgba(255,255,255,0.25); padding: 0.25rem 0.8rem;
            border-radius: 999px; font-size: 0.75rem; font-weight: 600; margin-bottom: 0.8rem;
        }
        .m-card {
            background: #1e293b; border: 1px solid #334155; border-radius: 14px;
            padding: 1.25rem 1.3rem; box-shadow: 0 4px 16px rgba(0,0,0,0.25);
            text-align: center; transition: all 0.2s ease;
        }
        .m-card:hover { border-color: #14b8a6; transform: translateY(-2px); }
        .m-label { font-size: 0.75rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.4rem; }
        .m-value { font-size: 1.45rem; font-weight: 800; color: #f1f5f9; letter-spacing: -0.4px; }
        .m-value.green { color: #34d399; }
        .m-value.teal  { color: #2dd4bf; }
        .m-sub { font-size: 0.78rem; color: #64748b; margin-top: 0.25rem; }
        .section-head { font-size: 1.1rem; font-weight: 700; color: #f1f5f9; margin: 1.4rem 0 0.8rem 0; }
        .section-head::before { content: ""; width: 4px; height: 1.1rem; background: #14b8a6; border-radius: 4px; display: inline-block; margin-right: 0.45rem; }
        .info-soft { background: #134e4a; border: 1px solid #0f766e; border-radius: 12px; padding: 0.9rem 1.1rem; font-size: 0.85rem; color: #99f6e4; margin: 0.9rem 0; line-height: 1.5; }
        .disclaimer { background: #422006; border: 1px solid #854d0e; border-radius: 12px; padding: 0.85rem 1.1rem; font-size: 0.8rem; color: #fde68a; margin-top: 1.1rem; line-height: 1.5; }
        .bot-msg { background: #134e4a; border-radius: 12px 12px 12px 4px; padding: 0.7rem 0.95rem; margin: 0.4rem 0; font-size: 0.88rem; color: #ccfbf1; line-height: 1.5; }
        .user-msg { background: #334155; border-radius: 12px 12px 4px 12px; padding: 0.7rem 0.95rem; margin: 0.4rem 0; font-size: 0.88rem; color: #e2e8f0; text-align: right; }
        section[data-testid="stSidebar"] { background: #1e293b; border-right: 1px solid #334155; }
        .stButton > button {
            background: linear-gradient(135deg, #0f766e, #14b8a6) !important; color: white !important;
            border: none !important; border-radius: 11px !important; font-weight: 600 !important;
            box-shadow: 0 4px 14px rgba(15,118,110,0.3) !important;
        }
        .block-container { padding-top: 1.3rem !important; padding-bottom: 1.8rem !important; }
        </style>
        """
    else:
        return """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1e293b; }
        .stApp { background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%); }
        #MainMenu, footer, header {visibility: hidden;}
        .hero {
            background: linear-gradient(135deg, #0f766e 0%, #14b8a6 45%, #2dd4bf 100%);
            padding: 2.1rem 2.3rem; border-radius: 18px; color: white;
            margin-bottom: 1.6rem; box-shadow: 0 12px 40px rgba(15,118,110,0.22);
            position: relative; overflow: hidden;
        }
        .hero::after {
            content: ""; position: absolute; top: -40%; right: -10%;
            width: 360px; height: 360px;
            background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, transparent 70%);
            border-radius: 50%;
        }
        .hero h1 { font-size: 1.95rem; font-weight: 800; margin: 0 0 0.3rem 0; letter-spacing: -0.5px; }
        .hero p { font-size: 0.98rem; opacity: 0.93; margin: 0; }
        .hero-badge {
            display: inline-block; background: rgba(255,255,255,0.18);
            border: 1px solid rgba(255,255,255,0.3); padding: 0.25rem 0.8rem;
            border-radius: 999px; font-size: 0.75rem; font-weight: 600; margin-bottom: 0.8rem;
        }
        .m-card {
            background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px;
            padding: 1.25rem 1.3rem; box-shadow: 0 4px 16px rgba(15,23,42,0.04);
            text-align: center; transition: all 0.2s ease;
        }
        .m-card:hover { transform: translateY(-3px); box-shadow: 0 10px 28px rgba(15,23,42,0.08); border-color: #99f6e4; }
        .m-label { font-size: 0.75rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.4rem; }
        .m-value { font-size: 1.45rem; font-weight: 800; color: #0f172a; letter-spacing: -0.4px; }
        .m-value.green { color: #059669; }
        .m-value.teal  { color: #0d9488; }
        .m-sub { font-size: 0.78rem; color: #94a3b8; margin-top: 0.25rem; }
        .section-head { font-size: 1.1rem; font-weight: 700; color: #0f172a; margin: 1.4rem 0 0.8rem 0; display: flex; align-items: center; gap: 0.45rem; }
        .section-head::before { content: ""; width: 4px; height: 1.1rem; background: #14b8a6; border-radius: 4px; display: inline-block; }
        .info-soft { background: #f0fdfa; border: 1px solid #99f6e4; border-radius: 12px; padding: 0.9rem 1.1rem; font-size: 0.85rem; color: #0f766e; margin: 0.9rem 0; line-height: 1.5; }
        .disclaimer { background: #fffbeb; border: 1px solid #fde68a; border-radius: 12px; padding: 0.85rem 1.1rem; font-size: 0.8rem; color: #92400e; margin-top: 1.1rem; line-height: 1.5; }
        .bot-msg { background: #f0fdfa; border-radius: 12px 12px 12px 4px; padding: 0.7rem 0.95rem; margin: 0.4rem 0; font-size: 0.88rem; color: #134e4a; line-height: 1.5; }
        .user-msg { background: #f1f5f9; border-radius: 12px 12px 4px 12px; padding: 0.7rem 0.95rem; margin: 0.4rem 0; font-size: 0.88rem; color: #1e293b; text-align: right; }
        section[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e2e8f0; }
        .stButton > button {
            background: linear-gradient(135deg, #0f766e, #14b8a6) !important; color: white !important;
            border: none !important; border-radius: 11px !important; font-weight: 600 !important;
            box-shadow: 0 4px 14px rgba(15,118,110,0.25) !important;
        }
        .stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 6px 20px rgba(15,118,110,0.35) !important; }
        .block-container { padding-top: 1.3rem !important; padding-bottom: 1.8rem !important; }
        </style>
        """

st.markdown(get_css(st.session_state.dark_mode), unsafe_allow_html=True)

# ============================================================
# HELPERS
# ============================================================
def calc_simple(principal: float, rate: float, months: int) -> dict:
    t = months / 12.0
    interest = principal * (rate / 100.0) * t
    total = principal + interest
    balances = [principal + principal * (rate / 100.0) * (m / 12.0) for m in range(0, months + 1)]
    return {"interest": interest, "total": total, "monthly_balance": balances}

def calc_compound(principal: float, rate: float, months: int, n: int = 12) -> dict:
    t = months / 12.0
    r = rate / 100.0
    total = principal * ((1 + r / n) ** (n * t))
    interest = total - principal
    balances = [principal * ((1 + r / n) ** (n * (m / 12.0))) for m in range(0, months + 1)]
    return {"interest": interest, "total": total, "monthly_balance": balances}

def format_vnd(x: float) -> str:
    return f"{x:,.0f}".replace(",", ".") + " ₫"

def get_chatbot_reply(question: str, ctx: dict) -> str:
    q = question.lower().strip()
    p, r, m = ctx.get("principal", 0), ctx.get("rate", 0), ctx.get("months", 0)
    itype = ctx.get("itype", "kép")

    if any(k in q for k in ["lãi đơn", "lai don", "simple"]):
        return ("**Lãi đơn** = P × r × t\n\n"
                "Lãi chỉ tính trên số gốc ban đầu, không cộng dồn. "
                "Phù hợp kỳ hạn ngắn hoặc khi bạn muốn tính toán đơn giản, dễ hiểu.")
    if any(k in q for k in ["lãi kép", "lai kep", "compound"]):
        return ("**Lãi kép** = P × (1 + r/n)^(n×t)\n\n"
                "Lãi được cộng vào gốc và tiếp tục sinh lãi. "
                "Càng gửi lâu + ghép lãi thường xuyên thì lợi nhuận càng cao hơn lãi đơn.")
    if any(k in q for k in ["nên chọn", "nen chon", "kỳ hạn", "ky han", "nên gửi", "nen gui"]):
        if m <= 6:
            return f"Với kỳ hạn **{m} tháng**, chênh lệch lãi đơn/kép chưa lớn. Bạn có thể chọn lãi đơn cho đơn giản, hoặc lãi kép để tối ưu nhẹ."
        return (f"Với kỳ hạn **{m} tháng**, lãi kép thường mang lại lợi nhuận cao hơn rõ rệt. "
                "Nếu không cần rút giữa kỳ, hãy ưu tiên **lãi kép** (ghép hàng tháng nếu ngân hàng hỗ trợ).")
    if any(k in q for k in ["so sánh", "so sanh", "khác nhau", "khac nhau"]):
        return ("**Khác biệt chính:**\n"
                "• Lãi đơn → lãi chỉ trên gốc, dễ tính, lợi nhuận ổn định.\n"
                "• Lãi kép → lãi cộng dồn, lợi nhuận cao hơn khi kỳ hạn dài.\n\n"
                "Nhìn biểu đồ bên trái để thấy sự chênh lệch theo thời gian.")
    if any(k in q for k in ["ngân hàng", "ngan hang", "lãi suất", "lai suat", "vcb", "tcb", "mb"]):
        return ("Bạn có thể xem **bảng lãi suất tham khảo** ở tab «Lãi suất ngân hàng». "
                "Lãi suất thực tế thay đổi theo từng thời điểm, nên luôn đối chiếu với website chính thức của ngân hàng.")
    if any(k in q for k in ["an toàn", "an toan", "rủi ro", "rui ro", "uy tín", "uy tin"]):
        return ("App chỉ mang tính **tham khảo & giáo dục**. "
                "Lãi suất và điều kiện thực tế do ngân hàng quy định. "
                "App **không thu thập** bất kỳ dữ liệu cá nhân nào của bạn.")
    if any(k in q for k in ["cảm ơn", "cam on", "thanks", "cám ơn"]):
        return "Không có gì ạ! Cứ hỏi thêm nếu cần nhé 😊"
    if any(k in q for k in ["xin chào", "hello", "hi", "chào", "chao"]):
        return "Xin chào! Tôi là trợ lý Fintech. Bạn muốn hỏi về lãi đơn/kép, kỳ hạn, hay so sánh kết quả hiện tại?"

    return (f"Hiện tại bạn đang tính **{format_vnd(p)}**, kỳ hạn **{m} tháng**, "
            f"lãi suất **{r}%/năm**, loại **lãi {itype}**.\n\n"
            "Bạn có thể hỏi:\n• Lãi đơn và lãi kép khác nhau thế nào?\n"
            "• Nên chọn kỳ hạn bao lâu?\n• Lãi suất các ngân hàng thế nào?")

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### ⚙️ Thông số gửi tiết kiệm")
    st.markdown("---")

    principal = st.number_input(
        "Số tiền gửi (VND)",
        min_value=1_000_000,
        max_value=10_000_000_000,
        value=100_000_000,
        step=1_000_000,
        help="Số tiền gốc bạn muốn gửi"
    )

    months = st.selectbox(
        "Kỳ hạn gửi",
        options=[1, 3, 6, 9, 12, 18, 24, 36],
        index=4,
        format_func=lambda x: f"{x} tháng"
    )

    rate = st.number_input(
        "Lãi suất (%/năm)",
        min_value=0.1,
        max_value=15.0,
        value=5.50,
        step=0.1,
        format="%.2f"
    )

    itype = st.radio(
        "Loại lãi",
        options=["Lãi đơn (Simple)", "Lãi kép (Compound)"],
        index=1
    )

    n_compound = 12
    if "kép" in itype.lower():
        freq = st.selectbox(
            "Tần suất ghép lãi",
            options=[("Hàng tháng", 12), ("Hàng quý", 4), ("Hàng năm", 1)],
            format_func=lambda x: x[0],
            index=0
        )
        n_compound = freq[1]

    st.markdown("---")
    calc_btn = st.button("🚀 Tính toán ngay", use_container_width=True)

    # Dark mode toggle
    dark = st.toggle("🌙 Chế độ tối", value=st.session_state.dark_mode)
    if dark != st.session_state.dark_mode:
        st.session_state.dark_mode = dark
        st.rerun()

    st.markdown("""
    <div class="info-soft">
        <strong>💡 Lưu ý</strong><br>
        • Kết quả mang tính tham khảo.<br>
        • Lãi suất thực tế có thể thay đổi.<br>
        • Nên đối chiếu với ngân hàng.
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# CALCULATE
# ============================================================
is_compound = "kép" in itype.lower()
if is_compound:
    result = calc_compound(principal, rate, months, n_compound)
    itype_label = "Lãi kép"
else:
    result = calc_simple(principal, rate, months)
    itype_label = "Lãi đơn"

interest = result["interest"]
total = result["total"]
balances = result["monthly_balance"]

if is_compound:
    other = calc_simple(principal, rate, months)
    other_label = "Lãi đơn"
else:
    other = calc_compound(principal, rate, months, 12)
    other_label = "Lãi kép"

diff = interest - other["interest"]

# Save to history when button pressed
if calc_btn:
    st.session_state.history.insert(0, {
        "time": datetime.now().strftime("%H:%M:%S"),
        "principal": principal,
        "months": months,
        "rate": rate,
        "type": itype_label,
        "interest": interest,
        "total": total
    })
    st.session_state.history = st.session_state.history[:8]  # keep last 8

# ============================================================
# HERO
# ============================================================
st.markdown("""
<div class="hero">
    <div class="hero-badge">FINTECH MINI APP</div>
    <h1>💰 Tính Lãi Tiết Kiệm Ngân Hàng</h1>
    <p>Công cụ Fintech giúp bạn tính toán chính xác tiền lãi cuối kỳ – Đơn giản • Minh bạch • Tin cậy</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# METRICS
# ============================================================
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""
    <div class="m-card">
        <div class="m-label">Số tiền gửi</div>
        <div class="m-value">{format_vnd(principal)}</div>
        <div class="m-sub">Gốc ban đầu</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="m-card">
        <div class="m-label">Tiền lãi nhận được</div>
        <div class="m-value green">+{format_vnd(interest)}</div>
        <div class="m-sub">{itype_label}</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="m-card">
        <div class="m-label">Tổng nhận cuối kỳ</div>
        <div class="m-value teal">{format_vnd(total)}</div>
        <div class="m-sub">{months} tháng • {rate}%/năm</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Kết quả & Biểu đồ", "🏦 Lãi suất ngân hàng", "💬 Trợ lý AI", "🕘 Lịch sử tính"])

# ---------- TAB 1: Results + Chart ----------
with tab1:
    left, right = st.columns([1.5, 1], gap="medium")

    with left:
        st.markdown('<div class="section-head">Kết quả chi tiết</div>', unsafe_allow_html=True)
        summary = pd.DataFrame({
            "Hạng mục": [
                "Số tiền gốc", "Kỳ hạn", "Lãi suất", "Loại lãi",
                "Tiền lãi", "Tổng cuối kỳ", f"Chênh lệch vs {other_label}"
            ],
            "Chi tiết": [
                format_vnd(principal),
                f"{months} tháng ({months/12:.2f} năm)",
                f"{rate:.2f} % / năm",
                itype_label + (f" (ghép {n_compound} lần/năm)" if is_compound else ""),
                format_vnd(interest),
                format_vnd(total),
                format_vnd(abs(diff)) + (" (cao hơn)" if diff > 0 else " (thấp hơn)" if diff < 0 else " (bằng)")
            ]
        })
        st.dataframe(summary, use_container_width=True, hide_index=True, height=290)

        # Download CSV
        csv_buf = io.StringIO()
        summary.to_csv(csv_buf, index=False, encoding="utf-8-sig")
        st.download_button(
            "⬇️ Tải kết quả (CSV)",
            data=csv_buf.getvalue(),
            file_name=f"tinh_lai_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with right:
        st.markdown('<div class="section-head">So sánh nhanh</div>', unsafe_allow_html=True)
        st.metric("Lãi hiện tại", format_vnd(interest), delta=f"{diff:+,.0f} ₫ so với {other_label}".replace(",", "."))
        st.metric("Tổng cuối kỳ", format_vnd(total))
        st.metric("Tỷ suất sinh lời", f"{(interest/principal)*100:.2f} %")

    # Chart full width
    st.markdown('<div class="section-head">Biểu đồ tăng trưởng số dư</div>', unsafe_allow_html=True)
    months_axis = list(range(0, months + 1))
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months_axis, y=balances, mode="lines+markers", name=itype_label,
        line=dict(color="#0d9488", width=3), marker=dict(size=5),
        fill="tozeroy", fillcolor="rgba(13,148,136,0.12)"
    ))
    fig.add_trace(go.Scatter(
        x=months_axis, y=other["monthly_balance"], mode="lines", name=other_label,
        line=dict(color="#94a3b8", width=2, dash="dot")
    ))
    fig.update_layout(
        height=360, margin=dict(l=10, r=10, t=25, b=40),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title="Tháng", showgrid=True, gridcolor="#e2e8f0" if not st.session_state.dark_mode else "#334155"),
        yaxis=dict(title="Số dư (VND)", showgrid=True, gridcolor="#e2e8f0" if not st.session_state.dark_mode else "#334155", tickformat=",.0f"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=dict(family="Inter", size=12, color="#94a3b8" if st.session_state.dark_mode else "#334155"),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------- TAB 2: Bank rates ----------
with tab2:
    st.markdown('<div class="section-head">Lãi suất tiết kiệm tham khảo (%/năm)</div>', unsafe_allow_html=True)
    st.caption("Dữ liệu tham khảo (có thể thay đổi theo thời điểm). Nguồn: tổng hợp công bố của các ngân hàng.")

    rate_df = pd.DataFrame(BANK_RATES).T
    rate_df.columns = [f"{c} tháng" for c in rate_df.columns]
    rate_df.index.name = "Ngân hàng"
    st.dataframe(rate_df.style.format("{:.2f}"), use_container_width=True)

    st.markdown("""
    <div class="info-soft">
        <strong>Gợi ý sử dụng:</strong> Chọn kỳ hạn gần với nhu cầu của bạn → nhìn cột tương ứng → 
        nhập lãi suất vào sidebar bên trái để tính toán chính xác hơn.
    </div>
    """, unsafe_allow_html=True)

# ---------- TAB 3: Chatbot ----------
with tab3:
    st.markdown('<div class="section-head">Trợ lý tư vấn tiết kiệm</div>', unsafe_allow_html=True)

    # Quick suggestion buttons
    qs = st.columns(4)
    suggestions = [
        "Lãi đơn vs lãi kép?",
        "Nên chọn kỳ hạn nào?",
        "Lãi suất ngân hàng?",
        "App có an toàn không?"
    ]
    for i, s in enumerate(suggestions):
        if qs[i].button(s, use_container_width=True, key=f"sug_{i}"):
            st.session_state.chat_history.append({"role": "user", "content": s})
            ctx = {"principal": principal, "rate": rate, "months": months, "itype": "kép" if is_compound else "đơn"}
            reply = get_chatbot_reply(s, ctx)
            st.session_state.chat_history.append({"role": "bot", "content": reply})
            st.rerun()

    # Chat display
    for msg in st.session_state.chat_history[-8:]:
        if msg["role"] == "bot":
            st.markdown(f'<div class="bot-msg">{msg["content"].replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)

    user_q = st.chat_input("Hỏi trợ lý về tiết kiệm...")
    if user_q:
        st.session_state.chat_history.append({"role": "user", "content": user_q})
        ctx = {"principal": principal, "rate": rate, "months": months, "itype": "kép" if is_compound else "đơn"}
        reply = get_chatbot_reply(user_q, ctx)
        st.session_state.chat_history.append({"role": "bot", "content": reply})
        st.rerun()

# ---------- TAB 4: History ----------
with tab4:
    st.markdown('<div class="section-head">Lịch sử tính toán trong phiên</div>', unsafe_allow_html=True)
    if not st.session_state.history:
        st.info("Chưa có lịch sử. Nhấn «Tính toán ngay» ở sidebar để lưu kết quả.")
    else:
        hist_df = pd.DataFrame(st.session_state.history)
        hist_df["Số tiền gửi"] = hist_df["principal"].apply(format_vnd)
        hist_df["Tiền lãi"] = hist_df["interest"].apply(format_vnd)
        hist_df["Tổng cuối kỳ"] = hist_df["total"].apply(format_vnd)
        hist_df = hist_df.rename(columns={
            "time": "Thời gian", "months": "Kỳ hạn (tháng)",
            "rate": "Lãi suất (%)", "type": "Loại lãi"
        })
        show_cols = ["Thời gian", "Số tiền gửi", "Kỳ hạn (tháng)", "Lãi suất (%)", "Loại lãi", "Tiền lãi", "Tổng cuối kỳ"]
        st.dataframe(hist_df[show_cols], use_container_width=True, hide_index=True)

        if st.button("🗑️ Xóa lịch sử", use_container_width=True):
            st.session_state.history = []
            st.rerun()

# ============================================================
# DISCLAIMER + FOOTER
# ============================================================
st.markdown("""
<div class="disclaimer">
    <strong>⚠️ Tuyên bố miễn trừ trách nhiệm:</strong> 
    Ứng dụng chỉ mang tính chất tham khảo và giáo dục. Kết quả dựa trên công thức lãi đơn/lãi kép chuẩn. 
    Lãi suất thực tế, phương thức tính lãi và điều kiện gửi tiền do từng ngân hàng quy định. 
    Vui lòng kiểm tra biểu lãi suất và điều khoản chính thức trước khi quyết định gửi tiết kiệm. 
    Ứng dụng không thu thập, lưu trữ hay chia sẻ bất kỳ dữ liệu cá nhân nào của người dùng.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; margin-top:1.5rem; color:#94a3b8; font-size:0.78rem;">
    Mini App Fintech • Tính Lãi Tiết Kiệm • Phát triển cho môn Công nghệ Tài chính – TS. Vũ Đức Bình
</div>
""", unsafe_allow_html=True)
