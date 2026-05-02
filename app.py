
from __future__ import annotations

import os
import math
from typing import List, Dict, Any, Tuple

from flask import Flask, render_template_string, request, jsonify, send_from_directory
import pandas as pd

# Optional: scikit-learn for TF-IDF similarity
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except Exception:
    TfidfVectorizer = None
    cosine_similarity = None

# Optional: OpenAI response (gated by env var)
USE_OPENAI = bool(os.getenv("OPENAI_API_KEY"))
if USE_OPENAI:
    try:
        from openai import OpenAI
        oai_client = OpenAI()
    except Exception:
        USE_OPENAI = False
        oai_client = None
else:
    oai_client = None

app = Flask(__name__)

# ------------- Data Loading -------------

def load_products() -> pd.DataFrame:
    """
    Load products CSV. Tries common paths:
    - ./products.csv
    - ./data/products.csv
    - ./products_old.csv (fallback columns will be normalized)
    """
    candidates = [
        "products.csv",
        os.path.join("data", "products.csv"),
        "products_old.csv",
    ]
    for p in candidates:
        if os.path.exists(p):
            df = pd.read_csv(p)
            break
    else:
        raise FileNotFoundError("Couldn't find products.csv or data/products.csv or products_old.csv")

    # Normalize expected columns
    expected = ["product_name", "category", "applications", "problems_solved", "key_params", "short_desc", "url"]
    for col in expected:
        if col not in df.columns:
            df[col] = ""

    # Coerce strings and fill NaN
    for c in expected:
        df[c] = df[c].astype(str).fillna("")
    return df[expected]

# Build text for vectorization
def row_to_text(row: pd.Series) -> str:
    fields = ["product_name", "category", "applications", "problems_solved", "key_params", "short_desc"]
    return " | ".join(str(row.get(f, "")) for f in fields)

# Global state
DF: pd.DataFrame = load_products()
PRODUCT_TEXTS: List[str] = [row_to_text(r) for _, r in DF.iterrows()]

VECTORIZER = None
EMBEDDINGS = None

if TfidfVectorizer is not None:
    VECTORIZER = TfidfVectorizer(max_features=2000, ngram_range=(1, 2))
    EMBEDDINGS = VECTORIZER.fit_transform(PRODUCT_TEXTS)
else:
    VECTORIZER = None
    EMBEDDINGS = None

# ------------- Core Search -------------

def search_products(query: str, top_k: int = 5) -> List[Tuple[int, float]]:
    """
    Returns list of (row_index, similarity) sorted by similarity desc.
    If sklearn unavailable or query empty, returns first top_k items with similarity 0.
    """
    query = (query or "").strip()
    if not query:
        return [(i, 0.0) for i in range(min(top_k, len(PRODUCT_TEXTS)))]
    if VECTORIZER is None or EMBEDDINGS is None or cosine_similarity is None:
        return [(i, 0.0) for i in range(min(top_k, len(PRODUCT_TEXTS)))]

    q_vec = VECTORIZER.transform([query])
    sims = cosine_similarity(q_vec, EMBEDDINGS)[0]
    idx_scores = sorted(enumerate(sims), key=lambda x: x[1], reverse=True)[:top_k]
    return idx_scores

def format_product(row: pd.Series, sim: float) -> Dict[str, Any]:
    return {
        "product_name": row["product_name"],
        "category": row["category"],
        "applications": row["applications"],
        "problems_solved": row["problems_solved"],
        "key_params": row["key_params"],
        "short_desc": row["short_desc"],
        "url": row["url"],
        "similarity": round(float(sim), 4),
    }

def generate_answer(question: str, top_items: List[Dict[str, Any]]) -> str:
    """
    If OpenAI is available, ask for a short Turkish answer referencing products.
    Otherwise create a templated answer.
    """
    if USE_OPENAI and oai_client is not None:
        context = "\n\n".join(
            f"- Ürün: {it['product_name']}\n  Kategori: {it['category']}\n  Kullanım: {it['applications']}\n  Çözdüğü Problemler: {it['problems_solved']}\n  Parametreler: {it['key_params']}\n  Açıklama: {it['short_desc']}"
            for it in top_items
        )
        prompt = f"""Aşağıdaki ürün bağlamını ve kullanıcı sorusunu kullanarak Türkçe, kısa ve net bir yanıt üret.
Gerektiğinde en fazla 3 ürün öner ve her ürün için kısa bir gerekçe ver. Link varsa ekle.

Soru: {question}

Ürün Bağlamı:
{context}
"""
        try:
            # Use responses API if available; otherwise fallback to chat.completions
            try:
                resp = oai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Sen Bimaks ürün asistanısın. Kısa, Türkçe ve net konuş."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2,
                )
                return resp.choices[0].message.content
            except Exception:
                # try responses api
                resp = oai_client.responses.create(
                    model="gpt-4o-mini",
                    input=[
                        {"role": "system", "content": "Sen Bimaks ürün asistanısın. Kısa, Türkçe ve net konuş."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2,
                )
                return resp.output_text
        except Exception as e:
            return f"Not: Otomatik yanıt üretici devre dışı. (Hata: {e})"
    # Fallback
    if not top_items:
        return "Bu soruya uygun ürün bulunamadı. Sorguyu daha spesifik hale getirmeyi deneyebilirsin."
    lines = ["Aşağıdaki ürünler soruna en yakın görünüyor:"]
    for it in top_items[:3]:
        part = f"- {it['product_name']} ({it['category']})"
        if it['url']:
            part += f" — {it['url']}"
        lines.append(part)
    return "\n".join(lines)

# ------------- Web UI -------------

INDEX_HTML = r"""
<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Bimaks Ürün Asistanı</title>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 20px; }
    .container { max-width: 960px; margin: 0 auto; }
    .card { border: 1px solid #ddd; border-radius: 12px; padding: 16px; margin-top: 12px; }
    .row { display: flex; gap: 8px; }
    input, button, textarea { padding: 10px; border-radius: 8px; border: 1px solid #ccc; }
    input, textarea { flex: 1; }
    button { cursor: pointer; }
    .muted { color: #666; font-size: 0.9rem; }
    .pill { display: inline-block; padding: 2px 8px; border-radius: 999px; background: #f3f3f3; margin-right: 6px; font-size: 12px; }
    .list { margin-top: 8px; }
    .item { padding: 8px 0; border-bottom: 1px dashed #eee; }
    .sim { font-variant-numeric: tabular-nums; }
    a { text-decoration: none; }
  </style>
</head>
<body>
  <div class="container">
    <h1>🧪 Bimaks Ürün Asistanı</h1>
    <p class="muted">Soru sor veya ürün arat. Ör: <em>"ters osmoz için antiskalant"</em>, <em>"soğutma kulesi korozyon"</em></p>

    <div class="card">
      <div class="row">
        <input id="q" placeholder="Ürün veya problem ara..." />
        <button onclick="doSearch()">Ara</button>
      </div>
      <div class="list" id="results"></div>
    </div>

    <div class="card">
      <div class="row">
        <textarea id="ask" rows="3" placeholder="Sorunu yaz (örn. 'RO membran kireçlenmesi var, ne önerirsiniz?')"></textarea>
        <button onclick="doAsk()">Sor</button>
      </div>
      <div id="answer" class="list"></div>
    </div>

    <p class="muted">Veri kaynağı: products.csv | OpenAI: {{ 'Açık' if use_openai else 'Kapalı' }}</p>
  </div>

<script>
async function doSearch() {
  const q = document.getElementById('q').value.trim();
  const res = await fetch('/api/search', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({q})});
  const data = await res.json();
  const el = document.getElementById('results');
  el.innerHTML = data.products.map(p => `
    <div class="item">
      <div><strong>${p.product_name}</strong> <span class="pill">${p.category}</span> <span class="muted sim">sim=${p.similarity.toFixed(2)}</span></div>
      <div class="muted">${p.short_desc || ''}</div>
      ${p.url ? `<div><a href="${p.url}" target="_blank">Site</a></div>` : ''}
    </div>
  `).join('') || '<div class="muted">Sonuç yok.</div>';
}

async function doAsk() {
  const q = document.getElementById('ask').value.trim();
  const res = await fetch('/api/ask', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({q})});
  const data = await res.json();
  const list = data.products || [];
  document.getElementById('answer').innerHTML = `
    <div class="item"><pre style="white-space:pre-wrap;margin:0">${data.response || ''}</pre></div>
    <div class="item"><strong>İlgili Ürünler</strong></div>
    ${list.map(p => `
      <div class="item">
        <div><strong>${p.product_name}</strong> <span class="pill">${p.category}</span> <span class="muted sim">sim=${p.similarity.toFixed(2)}</span></div>
        <div class="muted">${p.short_desc || ''}</div>
        ${p.url ? `<div><a href="${p.url}" target="_blank">Site</a></div>` : ''}
      </div>
    `).join('') || '<div class="muted">—</div>'}
  `;
}
</script>
</body>
</html>
"""

# ------------- Routes -------------

@app.route("/")
def index():
    return render_template_string(INDEX_HTML, use_openai=USE_OPENAI)

@app.route("/api/search", methods=["POST"])
def api_search():
    payload = request.get_json(force=True, silent=True) or {}
    q = (payload.get("q") or "").strip()
    idx_scores = search_products(q, top_k=10)
    out = [format_product(DF.iloc[i], sim) for i, sim in idx_scores]
    return jsonify({"products": out})

@app.route("/api/ask", methods=["POST"])
def api_ask():
    payload = request.get_json(force=True, silent=True) or {}
    q = (payload.get("q") or "").strip()
    idx_scores = search_products(q, top_k=6)
    prods = [format_product(DF.iloc[i], sim) for i, sim in idx_scores]
    answer = generate_answer(q, prods)
    return jsonify({"response": answer, "products": prods})

if __name__ == "__main__":
    # Flask debug server
    # To run locally:
    #   pip install flask scikit-learn pandas openai
    #   export OPENAI_API_KEY=...   (optional)
    #   python app.py
    app.run(host="0.0.0.0", port=5000, debug=True)
