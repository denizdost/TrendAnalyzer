import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from analysis import (
    load_data, preprocess, calculate_performance_score,
    apply_kmeans_clustering, apply_sentiment_to_reviews,
    verify_discount, seller_trust_analysis, category_statistics,
    price_history, product_sentiment_summary
)

st.set_page_config(page_title="TrendAnalyzer", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Outfit:wght@300;400;600;700;800&display=swap');

:root {
    --bg: #080c14;
    --glass: rgba(255,255,255,0.04);
    --glass-border: rgba(255,255,255,0.08);
    --glass-hover: rgba(255,255,255,0.07);
    --accent: #ff6b35;
    --accent-soft: rgba(255,107,53,0.15);
    --green: #34d399;
    --green-soft: rgba(52,211,153,0.12);
    --blue: #60a5fa;
    --blue-soft: rgba(96,165,250,0.12);
    --yellow: #fbbf24;
    --text: #e2e8f0;
    --text-muted: #64748b;
    --text-dim: #334155;
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

/* Animated background */
[data-testid="stAppViewContainer"] {
    background: 
        radial-gradient(ellipse at 10% 20%, rgba(255,107,53,0.06) 0%, transparent 50%),
        radial-gradient(ellipse at 90% 80%, rgba(96,165,250,0.05) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(52,211,153,0.03) 0%, transparent 60%),
        #080c14;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.2rem 2rem 2rem 2rem; max-width: 100%; }

/* Glass metric cards */
.metric-card {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.5rem;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent);
}
.metric-card:hover {
    background: var(--glass-hover);
    border-color: rgba(255,255,255,0.14);
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}

.metric-label {
    font-size: 0.68rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.4rem;
    font-weight: 500;
}
.metric-value {
    font-family: 'Outfit', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    line-height: 1;
    letter-spacing: -0.02em;
}
.metric-value.green { color: var(--green); }
.metric-value.blue { color: var(--blue); }
.metric-value.orange { color: var(--accent); }
.metric-value.yellow { color: var(--yellow); }

/* Section titles */
.section-title {
    font-family: 'Outfit', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: var(--text);
    margin: 1.5rem 0 0.8rem 0;
    letter-spacing: -0.01em;
    opacity: 0.9;
}

/* Page title */
.page-title {
    font-family: 'Outfit', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.03em;
    margin-bottom: 0.15rem;
}
.page-subtitle {
    font-size: 0.78rem;
    color: var(--text-muted);
    margin-bottom: 1.2rem;
    font-weight: 400;
}

/* HR */
hr { border-color: rgba(255,255,255,0.06); margin: 1rem 0; }

/* Streamlit buttons - glassmorphism */
.stButton > button {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 0.4rem 1rem !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    backdrop-filter: blur(10px) !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    background: rgba(255,107,53,0.12) !important;
    border-color: rgba(255,107,53,0.4) !important;
    color: var(--accent) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(255,107,53,0.2) !important;
}
.stButton > button[kind="primary"] {
    background: rgba(255,107,53,0.15) !important;
    border-color: rgba(255,107,53,0.5) !important;
    color: var(--accent) !important;
}
.stButton > button[kind="primary"]:hover {
    background: rgba(255,107,53,0.25) !important;
    box-shadow: 0 4px 24px rgba(255,107,53,0.3) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--glass) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid var(--glass-border) !important;
    gap: 2px !important;
    backdrop-filter: blur(20px) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    color: var(--text-muted) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 6px 16px !important;
    transition: all 0.2s ease !important;
    border: none !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--text) !important;
    background: rgba(255,255,255,0.05) !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(255,107,53,0.15) !important;
    color: var(--accent) !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* Selectbox */
.stSelectbox > div > div {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    backdrop-filter: blur(10px) !important;
    transition: border-color 0.2s ease !important;
}
.stSelectbox > div > div:hover {
    border-color: rgba(255,107,53,0.3) !important;
}

/* Multiselect */
.stMultiSelect > div > div {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 10px !important;
    backdrop-filter: blur(10px) !important;
}

/* Slider */
.stSlider [data-baseweb="slider"] {
    padding: 0 !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    backdrop-filter: blur(10px) !important;
}

/* Text input */
.stTextInput > div > div > input, .stTextArea > div > div > textarea {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    transition: border-color 0.2s ease !important;
}
.stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
    border-color: rgba(255,107,53,0.4) !important;
    box-shadow: 0 0 0 2px rgba(255,107,53,0.1) !important;
}

/* Download button */
.stDownloadButton > button {
    background: var(--green-soft) !important;
    border: 1px solid rgba(52,211,153,0.3) !important;
    color: var(--green) !important;
    border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.82rem !important;
    transition: all 0.25s ease !important;
}
.stDownloadButton > button:hover {
    background: rgba(52,211,153,0.2) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(52,211,153,0.2) !important;
}

/* Spinner */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* Warning/info */
.stWarning { background: rgba(251,191,36,0.08) !important; border-color: rgba(251,191,36,0.2) !important; border-radius: 10px !important; }
.stInfo { background: var(--glass) !important; border-color: var(--glass-border) !important; border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans", color="#64748b", size=11),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        linecolor="rgba(255,255,255,0.06)",
        tickcolor="rgba(255,255,255,0.1)",
        tickfont=dict(color="#64748b", size=10),
        zerolinecolor="rgba(255,255,255,0.06)",
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        linecolor="rgba(255,255,255,0.06)",
        tickcolor="rgba(255,255,255,0.1)",
        tickfont=dict(color="#64748b", size=10),
        zerolinecolor="rgba(255,255,255,0.06)",
    ),
    margin=dict(l=10, r=10, t=30, b=10),
    hoverlabel=dict(
        bgcolor="rgba(8,12,20,0.95)",
        bordercolor="rgba(255,107,53,0.4)",
        font=dict(family="Plus Jakarta Sans", color="#e2e8f0", size=12),
    ),
    transition=dict(duration=400, easing="cubic-in-out"),
)

@st.cache_data
def get_data():
    products, sellers, reviews, prices = load_data()
    products, sellers = preprocess(products, sellers)
    reviews = apply_sentiment_to_reviews(reviews)
    scored = calculate_performance_score(products, sellers)
    clustered = apply_kmeans_clustering(scored)
    discounted = verify_discount(clustered)
    seller_trust = seller_trust_analysis(sellers, reviews)
    cat_stats = category_statistics(products)
    return discounted, seller_trust, cat_stats, prices, reviews

df, seller_df, cat_df, prices_df, reviews_df = get_data()

def metric_card(label, value, color="orange"):
    st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value {color}">{value}</div></div>', unsafe_allow_html=True)

# Header
st.markdown('<div style="font-family:Syne,sans-serif;font-size:1.4rem;font-weight:800;color:#ff6b35;padding-bottom:0.8rem;white-space:nowrap;">📊 TrendAnalyzer</div>', unsafe_allow_html=True)

filtered = df.copy()

st.markdown("<hr style='margin:0.5rem 0 0 0;'>", unsafe_allow_html=True)

# Tabs navigation
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Dashboard", "Product Detail", "Discount Verification", "Seller Trust", "Category Statistics"])

# ── DASHBOARD ──────────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="page-title">Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">General market overview</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1: metric_card("Total Products", f"{len(filtered):,}", "orange")
    with col2: metric_card("Best Buy Products", f"{(filtered['cluster_label']=='🏆 Best Buy').sum()}", "green")
    with col3: metric_card("Misleading Discounts", f"%{filtered['is_fake_discount'].mean()*100:.0f}", "blue")
    with col4: metric_card("Avg. Performance", f"{filtered['performance_score'].mean():.1f}", "orange")

    st.markdown("<hr>", unsafe_allow_html=True)
    col_l, col_r = st.columns([2, 1])

    with col_l:
        st.markdown('<div class="section-title">Average Price by Category</div>', unsafe_allow_html=True)
        cat_price = filtered.groupby("category")["discounted_price"].mean().reset_index().sort_values("discounted_price")
        fig = go.Figure(go.Bar(x=cat_price["discounted_price"], y=cat_price["category"], orientation="h", marker=dict(color="#ff6b35", opacity=0.85)))
        fig.update_layout(**PLOTLY_THEME, height=280)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">Product Distribution</div>', unsafe_allow_html=True)
        cluster_counts = filtered["cluster_label"].value_counts()
        fig2 = go.Figure(go.Pie(labels=cluster_counts.index, values=cluster_counts.values, hole=0.65,
            marker=dict(colors=["#4ade80", "#60a5fa", "#f87171"]), textinfo="percent", textfont=dict(size=11, color="#ccc")))
        fig2.update_layout(**PLOTLY_THEME, height=280, showlegend=True)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">Top Scored Products</div>', unsafe_allow_html=True)
    cols_needed = ["name", "category", "discounted_price", "rating", "performance_score", "cluster_label", "discount_verdict"]
    top = filtered[cols_needed].sort_values("performance_score", ascending=False).head(10).rename(columns={
        "name": "Product", "category": "Category", "discounted_price": "Price (₺)",
        "rating": "Rating", "performance_score": "Score", "cluster_label": "Label", "discount_verdict": "Discount"
    })
    st.dataframe(top, use_container_width=True, hide_index=True)

    csv = top.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download as CSV", csv, "top_products.csv", "text/csv")

# ── ÜRÜN DETAY ─────────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="page-title">Ürün Detay Analizi</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Product-level price history and review sentiment analysis</div>', unsafe_allow_html=True)

    all_names = filtered["name"].tolist()
    all_pids  = filtered["product_id"].tolist()
    chosen_name = st.selectbox("🔍 Search or select product",
        [None] + all_names,
        format_func=lambda x: "— Select a product —" if x is None else x,
        key="prod_select")
    selected_pid = all_pids[all_names.index(chosen_name)] if chosen_name else None

    if selected_pid:
        prod = filtered[filtered["product_id"] == selected_pid].iloc[0]

        col1, col2, col3, col4 = st.columns(4)
        with col1: metric_card("Fiyat", f"₺{prod['discounted_price']:,.0f}", "orange")
        with col2: metric_card("Rating", f"{prod['rating']} ⭐", "yellow")
        with col3: metric_card("Performans Skoru", f"{prod['performance_score']}", "green")
        with col4: metric_card("Label", prod['cluster_label'], "blue")

        st.markdown("<hr>", unsafe_allow_html=True)
        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown('<div class="section-title">📈 12-Month Price History</div>', unsafe_allow_html=True)
            ph = price_history(prices_df, selected_pid)
            fig = go.Figure(go.Scatter(
                x=ph["month"], y=ph["price"], mode="lines+markers",
                line=dict(color="#ff6b35", width=2), marker=dict(size=6, color="#ff6b35"),
                fill="tozeroy", fillcolor="rgba(255,107,53,0.08)"
            ))
            fig.update_layout(**PLOTLY_THEME, height=280)
            fig.update_xaxes(tickvals=list(range(1, 13)), ticktext=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])
            st.plotly_chart(fig, use_container_width=True)

        with col_r:
            st.markdown('<div class="section-title">💬 Review Sentiment Analysis</div>', unsafe_allow_html=True)
            sentiment_counts, total_reviews = product_sentiment_summary(reviews_df, selected_pid)
            metric_card("Total Reviews", f"{total_reviews}", "orange")

            if total_reviews > 0:
                pos = sentiment_counts["Positive"]
                neg = sentiment_counts["Negative"]
                neu = sentiment_counts["Neutral"]
                pos_pct = pos / total_reviews * 100
                neg_pct = neg / total_reviews * 100
                neu_pct = neu / total_reviews * 100

                fig2 = go.Figure(go.Bar(
                    x=[pos_pct, neu_pct, neg_pct],
                    y=["😊 Positive", "😐 Neutral", "😞 Negative"],
                    orientation="h",
                    marker=dict(color=["#4ade80", "#60a5fa", "#f87171"]),
                    text=[f"%{pos_pct:.0f} ({pos})", f"%{neu_pct:.0f} ({neu})", f"%{neg_pct:.0f} ({neg})"],
                    textposition="inside",
                ))
                fig2.update_layout(**PLOTLY_THEME, height=200)
                fig2.update_xaxes(range=[0, 100])
                st.plotly_chart(fig2, use_container_width=True)

                if pos_pct >= 60:
                    verdict, color, tc = "🟢 Customers are generally satisfied", "#052e16", "#4ade80"
                elif neg_pct >= 40:
                    verdict, color, tc = "🔴 Warning: High negative review rate", "#1c0505", "#f87171"
                else:
                    verdict, color, tc = "🟡 Mixed reviews", "#1c1100", "#facc15"
                st.markdown(f'<div style="background:{color};border-radius:8px;padding:0.8rem 1.2rem;margin-top:0.5rem;color:{tc};font-weight:600;font-size:0.9rem;">{verdict}</div>', unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">🔵 KMeans Cluster Analysis</div>', unsafe_allow_html=True)
        
        cluster_color = "#052e16" if prod["cluster_label"] == "🏆 Best Buy" else "#1c1100" if prod["cluster_label"] == "✅ Fair Value" else "#1c0505"
        cluster_tc = "#4ade80" if prod["cluster_label"] == "🏆 Best Buy" else "#facc15" if prod["cluster_label"] == "✅ Fair Value" else "#f87171"
        
        kc1, kc2, kc3, kc4 = st.columns(4)
        with kc1:
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-label">Price (Feature 1)</div>
                <div class="metric-value orange">₺{prod["discounted_price"]:,.0f}</div>
            </div>''', unsafe_allow_html=True)
        with kc2:
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-label">Performance Score (Feature 2)</div>
                <div class="metric-value green">{prod["performance_score"]}</div>
            </div>''', unsafe_allow_html=True)
        with kc3:
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-label">Review Count (Feature 3)</div>
                <div class="metric-value blue">{prod["review_count"]:,}</div>
            </div>''', unsafe_allow_html=True)
        with kc4:
            st.markdown(f'''
            <div style="background:{cluster_color};border-radius:12px;padding:1.2rem 1.4rem;margin-bottom:0.5rem;">
                <div class="metric-label" style="color:{cluster_tc};opacity:0.7;">KMeans Result</div>
                <div style="font-family:Syne,sans-serif;font-size:1.3rem;font-weight:700;color:{cluster_tc};">{prod["cluster_label"]}</div>
            </div>''', unsafe_allow_html=True)

        st.markdown(f'''
        <div style="background:#161616;border:1px solid #222;border-radius:10px;padding:0.8rem 1.2rem;margin-bottom:1rem;font-size:0.8rem;color:#555;">
            🤖 <span style="color:#888;">KMeans (k=3) algoritması bu ürünü fiyat, performans skoru ve yorum sayısı özelliklerine göre 
            StandardScaler ile normalize ederek <span style="color:{cluster_tc};font-weight:600;">{prod["cluster_label"]}</span> 
            cluster.</span>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">💰 Discount Analysis</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1: metric_card("Claimed Discount", f"%{prod['claimed_discount_rate']*100:.0f}", "orange")
        with col2: metric_card("Real Discount", f"%{prod['real_discount_rate']*100:.0f}", "green")
        with col3: metric_card("Result", prod['discount_verdict'], "blue")

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">🤖 Live BERT Sentiment Analysis</div>', unsafe_allow_html=True)
        st.markdown('''
        <div style="background:#161616;border:1px solid #222;border-radius:12px;padding:1rem 1.4rem;margin-bottom:1rem;">
            <div style="font-size:0.75rem;color:#555;margin-bottom:0.5rem;">
                Model: <span style="color:#ff6b35;">savasy/bert-base-turkish-sentiment-cased</span> 
                &nbsp;·&nbsp; HuggingFace Transformers &nbsp;·&nbsp; Fine-tuned on Turkish reviews
            </div>
            <div style="font-size:0.82rem;color:#888;">
                Write your own review and let the BERT model analyze it in real time.
            </div>
        </div>
        ''', unsafe_allow_html=True)

        user_review = st.text_area("Write a review...", placeholder="Örn: Ürün çok kaliteliydi, kesinlikle tavsiye ederim.", height=80, label_visibility="collapsed")

        if st.button("🔍 Analyze", type="primary"):
            if user_review.strip():
                col_bert, col_rule = st.columns(2)

                # Rule-based result (instant)
                from analysis import analyze_sentiment
                rule_verdict = analyze_sentiment(user_review)
                rule_emoji = "😊" if rule_verdict == "Positive" else "😞" if rule_verdict == "Negative" else "😐"
                rule_color = "#052e16" if rule_verdict == "Positive" else "#1c0505" if rule_verdict == "Negative" else "#1c1100"
                rule_tc = "#4ade80" if rule_verdict == "Positive" else "#f87171" if rule_verdict == "Negative" else "#facc15"

                with col_rule:
                    st.markdown(f'''
                    <div style="background:{rule_color};border-radius:10px;padding:1rem 1.4rem;">
                        <div style="font-size:0.7rem;color:{rule_tc};opacity:0.7;margin-bottom:4px;text-transform:uppercase;letter-spacing:0.08em;">Rule-Based Analysis</div>
                        <div style="font-family:Syne,sans-serif;font-size:1.4rem;font-weight:700;color:{rule_tc};">{rule_emoji} {rule_verdict}</div>
                        <div style="font-size:0.75rem;color:{rule_tc};opacity:0.7;margin-top:4px;">Turkish keyword list</div>
                    </div>
                    ''', unsafe_allow_html=True)

                # BERT result
                with col_bert:
                    with st.spinner("BERT analiz ediyor..."):
                        try:
                            from transformers import pipeline
                            bert = pipeline("text-classification", model="savasy/bert-base-turkish-sentiment-cased")
                            result = bert(user_review[:512])[0]
                            label = result["label"]
                            score = result["score"]
                            if label == "positive":
                                emoji, color, tc, verdict = "😊", "#052e16", "#4ade80", "Positive"
                            elif label == "negative":
                                emoji, color, tc, verdict = "😞", "#1c0505", "#f87171", "Negative"
                            else:
                                emoji, color, tc, verdict = "😐", "#1c1100", "#facc15", "Neutral"
                            st.markdown(f'''
                            <div style="background:{color};border-radius:10px;padding:1rem 1.4rem;">
                                <div style="font-size:0.7rem;color:{tc};opacity:0.7;margin-bottom:4px;text-transform:uppercase;letter-spacing:0.08em;">BERT Model</div>
                                <div style="font-family:Syne,sans-serif;font-size:1.4rem;font-weight:700;color:{tc};">{emoji} {verdict}</div>
                                <div style="font-size:0.75rem;color:{tc};opacity:0.7;margin-top:4px;">Confidence: %{score*100:.1f}</div>
                            </div>
                            ''', unsafe_allow_html=True)
                        except Exception:
                            st.markdown('''
                            <div style="background:#161616;border:1px solid #333;border-radius:10px;padding:1rem 1.4rem;">
                                <div style="font-size:0.7rem;color:#555;margin-bottom:4px;text-transform:uppercase;">BERT Model</div>
                                <div style="color:#555;font-size:0.9rem;">Model unavailable</div>
                            </div>
                            ''', unsafe_allow_html=True)
            else:
                st.warning("Please enter a review.")

# ── İNDİRİM DOĞRULAMA ─────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="page-title">İndirim Doğrulama</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Compare genuine vs. misleading discounts</div>', unsafe_allow_html=True)

    # Genel istatistikler
    real = filtered[~filtered["is_fake_discount"]]
    fake = filtered[filtered["is_fake_discount"]]
    col1, col2, col3 = st.columns(3)
    with col1: metric_card("Misleading Discounts", f"{len(fake)}", "orange")
    with col2: metric_card("Real Discount", f"{len(real)}", "green")
    with col3: metric_card("Ort. İndirim Farkı", f"%{filtered['discount_gap'].mean()*100:.1f}", "blue")

    st.markdown("<hr>", unsafe_allow_html=True)

    # Ürün bazlı arama
    st.markdown('<div class="section-title">🔍 Product-Based Discount Query</div>', unsafe_allow_html=True)
    disc_names = filtered["name"].tolist()
    disc_pids  = filtered["product_id"].tolist()
    disc_chosen = st.selectbox("🔍 Search or select product", [None] + disc_names,
        format_func=lambda x: "— Select a product —" if x is None else x, key="disc_select")
    selected_d = disc_pids[disc_names.index(disc_chosen)] if disc_chosen else None

    if selected_d:
        prod_d = filtered[filtered["product_id"] == selected_d].iloc[0]
        col1, col2, col3, col4 = st.columns(4)
        with col1: metric_card("Inflated Price", f"₺{prod_d['inflated_price']:,.0f}", "orange")
        with col2: metric_card("Discounted Price", f"₺{prod_d['discounted_price']:,.0f}", "green")
        with col3: metric_card("İddia Edilen", f"%{prod_d['claimed_discount_rate']*100:.0f}", "blue")
        with col4: metric_card("Real Discount", f"%{prod_d['real_discount_rate']*100:.0f}", "green")
        gap = prod_d['discount_gap'] * 100
        if prod_d['is_fake_discount']:
            st.markdown(f'<div style="background:#1c0505;border-radius:8px;padding:1rem 1.4rem;color:#f87171;font-weight:600;">❌ Misleading Discounts — İddia edilen ile gerçek arasında %{gap:.1f} </div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background:#052e16;border-radius:8px;padding:1rem 1.4rem;color:#4ade80;font-weight:600;">✅ Real Discount — Sadece %{gap:.1f} gap detected.</div>', unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

    # Genel grafikler
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-title">Claimed vs Real Discount</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=filtered["claimed_discount_rate"]*100, y=filtered["real_discount_rate"]*100,
            mode="markers",
            marker=dict(color=filtered["is_fake_discount"].map({True:"#f87171",False:"#4ade80"}), size=6, opacity=0.7),
            text=filtered["name"],
        ))
        fig.add_shape(type="line", x0=0, y0=0, x1=60, y1=60, line=dict(color="#444", dash="dash", width=1))
        fig.update_layout(**PLOTLY_THEME, height=320, xaxis_title="Claimed (%)", yaxis_title="Real (%)")
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">Misleading Discount Rate by Category</div>', unsafe_allow_html=True)
        fake_rate = filtered.groupby("category")["is_fake_discount"].mean().reset_index()
        fake_rate.columns = ["category", "fake_rate"]
        fake_rate = fake_rate.sort_values("fake_rate")
        fig2 = go.Figure(go.Bar(x=fake_rate["fake_rate"]*100, y=fake_rate["category"], orientation="h", marker=dict(color="#f87171", opacity=0.8)))
        fig2.update_layout(**PLOTLY_THEME, height=320, xaxis_title="Misleading Discounts Oranı (%)")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">Discount Detail Table</div>', unsafe_allow_html=True)
    show_df = filtered[["name","category","inflated_price","discounted_price","claimed_discount_rate","real_discount_rate","discount_gap","discount_verdict"]].copy()
    show_df["claimed_discount_rate"] = (show_df["claimed_discount_rate"]*100).round(1).astype(str)+"%"
    show_df["real_discount_rate"] = (show_df["real_discount_rate"]*100).round(1).astype(str)+"%"
    show_df["discount_gap"] = (show_df["discount_gap"]*100).round(1).astype(str)+"%"
    show_df = show_df.rename(columns={"name":"Product","category":"Category","inflated_price":"Inflated (₺)","discounted_price":"Discounted (₺)","claimed_discount_rate":"Claimed","real_discount_rate":"Real","discount_gap":"Gap","discount_verdict":"Result"})
    st.dataframe(show_df, use_container_width=True, hide_index=True)

# ── SATICI GÜVEN ───────────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="page-title">Satıcı Güven Analizi</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Seller ratings and customer satisfaction</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1: metric_card("Reliable Sellers", f"{(seller_df['trust_label']=='🟢 Güvenilir').sum()}", "green")
    with col2: metric_card("Average Sellers", f"{(seller_df['trust_label']=='🟡 Orta').sum()}", "orange")
    with col3: metric_card("Risky Sellers", f"{(seller_df['trust_label']=='🔴 Riskli').sum()}", "blue")

    st.markdown("<hr>", unsafe_allow_html=True)

    # Satıcı arama
    st.markdown('<div class="section-title">🔍 Seller-Based Analysis</div>', unsafe_allow_html=True)
    s_names = seller_df["name"].tolist()
    s_ids   = seller_df["seller_id"].tolist()
    s_chosen = st.selectbox("🔍 Search or select seller", [None] + s_names,
        format_func=lambda x: "— Select a seller —" if x is None else x, key="seller_select")
    selected_s = s_ids[s_names.index(s_chosen)] if s_chosen else None

    if selected_s:
        s = seller_df[seller_df["seller_id"] == selected_s].iloc[0]
        s = seller_df[seller_df["seller_id"] == selected_s].iloc[0]

        col1, col2, col3, col4 = st.columns(4)
        with col1: metric_card("Seller Rating", f"{s['rating']} ⭐", "yellow")
        with col2: metric_card("Total Sales", f"{s['total_sales']:,}", "orange")
        with col3: metric_card("Positive Yorum", f"%{s['positive_rate']:.1f}", "green")
        with col4: metric_card("Trust Score", f"{s['trust_score']}", "blue")

        # Satıcının ürünleri
        seller_products = filtered[filtered["seller_id"] == selected_s]
        if len(seller_products) > 0:
            st.markdown(f'<div class="section-title">Products by This Seller ({len(seller_products)} adet)</div>', unsafe_allow_html=True)
            show_sp = seller_products[["name","category","discounted_price","rating","performance_score","cluster_label","discount_verdict"]].rename(columns={
                "name":"Product","category":"Category","discounted_price":"Price (₺)","rating":"Rating","performance_score":"Score","cluster_label":"Label","discount_verdict":"Discount"
            })
            st.dataframe(show_sp, use_container_width=True, hide_index=True)

        # Güven etiketi
        if s['trust_label'] == "🟢 Güvenilir":
            st.markdown(f'<div style="background:#052e16;border-radius:8px;padding:1rem 1.4rem;color:#4ade80;font-weight:600;">{s["trust_label"]} — This seller has high ratings and positive review rate.</div>', unsafe_allow_html=True)
        elif s['trust_label'] == "🟡 Orta":
            st.markdown(f'<div style="background:#1c1100;border-radius:8px;padding:1rem 1.4rem;color:#facc15;font-weight:600;">{s["trust_label"]} — Caution: mixed performance.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background:#1c0505;border-radius:8px;padding:1rem 1.4rem;color:#f87171;font-weight:600;">{s["trust_label"]} — Evaluate carefully before purchasing from this seller.</div>', unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

    # Genel grafikler
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-title">Rating vs Positive Review Rate</div>', unsafe_allow_html=True)
        colors = seller_df["trust_label"].map({"🟢 Güvenilir":"#4ade80","🟡 Orta":"#facc15","🔴 Riskli":"#f87171"})
        fig = go.Figure()
        for label, color in [("🟢 Güvenilir","#4ade80"),("🟡 Orta","#facc15"),("🔴 Riskli","#f87171")]:
            sub = seller_df[seller_df["trust_label"]==label]
            if len(sub) == 0: continue
            fig.add_trace(go.Scatter(
                x=sub["rating"], y=sub["positive_rate"],
                mode="markers",
                name=label,
                marker=dict(color=color, size=12, opacity=0.85, line=dict(width=1, color="#0d0d0d")),
                customdata=sub[["name","trust_score"]].values,
                hovertemplate="<b>%{customdata[0]}</b><br>Puan: %{x}<br>Positive Yorum: %{y:.1f}%<br>Trust Score: %{customdata[1]}<extra></extra>"
            ))
        fig.update_layout(**PLOTLY_THEME, height=340,
            xaxis_title="Seller Rating", yaxis_title="Positive Reviews (%)",
            legend=dict(font=dict(color="#888", size=10), bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">Top 10 Sellers — Trust Score</div>', unsafe_allow_html=True)
        top_sellers = seller_df.sort_values("trust_score", ascending=True).tail(10)
        fig2 = go.Figure(go.Bar(x=top_sellers["trust_score"], y=top_sellers["name"], orientation="h", marker=dict(color="#4ade80", opacity=0.8)))
        fig2.update_layout(**PLOTLY_THEME, height=340, xaxis_title="Trust Score")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">Seller Table</div>', unsafe_allow_html=True)
    show_sellers = seller_df[["name","rating","total_sales","positive_rate","trust_score","trust_label"]].rename(columns={
        "name":"Seller","rating":"Rating","total_sales":"Total Sales","positive_rate":"Positive Reviews (%)","trust_score":"Trust Score","trust_label":"Label"})
    show_sellers = show_sellers.copy()
    show_sellers["Positive Reviews (%)"] = show_sellers["Positive Reviews (%)"].round(1)
    st.dataframe(show_sellers, use_container_width=True, hide_index=True)

# ── KATEGORİ ──────────────────────────────────────────────────────────────────
with tab5:
    st.markdown('<div class="page-title">Kategori İstatistikleri</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Category-level market analysis</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1: metric_card("Total Categories", f"{len(cat_df)}", "orange")
    with col2: metric_card("Highest Rated", cat_df.loc[cat_df["avg_rating"].idxmax(),"category"], "green")
    with col3: metric_card("Most Affordable", cat_df.loc[cat_df["avg_price"].idxmin(),"category"], "blue")

    st.markdown("<hr>", unsafe_allow_html=True)
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-title">Category Average Prices</div>', unsafe_allow_html=True)
        fig = go.Figure(go.Bar(x=cat_df["category"], y=cat_df["avg_price"], marker=dict(color="#ff6b35", opacity=0.85),
            error_y=dict(type="data", array=cat_df["std_price"], color="#333", thickness=1.5)))
        fig.update_layout(**PLOTLY_THEME, height=320, xaxis_tickangle=-30, yaxis_title="Avg. Price (₺)")
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">Category Average Ratings</div>', unsafe_allow_html=True)
        fig2 = go.Figure(go.Bar(x=cat_df["category"], y=cat_df["avg_rating"], marker=dict(color="#60a5fa", opacity=0.85)))
        fig2.update_layout(**PLOTLY_THEME, height=320, xaxis_tickangle=-30, yaxis_title="Avg. Rating", yaxis_range=[0,5])
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">Category Summary Table</div>', unsafe_allow_html=True)
    show_cat = cat_df.rename(columns={"category":"Category","avg_price":"Avg. Price (₺)","median_price":"Median Price (₺)","std_price":"Std. Dev.","avg_rating":"Avg. Rating","product_count":"Product Count"})
    st.dataframe(show_cat, use_container_width=True, hide_index=True)
