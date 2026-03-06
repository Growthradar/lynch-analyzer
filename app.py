import streamlit as st
import yfinance as yf
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="محلل بيتر لينش", layout="wide")
st.title("📊 نظام تقييم أسهم النمو - معايير بيتر لينش")

# مدخل السهم
ticker_raw = st.text_input("أدخل رمز السهم (مثال: 7010 أو AAPL)", value="7010")
ticker = f"{ticker_raw}.SR" if (ticker_raw.isdigit() and len(ticker_raw) == 4) else ticker_raw

if st.button("تحليل السهم"):
    try:
        with st.spinner('جاري معالجة البيانات المالية...'):
            stock = yf.Ticker(ticker)
            income = stock.financials
            balance = stock.balance_sheet
            cf = stock.cashflow
            info = stock.info

            # دالة لاستخراج القيم بأمان
            def safe_get(df, label):
                if df is not None and label in df.index:
                    val = df.loc[label]
                    return val.iloc[0] if hasattr(val, 'iloc') else val
                return 0

            # 1. حساب نمو الأرباح (متوسط آخر 3 سنوات)
            net_inc = income.loc['Net Income'] if 'Net Income' in income.index else None
            eps_growth = (net_inc.pct_change(periods=-1).dropna().mean() * 100) if net_inc is not None else 0
            
            # 2. مكرر الربحية والـ PEG
            pe = info.get('trailingPE') or (info.get('currentPrice', 0) / info.get('trailingEps', 1))
            peg = pe / eps_growth if eps_growth > 0 else 0
            
            # 3. الديون وحقوق الملكية
            debt = safe_get(balance, 'Total Debt')
            equity = safe_get(balance, 'Stockholders Equity')
            de_ratio = (debt / equity * 100) if equity != 0 else 0
            
            # 4. النقد الصافي
            cash = safe_get(balance, 'Cash And Cash Equivalents')
            net_cash = cash - debt
            
            # 5. نمو المخزون مقابل المبيعات
            rev_growth = (income.loc['Total Revenue'].pct_change(periods=-1).iloc[0] * 100) if 'Total Revenue' in income.index else 0
            inv_growth = (balance.loc['Inventory'].pct_change(periods=-1).iloc[0] * 100) if 'Inventory' in balance.index else 0
            
            # 6. التدفق النقدي الحر
            fcf = safe_get(cf, 'Free Cash Flow')
            profit = safe_get(income, 'Net Income')
            fcf_ratio = (fcf / profit) if profit != 0 else 0

            # بناء الجدول التوضيحي
            results = [
                {
                    "المؤشر المالي": "نسبة PEG",
                    "القيمة الحالية": f"{peg:.2f}",
                    "طريقة الحساب": "P/E ÷ معدل النمو سنوي",
                    "معيار لينش": "أقل من 1.0 (عادل) / 0.5 (لقطة)",
                    "حالة السهم": "ممتاز ✅" if 0 < peg < 1 else "متضخم ❌"
                },
                {
                    "المؤشر المالي": "نمو الأرباح (EPS)",
                    "القيمة الحالية": f"{eps_growth:.1f}%",
                    "طريقة الحساب": "متوسط نمو صافي الربح السنوي",
                    "معيار لينش": "بين 20% و 25% (تجنب > 50%)",
                    "حالة السهم": "مثالي ✅" if 15 < eps_growth < 35 else "خارج النطاق ⚠️"
                },
                {
                    "المؤشر المالي": "الديون / الملكية",
                    "القيمة الحالية": f"{de_ratio:.1f}%",
                    "طريقة الحساب": "إجمالي الديون ÷ حقوق المساهمين",
                    "معيار لينش": "أقل من 35% لأسهم النمو",
                    "حالة السهم": "آمن ✅" if de_ratio < 35 else "مخاطرة ❌"
                },
                {
                    "المؤشر المالي": "النقد الصافي",
                    "القيمة الحالية": f"{net_cash:,.0f}",
                    "طريقة الحساب": "إجمالي الكاش - إجمالي الديون",
                    "معيار لينش": "قيمة موجبة (وسادة أمان)",
                    "حالة السهم": "قوي ✅" if net_cash > 0 else "ضعيف ❌"
                },
                {
                    "المؤشر المالي": "كفاءة المخزون",
                    "القيمة الحالية": f"نمو {inv_growth:.1f}%",
                    "طريقة الحساب": "مقارنة نمو المخزون بنمو المبيعات",
                    "معيار لينش": "نمو المخزون < نمو المبيعات",
                    "حالة السهم": "سليم ✅" if inv_growth < rev_growth else "ركود ⚠️"
                },
                {
                    "المؤشر المالي": "جودة الأرباح",
                    "القيمة الحالية": f"{fcf_ratio:.2f}",
                    "طريقة الحساب": "التدفق النقدي الحر ÷ صافي الربح",
                    "معيار لينش": "أكبر من 1.0 (أرباح حقيقية)",
                    "حالة السهم": "جودة عالية ✅" if fcf_ratio > 1 else "أرباح ورقية ⚠️"
                }
            ]

            st.table(pd.DataFrame(results))
            
    except Exception as e:
        st.error(f"خطأ في معالجة السهم: {e}")
        st.info("تأكد من إدخال رمز صحيح وتوفر بياناته المالية.")
