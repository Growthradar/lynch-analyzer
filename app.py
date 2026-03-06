import streamlit as st
import yfinance as yf
import pandas as pd

# 1. إعدادات الواجهة والألوان (ELM Theme: Royal Blue & Sky Blue)
st.set_page_config(page_title="Lynch ELM Edition", layout="wide")

st.markdown("""
    <style>
    /* ألوان هوية علم */
    :root {
        --elm-dark-blue: #003366;
        --elm-light-blue: #00AEEF;
        --elm-bg: #f4f7f9;
        --card-bg: #ffffff;
    }
    
    .stApp { background-color: var(--elm-bg); color: #333; }
    
    /* العناوين */
    h1, h2, h3 { 
        color: var(--elm-dark-blue) !important; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 700;
        border-bottom: 2px solid var(--elm-light-blue);
        padding-bottom: 10px;
    }

    /* المدخلات والأزرار */
    .stTextInput>div>div>input { border: 2px solid var(--elm-light-blue); border-radius: 8px; }
    .stButton>button { 
        background-color: var(--elm-dark-blue); 
        color: white; 
        border: none; 
        font-weight: bold;
        padding: 12px;
        border-radius: 8px;
        transition: 0.3s;
    }
    .stButton>button:hover { 
        background-color: var(--elm-light-blue); 
        box-shadow: 0 4px 15px rgba(0, 174, 239, 0.3);
    }

    /* تصميم البطاقات (Cards) */
    .metric-card { 
        background-color: var(--card-bg); 
        border: 1px solid #e1e8ed; 
        padding: 25px; 
        border-radius: 12px; 
        margin-bottom: 20px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-top: 6px solid var(--elm-dark-blue);
    }
    .metric-title { font-size: 1.1rem; font-weight: bold; color: var(--elm-dark-blue); margin-bottom: 10px; }
    .metric-value { font-size: 1.8rem; font-weight: 800; color: var(--elm-light-blue); }
    
    .section-box {
        margin-top: 15px;
        padding-top: 10px;
        border-top: 1px solid #eee;
        font-size: 0.85rem;
    }
    .label-blue { color: var(--elm-dark-blue); font-weight: 600; }
    .goal-text { color: #28a745; font-weight: bold; } /* لون النجاح الأخضر الهادئ للمعايير */
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ منصة تحليل بيتر لينش - نسخة ELM التقنية")

# 2. منطقة الإدخال
col_input, _ = st.columns([1, 2])
with col_input:
    ticker_raw = st.text_input("رمز السهم (مثال: 7010 أو AAPL)", value="7010")
    ticker = f"{ticker_raw}.SR" if (ticker_raw.isdigit() and len(ticker_raw) == 4) else ticker_raw
    btn = st.button("تحليل البيانات المالية 🔍")

if btn:
    try:
        with st.spinner('📡 جاري استخراج البيانات من المصادر الموثوقة...'):
            stock = yf.Ticker(ticker)
            # جلب البيانات المالية
            income = stock.financials
            balance = stock.balance_sheet
            cf = stock.cashflow
            info = stock.info

            # دالة استخراج القيم
            def get_f(df, label): return df.loc[label].iloc if (df is not None and label in df.index) else 0

            # الحسابات الدقيقة
            eps_g = (income.loc['Net Income'].pct_change(periods=-1).dropna().mean() * 100) if 'Net Income' in income.index else 0
            pe = info.get('trailingPE') or (info.get('currentPrice', 1) / info.get('trailingEps', 1))
            peg = pe / eps_g if eps_g > 0 else 0
            debt = get_f(balance, 'Total Debt')
            equity = get_f(balance, 'Stockholders Equity')
            de_ratio = (debt / equity * 100) if equity != 0 else 0
            net_cash = get_f(balance, 'Cash And Cash Equivalents') - debt
            inv_g = (balance.loc['Inventory'].pct_change(periods=-1).iloc * 100) if 'Inventory' in balance.index else 0
            rev_g = (income.loc['Total Revenue'].pct_change(periods=-1).iloc * 100) if 'Total Revenue' in income.index else 0
            fcf_r = (get_f(cf, 'Free Cash Flow') / get_f(income, 'Net Income')) if get_f(income, 'Net Income') != 0 else 0

            # 3. عرض النتائج بأسلوب البطاقات المنظمة
            st.subheader(f"📊 تحليل السهم: {ticker}")
            
            metrics = [
                ("نسبة PEG", f"{peg:.2f}", "P/E ÷ معدل النمو", "أقل من 1.0", "تحدد ما إذا كان السعر عادلاً مقابل نمو الأرباح."),
                ("نمو الأرباح (EPS)", f"{eps_g:.1f}%", "متوسط نمو صافي الربح السنوي", "20% - 25% (تجنب > 50%)", "المحرك الأساسي لقيمة السهم في المستقبل."),
                ("الديون / الملكية", f"{de_ratio:.1f}%", "إجمالي الدين ÷ حقوق المساهمين", "أقل من 35%", "مقياس الأمان المالي والقدرة على الصمود."),
                ("النقد الصافي", f"{net_cash:,.0f}", "الكاش - إجمالي الديون", "قيمة موجبة (+)", "وسادة أمان نقدية تقلل المخاطر."),
                ("اختبار المخزون", "سليم ✅" if inv_g < rev_g else "تراكم ⚠️", "نمو المخزون vs المبيعات", "نمو المخزون < المبيعات", "المبيعات تسبق المخزون تدل على طلب قوي."),
                ("جودة الأرباح (FCF)", f"{fcf_r:.2f}", "التدفق النقدي الحر ÷ الربح", "أعلى من 1.0", "تضمن أن الأرباح 'نقد حقيقي' وليست أرقاماً.")
            ]

            cols = st.columns(3)
            for i, (title, val, calc, target, desc) in enumerate(metrics):
                with cols[i % 3]:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-title">{title}</div>
                            <div class="metric-value">{val}</div>
                            <div class="section-box">
                                <span class="label-blue">🧪 المعادلة:</span> {calc}<br>
                                <span class="label-blue">🎯 المستهدف:</span> <span class="goal-text">{target}</span><br>
                                <span class="label-blue">📖 الشرح:</span> {desc}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"حدث خطأ أثناء التحليل: {e}")

st.sidebar.markdown(f"""
### 💡 فلسفة التميز الرقمي
هذه الأداة تجمع بين **الذكاء المالي** و**المعايير التقنية** لضمان دقة اتخاذ القرار الاستثماري.
""")
