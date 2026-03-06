import streamlit as st
import yfinance as yf
import pandas as pd

# 1. إعدادات الواجهة والألوان (Neon Green & Black)
st.set_page_config(page_title="Lynch Neon Pro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; }
    .stApp { background-color: #000000; color: #39FF14; }
    h1, h2, h3 { color: #39FF14 !important; font-family: 'Courier New', Courier, monospace; text-shadow: 0 0 10px #39FF14; }
    .stTextInput>div>div>input { background-color: #111; color: #39FF14; border: 1px solid #39FF14; }
    .stButton>button { background-color: #000; color: #39FF14; border: 2px solid #39FF14; width: 100%; border-radius: 10px; transition: 0.3s; }
    .stButton>button:hover { background-color: #39FF14; color: #000; box-shadow: 0 0 20px #39FF14; }
    .metric-card { background-color: #111; border: 1px solid #333; padding: 20px; border-radius: 15px; margin-bottom: 20px; border-left: 5px solid #39FF14; }
    .metric-title { font-size: 1.2rem; font-weight: bold; color: #39FF14; }
    .metric-value { font-size: 2rem; color: #ffffff; }
    .explanation { font-size: 0.9rem; color: #888; margin-top: 10px; border-top: 1px solid #222; padding-top: 10px; }
    .goal { color: #39FF14; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ نظام تحليل بيتر لينش المتطور")
st.write("---")

# 2. إدخال البيانات
col_input, col_info = st.columns([1, 2])
with col_input:
    ticker_raw = st.text_input("أدخل رمز السهم (مثال: 7010)", value="7010")
    ticker = f"{ticker_raw}.SR" if (ticker_raw.isdigit() and len(ticker_raw) == 4) else ticker_raw
    analyze_btn = st.button("تفعيل فحص النمو 🚀")

# 3. منطق التحليل المالي
if analyze_btn:
    try:
        with st.spinner('📡 جاري سحب البيانات من السحابة المالية...'):
            stock = yf.Ticker(ticker)
            income = stock.financials
            balance = stock.balance_sheet
            cf = stock.cashflow
            info = stock.info

            def get_f(df, label): return df.loc[label].iloc[0] if (df is not None and label in df.index) else 0

            # الحسابات
            eps_g = (income.loc['Net Income'].pct_change(periods=-1).dropna().mean() * 100) if 'Net Income' in income.index else 0
            pe = info.get('trailingPE') or (info.get('currentPrice', 1) / info.get('trailingEps', 1))
            peg = pe / eps_g if eps_g > 0 else 0
            debt = get_f(balance, 'Total Debt')
            equity = get_f(balance, 'Stockholders Equity')
            de_ratio = (debt / equity * 100) if equity != 0 else 0
            net_cash = get_f(balance, 'Cash And Cash Equivalents') - debt
            inv_g = (balance.loc['Inventory'].pct_change(periods=-1).iloc[0] * 100) if 'Inventory' in balance.index else 0
            rev_g = (income.loc['Total Revenue'].pct_change(periods=-1).iloc[0] * 100) if 'Total Revenue' in income.index else 0
            fcf_r = (get_f(cf, 'Free Cash Flow') / get_f(income, 'Net Income')) if get_f(income, 'Net Income') != 0 else 0

            # 4. عرض البطاقات المتطورة
            st.subheader(f"📊 تقرير السهم: {ticker}")
            
            metrics = [
                ("نسبة PEG", f"{peg:.2f}", "P/E ÷ معدل النمو", "أقل من 1.0 (والأفضل < 0.5)", "تحدد ما إذا كنت تشتري النمو بسعر عادل أو متضخم."),
                ("نمو الأرباح (EPS)", f"{eps_g:.1f}%", "متوسط نمو صافي الربح", "بين 20% و 25% (تجنب > 50%)", "الوقود المحرك لأسعار الأسهم على المدى الطويل."),
                ("الديون / الملكية", f"{de_ratio:.1f}%", "إجمالي الدين ÷ حقوق المساهمين", "أقل من 35% لشركات النمو", "تضمن عدم إفلاس الشركة في حال تعثر الاقتصاد."),
                ("النقد الصافي", f"{net_cash:,.0f}", "الكاش - إجمالي الديون", "قيمة موجبة (Net Cash Pos)", "يعمل كوسادة أمان ويقلل تكلفة السهم الفعلية."),
                ("كفاءة المخزون", "سليم ✅" if inv_g < rev_g else "خطر ❌", "نمو المخزون vs نمو المبيعات", "نمو المخزون < نمو المبيعات", "تراكم المخزون أسرع من البيع يعني ضعف الطلب."),
                ("جودة الأرباح (FCF)", f"{fcf_r:.2f}", "التدفق النقدي الحر ÷ الربح", "أكبر من 1.0", "تؤكد أن الأرباح 'كاش حقيقي' وليست مجرد محاسبة.")
            ]

            # توزيع البطاقات في 3 أعمدة
            cols = st.columns(3)
            for i, (title, val, calc, target, desc) in enumerate(metrics):
                with cols[i % 3]:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-title">{title}</div>
                            <div class="metric-value">{val}</div>
                            <div class="explanation">
                                🧪 <b>الحساب:</b> {calc}<br>
                                🎯 <span class="goal">المستهدف:</span> {target}<br>
                                📖 <b>شرح:</b> {desc}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"⚠️ خطأ تقني: تأكد من أن السهم لديه قوائم مالية مكتملة.")

st.sidebar.markdown("### 🧬 فلسفة بيتر لينش\nاستثمر فيما تفهمه، وابحث عن 'الأحجار الكريمة' قبل أن تكتشفها المؤسسات الكبرى.")
