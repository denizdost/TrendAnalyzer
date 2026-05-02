import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from analysis import (
    load_data, preprocess, calculate_performance_score,
    verify_discount, seller_trust_analysis, category_statistics,
    price_history, product_sentiment_summary
)

st.set_page_config(page_title="TrendAnalyzer", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background-color: #0d0d0d; color: #e8e8e8; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 2rem 2rem; max-width: 100%; }
[data-testid="stSidebar"] { background: #111111; border-right: 1px solid #1e1e1e; }
.metric-card { background: #161616; border: 1px solid #222; border-radius: 12px; padding: 1.2rem 1.4rem; margin-bottom: 0.5rem; }
.metric-label { font-size: 0.72rem; color: #555; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.3rem; }
.metric-value { font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 700; line-height: 1; }
.metric-value.green { color: #4ade80; }
.metric-value.blue { color: #60a5fa; }
.metric-value.orange { color: #ff6b35; }
.metric-value.yellow { color: #facc15; }
.section-title { font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700; color: #e8e8e8; margin: 1.5rem 0 0.8rem 0; }
.page-title { font-family: 'Syne', sans-serif; font-size: 1.8rem; font-weight: 800; color: #ffffff; letter-spacing: -0.03em; margin-bottom: 0.2rem; }
.page-subtitle { font-size: 0.82rem; color: #555; margin-bottom: 1.5rem; }
hr { border-color: #1e1e1e; margin: 1rem 0; }
.search-section { background: #161616; border: 1px solid #222; border-radius: 12px; padding: 1.2rem 1.4rem; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#888", size=11),
    xaxis=dict(gridcolor="#1a1a1a", linecolor="#1a1a1a"),
    yaxis=dict(gridcolor="#1a1a1a", linecolor="#1a1a1a"),
    margin=dict(l=10, r=10, t=30, b=10),
)

@st.cache_data
def get_data():
    products, sellers, reviews, prices = load_data()
    products, sellers = preprocess(products, sellers)
    scored = calculate_performance_score(products, sellers)
    discounted = verify_discount(scored)
    seller_trust = seller_trust_analysis(sellers, reviews)
    cat_stats = category_statistics(products)
    return discounted, seller_trust, cat_stats, prices, reviews

df, seller_df, cat_df, prices_df, reviews_df = get_data()

def metric_card(label, value, color="orange"):
    st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value {color}">{value}</div></div>', unsafe_allow_html=True)

# Top navbar
st.markdown('''
<div style="display:flex;align-items:center;justify-content:space-between;padding:0.6rem 0 1.2rem 0;border-bottom:1px solid #1e1e1e;margin-bottom:1.2rem;">
    <div style="font-family:Syne,sans-serif;font-size:1.4rem;font-weight:800;color:#ff6b35;white-space:nowrap;">📊 TrendAnalyzer</div>
    <div style="font-size:0.72rem;color:#444;">Trendyol Ürün Analizi</div>
</div>
''', unsafe_allow_html=True)

col_nav1, col_nav2, col_nav3, col_nav4, col_nav5 = st.columns(5)
pages = ["🏠  Dashboard", "🔍  Ürün Detay", "💰  İndirim Doğrulama", "🏪  Satıcı Güven", "📈  Kategori İstatistikleri"]
if "page" not in st.session_state:
    st.session_state.page = pages[0]

for col, p in zip([col_nav1, col_nav2, col_nav3, col_nav4, col_nav5], pages):
    with col:
        active = st.session_state.page == p
        if st.button(p, use_container_width=True, type="primary" if active else "secondary"):
            st.session_state.page = p
            st.rerun()

page = st.session_state.page

st.markdown("<hr>", unsafe_allow_html=True)

# Filters row
fc1, fc2, fc3 = st.columns([2, 3, 1])
with fc1:
    selected_cats = st.multiselect("Kategori", options=sorted(df["category"].unique()), default=[], placeholder="Tümü", label_visibility="collapsed")
with fc2:
    price_range = st.slider("Fiyat", 0, int(df["discounted_price"].max()), (0, int(df["discounted_price"].max())), label_visibility="collapsed")
with fc3:
    st.markdown(f'<div style="font-size:0.75rem;color:#555;padding-top:0.5rem;">{len(df)} ürün</div>', unsafe_allow_html=True)

filtered = df.copy()
if selected_cats:
    filtered = filtered[filtered["category"].isin(selected_cats)]
filtered = filtered[(filtered["discounted_price"] >= price_range[0]) & (filtered["discounted_price"] <= price_range[1])]

st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)

# ── DASHBOARD ──────────────────────────────────────────────────────────────────
if page == "🏠  Dashboard":
    st.markdown('<div class="page-title">Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Genel pazar özeti</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1: metric_card("Toplam Ürün", f"{len(filtered):,}", "orange")
    with col2: metric_card("Best Buy Ürün", f"{(filtered['cluster_label']=='🏆 Best Buy').sum()}", "green")
    with col3: metric_card("Yanıltıcı İndirim", f"%{filtered['is_fake_discount'].mean()*100:.0f}", "blue")
    with col4: metric_card("Ort. Performans", f"{filtered['performance_score'].mean():.1f}", "orange")

    st.markdown("<hr>", unsafe_allow_html=True)
    col_l, col_r = st.columns([2, 1])

    with col_l:
        st.markdown('<div class="section-title">Kategori Başına Ortalama Fiyat</div>', unsafe_allow_html=True)
        cat_price = filtered.groupby("category")["discounted_price"].mean().reset_index().sort_values("discounted_price")
        fig = go.Figure(go.Bar(x=cat_price["discounted_price"], y=cat_price["category"], orientation="h", marker=dict(color="#ff6b35", opacity=0.85)))
        fig.update_layout(**PLOTLY_THEME, height=280)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">Ürün Dağılımı</div>', unsafe_allow_html=True)
        cluster_counts = filtered["cluster_label"].value_counts()
        fig2 = go.Figure(go.Pie(labels=cluster_counts.index, values=cluster_counts.values, hole=0.65,
            marker=dict(colors=["#4ade80", "#60a5fa", "#f87171"]), textinfo="percent", textfont=dict(size=11, color="#ccc")))
        fig2.update_layout(**PLOTLY_THEME, height=280, showlegend=True, legend=dict(font=dict(color="#666", size=10)))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">En Yüksek Skorlu Ürünler</div>', unsafe_allow_html=True)
    cols_needed = ["name", "category", "discounted_price", "rating", "performance_score", "cluster_label", "discount_verdict"]
    top = filtered[cols_needed].sort_values("performance_score", ascending=False).head(10).rename(columns={
        "name": "Ürün", "category": "Kategori", "discounted_price": "Fiyat (₺)",
        "rating": "Puan", "performance_score": "Skor", "cluster_label": "Etiket", "discount_verdict": "İndirim"
    })
    st.dataframe(top, use_container_width=True, hide_index=True)

# ── ÜRÜN DETAY ─────────────────────────────────────────────────────────────────
elif page == "🔍  Ürün Detay":
    st.markdown('<div class="page-title">Ürün Detay Analizi</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Ürün bazlı fiyat geçmişi ve yorum sentiment analizi</div>', unsafe_allow_html=True)

    all_names = filtered["name"].tolist()
    all_pids  = filtered["product_id"].tolist()
    chosen_name = st.selectbox("🔍 Ürün seç veya ara",
        [None] + all_names,
        format_func=lambda x: "— Ürün giriniz —" if x is None else x,
        key="prod_select")
    selected_pid = all_pids[all_names.index(chosen_name)] if chosen_name else None

    if selected_pid:
        prod = filtered[filtered["product_id"] == selected_pid].iloc[0]

        col1, col2, col3, col4 = st.columns(4)
        with col1: metric_card("Fiyat", f"₺{prod['discounted_price']:,.0f}", "orange")
        with col2: metric_card("Puan", f"{prod['rating']} ⭐", "yellow")
        with col3: metric_card("Performans Skoru", f"{prod['performance_score']}", "green")
        with col4: metric_card("Etiket", prod['cluster_label'], "blue")

        st.markdown("<hr>", unsafe_allow_html=True)
        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown('<div class="section-title">📈 12 Aylık Fiyat Geçmişi</div>', unsafe_allow_html=True)
            ph = price_history(prices_df, selected_pid)
            fig = go.Figure(go.Scatter(
                x=ph["month"], y=ph["price"], mode="lines+markers",
                line=dict(color="#ff6b35", width=2), marker=dict(size=6, color="#ff6b35"),
                fill="tozeroy", fillcolor="rgba(255,107,53,0.08)"
            ))
            fig.update_layout(**PLOTLY_THEME, height=280)
            fig.update_xaxes(tickvals=list(range(1, 13)), ticktext=["Oca","Şub","Mar","Nis","May","Haz","Tem","Ağu","Eyl","Eki","Kas","Ara"])
            st.plotly_chart(fig, use_container_width=True)

        with col_r:
            st.markdown('<div class="section-title">💬 Yorum Sentiment Analizi</div>', unsafe_allow_html=True)
            sentiment_counts, total_reviews = product_sentiment_summary(reviews_df, selected_pid)
            metric_card("Toplam Yorum", f"{total_reviews}", "orange")

            if total_reviews > 0:
                pos = sentiment_counts["Pozitif"]
                neg = sentiment_counts["Negatif"]
                neu = sentiment_counts["Nötr"]
                pos_pct = pos / total_reviews * 100
                neg_pct = neg / total_reviews * 100
                neu_pct = neu / total_reviews * 100

                fig2 = go.Figure(go.Bar(
                    x=[pos_pct, neu_pct, neg_pct],
                    y=["😊 Pozitif", "😐 Nötr", "😞 Negatif"],
                    orientation="h",
                    marker=dict(color=["#4ade80", "#60a5fa", "#f87171"]),
                    text=[f"%{pos_pct:.0f} ({pos})", f"%{neu_pct:.0f} ({neu})", f"%{neg_pct:.0f} ({neg})"],
                    textposition="inside",
                ))
                fig2.update_layout(**PLOTLY_THEME, height=200)
                fig2.update_xaxes(range=[0, 100])
                st.plotly_chart(fig2, use_container_width=True)

                if pos_pct >= 60:
                    verdict, color, tc = "🟢 Müşteriler genel olarak memnun", "#052e16", "#4ade80"
                elif neg_pct >= 40:
                    verdict, color, tc = "🔴 Dikkat: Yüksek negatif yorum oranı", "#1c0505", "#f87171"
                else:
                    verdict, color, tc = "🟡 Karışık yorumlar", "#1c1100", "#facc15"
                st.markdown(f'<div style="background:{color};border-radius:8px;padding:0.8rem 1.2rem;margin-top:0.5rem;color:{tc};font-weight:600;font-size:0.9rem;">{verdict}</div>', unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">💰 İndirim Analizi</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1: metric_card("İddia Edilen İndirim", f"%{prod['claimed_discount_rate']*100:.0f}", "orange")
        with col2: metric_card("Gerçek İndirim", f"%{prod['real_discount_rate']*100:.0f}", "green")
        with col3: metric_card("Sonuç", prod['discount_verdict'], "blue")

# ── İNDİRİM DOĞRULAMA ─────────────────────────────────────────────────────────
elif page == "💰  İndirim Doğrulama":
    st.markdown('<div class="page-title">İndirim Doğrulama</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Gerçek ve yanıltıcı indirimleri karşılaştır</div>', unsafe_allow_html=True)

    # Genel istatistikler
    real = filtered[~filtered["is_fake_discount"]]
    fake = filtered[filtered["is_fake_discount"]]
    col1, col2, col3 = st.columns(3)
    with col1: metric_card("Yanıltıcı İndirim", f"{len(fake)}", "orange")
    with col2: metric_card("Gerçek İndirim", f"{len(real)}", "green")
    with col3: metric_card("Ort. İndirim Farkı", f"%{filtered['discount_gap'].mean()*100:.1f}", "blue")

    st.markdown("<hr>", unsafe_allow_html=True)

    # Ürün bazlı arama
    st.markdown('<div class="section-title">🔍 Ürün Bazlı İndirim Sorgula</div>', unsafe_allow_html=True)
    disc_names = filtered["name"].tolist()
    disc_pids  = filtered["product_id"].tolist()
    disc_chosen = st.selectbox("🔍 Ürün seç veya ara", [None] + disc_names,
        format_func=lambda x: "— Ürün giriniz —" if x is None else x, key="disc_select")
    selected_d = disc_pids[disc_names.index(disc_chosen)] if disc_chosen else None

    if selected_d:
        prod_d = filtered[filtered["product_id"] == selected_d].iloc[0]
        col1, col2, col3, col4 = st.columns(4)
        with col1: metric_card("Şişirilmiş Fiyat", f"₺{prod_d['inflated_price']:,.0f}", "orange")
        with col2: metric_card("İndirimli Fiyat", f"₺{prod_d['discounted_price']:,.0f}", "green")
        with col3: metric_card("İddia Edilen", f"%{prod_d['claimed_discount_rate']*100:.0f}", "blue")
        with col4: metric_card("Gerçek İndirim", f"%{prod_d['real_discount_rate']*100:.0f}", "green")
        gap = prod_d['discount_gap'] * 100
        if prod_d['is_fake_discount']:
            st.markdown(f'<div style="background:#1c0505;border-radius:8px;padding:1rem 1.4rem;color:#f87171;font-weight:600;">❌ Yanıltıcı İndirim — İddia edilen ile gerçek arasında %{gap:.1f} fark var!</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background:#052e16;border-radius:8px;padding:1rem 1.4rem;color:#4ade80;font-weight:600;">✅ Gerçek İndirim — Sadece %{gap:.1f} fark mevcut.</div>', unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

    # Genel grafikler
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-title">İddia Edilen vs Gerçek İndirim</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=filtered["claimed_discount_rate"]*100, y=filtered["real_discount_rate"]*100,
            mode="markers",
            marker=dict(color=filtered["is_fake_discount"].map({True:"#f87171",False:"#4ade80"}), size=6, opacity=0.7),
            text=filtered["name"],
        ))
        fig.add_shape(type="line", x0=0, y0=0, x1=60, y1=60, line=dict(color="#444", dash="dash", width=1))
        fig.update_layout(**PLOTLY_THEME, height=320, xaxis_title="İddia Edilen (%)", yaxis_title="Gerçek (%)")
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">Kategoriye Göre Yanıltıcı İndirim Oranı</div>', unsafe_allow_html=True)
        fake_rate = filtered.groupby("category")["is_fake_discount"].mean().reset_index()
        fake_rate.columns = ["category", "fake_rate"]
        fake_rate = fake_rate.sort_values("fake_rate")
        fig2 = go.Figure(go.Bar(x=fake_rate["fake_rate"]*100, y=fake_rate["category"], orientation="h", marker=dict(color="#f87171", opacity=0.8)))
        fig2.update_layout(**PLOTLY_THEME, height=320, xaxis_title="Yanıltıcı İndirim Oranı (%)")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">İndirim Detay Tablosu</div>', unsafe_allow_html=True)
    show_df = filtered[["name","category","inflated_price","discounted_price","claimed_discount_rate","real_discount_rate","discount_gap","discount_verdict"]].copy()
    show_df["claimed_discount_rate"] = (show_df["claimed_discount_rate"]*100).round(1).astype(str)+"%"
    show_df["real_discount_rate"] = (show_df["real_discount_rate"]*100).round(1).astype(str)+"%"
    show_df["discount_gap"] = (show_df["discount_gap"]*100).round(1).astype(str)+"%"
    show_df = show_df.rename(columns={"name":"Ürün","category":"Kategori","inflated_price":"Şişirilmiş (₺)","discounted_price":"İndirimli (₺)","claimed_discount_rate":"İddia","real_discount_rate":"Gerçek","discount_gap":"Fark","discount_verdict":"Sonuç"})
    st.dataframe(show_df, use_container_width=True, hide_index=True)

# ── SATICI GÜVEN ───────────────────────────────────────────────────────────────
elif page == "🏪  Satıcı Güven":
    st.markdown('<div class="page-title">Satıcı Güven Analizi</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Satıcı puanları ve müşteri memnuniyeti</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1: metric_card("Güvenilir Satıcı", f"{(seller_df['trust_label']=='🟢 Güvenilir').sum()}", "green")
    with col2: metric_card("Orta Satıcı", f"{(seller_df['trust_label']=='🟡 Orta').sum()}", "orange")
    with col3: metric_card("Riskli Satıcı", f"{(seller_df['trust_label']=='🔴 Riskli').sum()}", "blue")

    st.markdown("<hr>", unsafe_allow_html=True)

    # Satıcı arama
    st.markdown('<div class="section-title">🔍 Satıcı Bazlı Analiz</div>', unsafe_allow_html=True)
    s_names = seller_df["name"].tolist()
    s_ids   = seller_df["seller_id"].tolist()
    s_chosen = st.selectbox("🔍 Satıcı seç veya ara", [None] + s_names,
        format_func=lambda x: "— Satıcı giriniz —" if x is None else x, key="seller_select")
    selected_s = s_ids[s_names.index(s_chosen)] if s_chosen else None

    if selected_s:
        s = seller_df[seller_df["seller_id"] == selected_s].iloc[0]
        s = seller_df[seller_df["seller_id"] == selected_s].iloc[0]

        col1, col2, col3, col4 = st.columns(4)
        with col1: metric_card("Satıcı Puanı", f"{s['rating']} ⭐", "yellow")
        with col2: metric_card("Toplam Satış", f"{s['total_sales']:,}", "orange")
        with col3: metric_card("Pozitif Yorum", f"%{s['positive_rate']:.1f}", "green")
        with col4: metric_card("Güven Skoru", f"{s['trust_score']}", "blue")

        # Satıcının ürünleri
        seller_products = filtered[filtered["seller_id"] == selected_s]
        if len(seller_products) > 0:
            st.markdown(f'<div class="section-title">Bu Satıcının Ürünleri ({len(seller_products)} adet)</div>', unsafe_allow_html=True)
            show_sp = seller_products[["name","category","discounted_price","rating","performance_score","cluster_label","discount_verdict"]].rename(columns={
                "name":"Ürün","category":"Kategori","discounted_price":"Fiyat (₺)","rating":"Puan","performance_score":"Skor","cluster_label":"Etiket","discount_verdict":"İndirim"
            })
            st.dataframe(show_sp, use_container_width=True, hide_index=True)

        # Güven etiketi
        if s['trust_label'] == "🟢 Güvenilir":
            st.markdown(f'<div style="background:#052e16;border-radius:8px;padding:1rem 1.4rem;color:#4ade80;font-weight:600;">{s["trust_label"]} — Bu satıcı yüksek puan ve pozitif yorum oranına sahip.</div>', unsafe_allow_html=True)
        elif s['trust_label'] == "🟡 Orta":
            st.markdown(f'<div style="background:#1c1100;border-radius:8px;padding:1rem 1.4rem;color:#facc15;font-weight:600;">{s["trust_label"]} — Dikkatli olun, karışık performans.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background:#1c0505;border-radius:8px;padding:1rem 1.4rem;color:#f87171;font-weight:600;">{s["trust_label"]} — Bu satıcıyla işlem yapmadan önce dikkatli değerlendirin.</div>', unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

    # Genel grafikler
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-title">Puan vs Pozitif Yorum Oranı</div>', unsafe_allow_html=True)
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
                hovertemplate="<b>%{customdata[0]}</b><br>Puan: %{x}<br>Pozitif Yorum: %{y:.1f}%<br>Güven Skoru: %{customdata[1]}<extra></extra>"
            ))
        fig.update_layout(**PLOTLY_THEME, height=340,
            xaxis_title="Satıcı Puanı", yaxis_title="Pozitif Yorum (%)",
            legend=dict(font=dict(color="#888", size=10), bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">Top 10 Satıcı — Güven Skoru</div>', unsafe_allow_html=True)
        top_sellers = seller_df.sort_values("trust_score", ascending=True).tail(10)
        fig2 = go.Figure(go.Bar(x=top_sellers["trust_score"], y=top_sellers["name"], orientation="h", marker=dict(color="#4ade80", opacity=0.8)))
        fig2.update_layout(**PLOTLY_THEME, height=340, xaxis_title="Güven Skoru")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">Satıcı Tablosu</div>', unsafe_allow_html=True)
    show_sellers = seller_df[["name","rating","total_sales","positive_rate","trust_score","trust_label"]].rename(columns={
        "name":"Satıcı","rating":"Puan","total_sales":"Toplam Satış","positive_rate":"Pozitif Yorum (%)","trust_score":"Güven Skoru","trust_label":"Etiket"})
    show_sellers = show_sellers.copy()
    show_sellers["Pozitif Yorum (%)"] = show_sellers["Pozitif Yorum (%)"].round(1)
    st.dataframe(show_sellers, use_container_width=True, hide_index=True)

# ── KATEGORİ ──────────────────────────────────────────────────────────────────
elif page == "📈  Kategori İstatistikleri":
    st.markdown('<div class="page-title">Kategori İstatistikleri</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Kategori bazlı piyasa analizi</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1: metric_card("Kategori Sayısı", f"{len(cat_df)}", "orange")
    with col2: metric_card("En İyi Puanlı", cat_df.loc[cat_df["avg_rating"].idxmax(),"category"], "green")
    with col3: metric_card("En Uygun Fiyatlı", cat_df.loc[cat_df["avg_price"].idxmin(),"category"], "blue")

    st.markdown("<hr>", unsafe_allow_html=True)
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-title">Kategori Ortalama Fiyatları</div>', unsafe_allow_html=True)
        fig = go.Figure(go.Bar(x=cat_df["category"], y=cat_df["avg_price"], marker=dict(color="#ff6b35", opacity=0.85),
            error_y=dict(type="data", array=cat_df["std_price"], color="#333", thickness=1.5)))
        fig.update_layout(**PLOTLY_THEME, height=320, xaxis_tickangle=-30, yaxis_title="Ort. Fiyat (₺)")
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">Kategori Ortalama Puanları</div>', unsafe_allow_html=True)
        fig2 = go.Figure(go.Bar(x=cat_df["category"], y=cat_df["avg_rating"], marker=dict(color="#60a5fa", opacity=0.85)))
        fig2.update_layout(**PLOTLY_THEME, height=320, xaxis_tickangle=-30, yaxis_title="Ort. Puan", yaxis_range=[0,5])
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">Kategori Özet Tablosu</div>', unsafe_allow_html=True)
    show_cat = cat_df.rename(columns={"category":"Kategori","avg_price":"Ort. Fiyat (₺)","median_price":"Medyan Fiyat (₺)","std_price":"Std. Sapma","avg_rating":"Ort. Puan","product_count":"Ürün Sayısı"})
    st.dataframe(show_cat, use_container_width=True, hide_index=True)
