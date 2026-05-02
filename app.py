import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from analysis import (
    load_data, preprocess, calculate_performance_score,
    verify_discount, seller_trust_analysis, category_statistics, price_history
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TrendAnalyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0d0d0d;
    color: #e8e8e8;
}

/* Hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 2rem 2rem; max-width: 100%; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #111111;
    border-right: 1px solid #1e1e1e;
}
[data-testid="stSidebar"] .stRadio label {
    font-family: 'DM Sans', sans-serif;
    color: #888;
    font-size: 0.85rem;
    padding: 6px 0;
    transition: color 0.2s;
}
[data-testid="stSidebar"] .stRadio label:hover { color: #ff6b35; }

/* Metric cards */
.metric-card {
    background: #161616;
    border: 1px solid #222;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.5rem;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: #333; }
.metric-label {
    font-size: 0.72rem;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.3rem;
    font-family: 'DM Sans', sans-serif;
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #ff6b35;
    line-height: 1;
}
.metric-value.green { color: #4ade80; }
.metric-value.blue { color: #60a5fa; }
.metric-value.orange { color: #ff6b35; }

/* Section headers */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #e8e8e8;
    margin: 1.5rem 0 0.8rem 0;
    letter-spacing: -0.01em;
}

/* Page title */
.page-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.03em;
    margin-bottom: 0.2rem;
}
.page-subtitle {
    font-size: 0.82rem;
    color: #555;
    margin-bottom: 1.5rem;
}

/* Plotly dark override */
.stPlotlyChart { background: transparent !important; }

/* Dataframe */
[data-testid="stDataFrame"] { border: 1px solid #1e1e1e; border-radius: 10px; }

/* Select / filter boxes */
.stSelectbox > div > div, .stMultiSelect > div > div {
    background: #161616 !important;
    border: 1px solid #222 !important;
    border-radius: 8px !important;
    color: #e8e8e8 !important;
}

/* Badge */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
}
.badge-green { background: #052e16; color: #4ade80; }
.badge-orange { background: #1c1100; color: #fb923c; }
.badge-red { background: #1c0505; color: #f87171; }

/* Divider */
hr { border-color: #1e1e1e; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#888", size=11),
    xaxis=dict(gridcolor="#1a1a1a", linecolor="#1a1a1a", tickcolor="#333"),
    yaxis=dict(gridcolor="#1a1a1a", linecolor="#1a1a1a", tickcolor="#333"),
    margin=dict(l=10, r=10, t=30, b=10),
)

# ── Load & process data ───────────────────────────────────────────────────────
@st.cache_data
def get_data():
    products, sellers, reviews, prices = load_data()
    products, sellers = preprocess(products, sellers)
    scored = calculate_performance_score(products, sellers)
    discounted = verify_discount(scored)
    seller_trust = seller_trust_analysis(sellers, reviews)
    cat_stats = category_statistics(products)
    return discounted, seller_trust, cat_stats, prices

df, seller_df, cat_df, prices_df = get_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 1rem 0 1.5rem 0;">
        <div style="font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800;color:#ff6b35;">
            📊 TrendAnalyzer
        </div>
        <div style="font-size:0.72rem;color:#444;margin-top:2px;">Trendyol Ürün Analizi</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigasyon",
        ["🏠  Dashboard", "🔍  Ürün Analizi", "💰  İndirim Doğrulama", "🏪  Satıcı Güven", "📈  Kategori İstatistikleri"],
        label_visibility="collapsed"
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    # Filters
    st.markdown("<div style='font-size:0.72rem;color:#444;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;'>Filtreler</div>", unsafe_allow_html=True)
    selected_cats = st.multiselect(
        "Kategori",
        options=sorted(df["category"].unique()),
        default=[],
        placeholder="Tümü"
    )
    price_range = st.slider("Fiyat Aralığı (₺)", 0, int(df["discounted_price"].max()), (0, int(df["discounted_price"].max())))

    filtered = df.copy()
    if selected_cats:
        filtered = filtered[filtered["category"].isin(selected_cats)]
    filtered = filtered[(filtered["discounted_price"] >= price_range[0]) & (filtered["discounted_price"] <= price_range[1])]

    st.markdown(f"<div style='font-size:0.75rem;color:#555;margin-top:8px;'>{len(filtered)} ürün gösteriliyor</div>", unsafe_allow_html=True)

# ── Helper: metric card ───────────────────────────────────────────────────────
def metric_card(label, value, color="orange"):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value {color}">{value}</div>
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ════════════════════════════════════════════════════════════════════════════════
if page == "🏠  Dashboard":
    st.markdown('<div class="page-title">Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Genel pazar özeti — tüm kategoriler</div>', unsafe_allow_html=True)

    # KPI row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Toplam Ürün", f"{len(filtered):,}", "orange")
    with col2:
        best_buy_count = (filtered["cluster_label"] == "🏆 Best Buy").sum()
        metric_card("Best Buy Ürün", f"{best_buy_count}", "green")
    with col3:
        fake_pct = filtered["is_fake_discount"].mean() * 100
        metric_card("Yanıltıcı İndirim", f"%{fake_pct:.0f}", "blue")
    with col4:
        avg_score = filtered["performance_score"].mean()
        metric_card("Ort. Performans Skoru", f"{avg_score:.1f}", "orange")

    st.markdown("<hr>", unsafe_allow_html=True)

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown('<div class="section-title">Kategori Başına Ortalama Fiyat</div>', unsafe_allow_html=True)
        cat_price = filtered.groupby("category")["discounted_price"].mean().reset_index().sort_values("discounted_price", ascending=True)
        fig = go.Figure(go.Bar(
            x=cat_price["discounted_price"],
            y=cat_price["category"],
            orientation="h",
            marker=dict(color="#ff6b35", opacity=0.85),
        ))
        fig.update_layout(**PLOTLY_THEME, height=280)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown('<div class="section-title">Ürün Dağılımı</div>', unsafe_allow_html=True)
        cluster_counts = filtered["cluster_label"].value_counts()
        fig2 = go.Figure(go.Pie(
            labels=cluster_counts.index,
            values=cluster_counts.values,
            hole=0.65,
            marker=dict(colors=["#4ade80", "#60a5fa", "#f87171"]),
            textinfo="percent",
            textfont=dict(size=11, color="#ccc"),
        ))
        fig2.update_layout(**PLOTLY_THEME, height=280, showlegend=True,
                           legend=dict(font=dict(color="#666", size=10)))
        st.plotly_chart(fig2, use_container_width=True)

    # Top products table
    st.markdown('<div class="section-title">En Yüksek Skorlu Ürünler</div>', unsafe_allow_html=True)
    top = filtered.sort_values("performance_score", ascending=False).head(10)[[
        "name", "category", "discounted_price", "rating", "performance_score", "cluster_label", "discount_verdict"
    ]].rename(columns={
        "name": "Ürün", "category": "Kategori", "discounted_price": "Fiyat (₺)",
        "rating": "Puan", "performance_score": "Skor", "cluster_label": "Etiket", "discount_verdict": "İndirim"
    })
    st.dataframe(top, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════════════════════
# PAGE: ÜRÜN ANALİZİ
# ════════════════════════════════════════════════════════════════════════════════
elif page == "🔍  Ürün Analizi":
    st.markdown('<div class="page-title">Ürün Analizi</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Fiyat-performans skoru ve kümeleme</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Ort. Puan", f"{filtered['rating'].mean():.2f} ⭐", "orange")
    with col2:
        metric_card("Ort. Skor", f"{filtered['performance_score'].mean():.1f}", "green")
    with col3:
        metric_card("Ort. Fiyat", f"₺{filtered['discounted_price'].mean():,.0f}", "blue")

    st.markdown("<hr>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-title">Fiyat vs Performans Skoru</div>', unsafe_allow_html=True)
        fig = px.scatter(
            filtered, x="discounted_price", y="performance_score",
            color="cluster_label", size="review_count",
            color_discrete_map={"🏆 Best Buy": "#4ade80", "✅ Fair Value": "#60a5fa", "⚠️ Overpriced": "#f87171"},
            hover_data=["name", "category", "rating"],
        )
        fig.update_layout(**PLOTLY_THEME, height=320)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">Performans Skoru Dağılımı</div>', unsafe_allow_html=True)
        fig2 = go.Figure(go.Histogram(
            x=filtered["performance_score"],
            nbinsx=20,
            marker_color="#ff6b35",
            opacity=0.8,
        ))
        fig2.update_layout(**PLOTLY_THEME, height=320)
        st.plotly_chart(fig2, use_container_width=True)

    # Fiyat geçmişi
    st.markdown('<div class="section-title">Ürün Fiyat Geçmişi</div>', unsafe_allow_html=True)
    product_options = filtered["product_id"].tolist()
    product_names = filtered.set_index("product_id")["name"].to_dict()
    selected_pid = st.selectbox("Ürün seçin", product_options, format_func=lambda x: product_names.get(x, x))
    ph = price_history(prices_df, selected_pid)
    fig3 = go.Figure(go.Scatter(
        x=ph["month"], y=ph["price"],
        mode="lines+markers",
        line=dict(color="#ff6b35", width=2),
        marker=dict(size=6, color="#ff6b35"),
        fill="tozeroy",
        fillcolor="rgba(255,107,53,0.08)"
    ))
    fig3.update_layout(**PLOTLY_THEME, height=260,
                       xaxis=dict(tickvals=list(range(1, 13)),
                                  ticktext=["Oca","Şub","Mar","Nis","May","Haz","Tem","Ağu","Eyl","Eki","Kas","Ara"]))
    st.plotly_chart(fig3, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════════
# PAGE: İNDİRİM DOĞRULAMA
# ════════════════════════════════════════════════════════════════════════════════
elif page == "💰  İndirim Doğrulama":
    st.markdown('<div class="page-title">İndirim Doğrulama</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Gerçek ve yanıltıcı indirimleri karşılaştır</div>', unsafe_allow_html=True)

    real = filtered[~filtered["is_fake_discount"]]
    fake = filtered[filtered["is_fake_discount"]]

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Yanıltıcı İndirim", f"{len(fake)}", "orange")
    with col2:
        metric_card("Gerçek İndirim", f"{len(real)}", "green")
    with col3:
        avg_gap = filtered["discount_gap"].mean() * 100
        metric_card("Ort. İndirim Farkı", f"%{avg_gap:.1f}", "blue")

    st.markdown("<hr>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-title">İddia Edilen vs Gerçek İndirim</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=filtered["claimed_discount_rate"] * 100,
            y=filtered["real_discount_rate"] * 100,
            mode="markers",
            marker=dict(
                color=filtered["is_fake_discount"].map({True: "#f87171", False: "#4ade80"}),
                size=6, opacity=0.7
            ),
            text=filtered["name"],
        ))
        fig.add_shape(type="line", x0=0, y0=0, x1=60, y1=60,
                      line=dict(color="#444", dash="dash", width=1))
        fig.update_layout(**PLOTLY_THEME, height=320,
                          xaxis_title="İddia Edilen İndirim (%)",
                          yaxis_title="Gerçek İndirim (%)")
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">Kategoriye Göre Yanıltıcı İndirim Oranı</div>', unsafe_allow_html=True)
        fake_rate = filtered.groupby("category")["is_fake_discount"].mean().reset_index()
        fake_rate.columns = ["category", "fake_rate"]
        fake_rate = fake_rate.sort_values("fake_rate", ascending=True)
        fig2 = go.Figure(go.Bar(
            x=fake_rate["fake_rate"] * 100,
            y=fake_rate["category"],
            orientation="h",
            marker=dict(color="#f87171", opacity=0.8),
        ))
        fig2.update_layout(**PLOTLY_THEME, height=320, xaxis_title="Yanıltıcı İndirim Oranı (%)")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">İndirim Detay Tablosu</div>', unsafe_allow_html=True)
    show_df = filtered[[
        "name", "category", "inflated_price", "discounted_price",
        "claimed_discount_rate", "real_discount_rate", "discount_gap", "discount_verdict"
    ]].copy()
    show_df["claimed_discount_rate"] = (show_df["claimed_discount_rate"] * 100).round(1).astype(str) + "%"
    show_df["real_discount_rate"] = (show_df["real_discount_rate"] * 100).round(1).astype(str) + "%"
    show_df["discount_gap"] = (show_df["discount_gap"] * 100).round(1).astype(str) + "%"
    show_df = show_df.rename(columns={
        "name": "Ürün", "category": "Kategori", "inflated_price": "Şişirilmiş Fiyat (₺)",
        "discounted_price": "İndirimli Fiyat (₺)", "claimed_discount_rate": "İddia",
        "real_discount_rate": "Gerçek", "discount_gap": "Fark", "discount_verdict": "Sonuç"
    })
    st.dataframe(show_df, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════════════════════
# PAGE: SATICI GÜVEN
# ════════════════════════════════════════════════════════════════════════════════
elif page == "🏪  Satıcı Güven":
    st.markdown('<div class="page-title">Satıcı Güven Analizi</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Satıcı puanları ve müşteri memnuniyeti</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Güvenilir Satıcı", f"{(seller_df['trust_label']=='🟢 Güvenilir').sum()}", "green")
    with col2:
        metric_card("Orta Satıcı", f"{(seller_df['trust_label']=='🟡 Orta').sum()}", "orange")
    with col3:
        metric_card("Riskli Satıcı", f"{(seller_df['trust_label']=='🔴 Riskli').sum()}", "blue")

    st.markdown("<hr>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-title">Satıcı Güven Skoru Dağılımı</div>', unsafe_allow_html=True)
        fig = px.scatter(
            seller_df, x="rating", y="positive_rate",
            size="total_sales", color="trust_label",
            color_discrete_map={"🟢 Güvenilir": "#4ade80", "🟡 Orta": "#facc15", "🔴 Riskli": "#f87171"},
            hover_data=["name", "trust_score"],
            text="name"
        )
        fig.update_traces(textposition="top center", textfont_size=9)
        fig.update_layout(**PLOTLY_THEME, height=340, xaxis_title="Satıcı Puanı", yaxis_title="Pozitif Yorum Oranı (%)")
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">Top 10 Satıcı — Güven Skoru</div>', unsafe_allow_html=True)
        top_sellers = seller_df.sort_values("trust_score", ascending=True).tail(10)
        fig2 = go.Figure(go.Bar(
            x=top_sellers["trust_score"],
            y=top_sellers["name"],
            orientation="h",
            marker=dict(color="#4ade80", opacity=0.8),
        ))
        fig2.update_layout(**PLOTLY_THEME, height=340, xaxis_title="Güven Skoru")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">Satıcı Tablosu</div>', unsafe_allow_html=True)
    show_sellers = seller_df[["name", "rating", "total_sales", "positive_rate", "trust_score", "trust_label"]].rename(columns={
        "name": "Satıcı", "rating": "Puan", "total_sales": "Toplam Satış",
        "positive_rate": "Pozitif Yorum (%)", "trust_score": "Güven Skoru", "trust_label": "Etiket"
    })
    show_sellers["Pozitif Yorum (%)"] = show_sellers["Pozitif Yorum (%)"].round(1)
    st.dataframe(show_sellers, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════════════════════
# PAGE: KATEGORİ İSTATİSTİKLERİ
# ════════════════════════════════════════════════════════════════════════════════
elif page == "📈  Kategori İstatistikleri":
    st.markdown('<div class="page-title">Kategori İstatistikleri</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Kategori bazlı piyasa analizi</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Kategori Sayısı", f"{len(cat_df)}", "orange")
    with col2:
        best_cat = cat_df.loc[cat_df["avg_rating"].idxmax(), "category"]
        metric_card("En İyi Puanlı Kategori", best_cat, "green")
    with col3:
        cheapest_cat = cat_df.loc[cat_df["avg_price"].idxmin(), "category"]
        metric_card("En Uygun Fiyatlı", cheapest_cat, "blue")

    st.markdown("<hr>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-title">Kategori Ortalama Fiyatları</div>', unsafe_allow_html=True)
        fig = go.Figure(go.Bar(
            x=cat_df["category"],
            y=cat_df["avg_price"],
            marker=dict(color="#ff6b35", opacity=0.85),
            error_y=dict(type="data", array=cat_df["std_price"], color="#333", thickness=1.5)
        ))
        fig.update_layout(**PLOTLY_THEME, height=320, xaxis_tickangle=-30, yaxis_title="Ort. Fiyat (₺)")
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">Kategori Ortalama Puanları</div>', unsafe_allow_html=True)
        fig2 = go.Figure(go.Bar(
            x=cat_df["category"],
            y=cat_df["avg_rating"],
            marker=dict(color="#60a5fa", opacity=0.85),
        ))
        fig2.update_layout(**PLOTLY_THEME, height=320, xaxis_tickangle=-30, yaxis_title="Ort. Puan",
                           yaxis_range=[0, 5])
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">Kategori Özet Tablosu</div>', unsafe_allow_html=True)
    show_cat = cat_df.rename(columns={
        "category": "Kategori", "avg_price": "Ort. Fiyat (₺)", "median_price": "Medyan Fiyat (₺)",
        "std_price": "Std. Sapma", "avg_rating": "Ort. Puan", "product_count": "Ürün Sayısı"
    })
    st.dataframe(show_cat, use_container_width=True, hide_index=True)
