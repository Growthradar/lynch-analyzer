import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="محلل لينش الذاتي", layout="wide")

st.title("🧮 المحلل المالي الذاتي (معادلات بيتر لينش)")
st.write("تقوم الأداة بحساب المؤشرات آلياً من القوائم المالية الخام لآخر سنوات.")

ticker_input = st.text_input("أدخل رمز السهم (مثلاً 7020 أو AAPL)", value="7020")
ticker = f"{ticker_input}.SR" if (ticker_input.isdigit() and len(ticker_input) == 4) else ticker_input

if st.button("تحليل القوائم المالية وحساب النقاط"):
    try:
        with st.spinner('جاري استخراج البيانات المالية وحساب المعادلات...'):
            stock = yf.Ticker(ticker)
            
            # 1. جلب القوائم المالية (Income Statement & Balance Sheet)
            income_stmt = stock.financials
            balance_sheet = stock.balance_sheet
            info = stock.info

            # --- أ. حساب معدل نمو الأرباح (EPS Growth) لآخر 3-4 سنوات ---
            # نأخذ صافي الدخل (Net Income) ونحسب متوسط النمو السنوي
            net_income = income_stmt.loc['Net Income']
            growth_rates = net_income.pct_change(periods=-1).dropna() * 100
            avg_growth = growth_rates.mean() # متوسط النمو التاريخي

            # --- ب. حساب نسبة الدين إلى حقوق الملكية (D/E Ratio) ---
            total_debt = balance_sheet.loc['Total Debt'][0] if 'Total Debt' in balance_sheet.index else 0
            equity = balance_sheet.loc['Stockholders Equity'][0]
            calc_de_ratio = (total_debt / equity) * 100

            # --- ج. حساب مكرر الربحية (P/E) الحالي ---
            current_price = info.get('currentPrice')
            eps_trailing = info.get('trailingEps')
            calc_pe = current_price / eps_trailing if eps_trailing else info.get('trailingPE')

            # --- د. حساب نسبة PEG (المعادلة: P/E ÷ Growth) ---
            calc_peg = calc_pe / avg_growth if (avg_growth and avg_growth > 0) else 0

            # --- نظام النقاط التراكمي (100 نقطة) ---
            score = 0
            report = []

            # تقييم PEG (30 نقطة)
            if 0 < calc_peg < 1.0:
                score += 30
                report.append(("✅ نسبة PEG المحسوبة", f"{calc_peg:.2f}", "سعر ممتاز مقارنة بنمو الأرباح التاريخي."))
            else:
                report.append(("❌ نسبة PEG المحسوبة", f"{calc_peg:.2f}", "السعر متضخم (PEG > 1)."))

            # تقييم النمو (25 نقطة)
            if 15 <= avg_growth <= 30:
                score += 25
                report.append(("✅ متوسط نمو الأرباح", f"{avg_growth:.1f}%", "نمو مثالي ومستدام حسب معايير لينش."))
            else:
                report.append(("⚠️ نمو الأرباح", f"{avg_growth:.1f}%", "خارج النطاق المثالي لأسهم النمو السريع."))

            # تقييم الديون (25 نقطة)
            if calc_de_ratio < 35:
                score += 25
                report.append(("✅ نسبة الديون", f"{calc_de_ratio:.1f}%", "ميزانية قوية جداً (ديون منخفضة)."))
            else:
                report.append(("❌ نسبة الديون", f"{calc_de_ratio:.1f}%", "ديون مرتفعة تزيد المخاطر."))

            # تقييم P/E مقابل النمو (20 نقطة)
            if calc_pe < avg_growth:
                score += 20
                report.append(("✅ مكرر الربحية الحالي", f"{calc_pe:.1f}", f"المكرر أقل من معدل النمو ({avg_growth:.1f}%)."))
            else:
                report.append(("❌ مكرر الربحية الحالي", f"{calc_pe:.1f}", "المكرر أعلى من النمو."))

            # عرض النتائج
            st.divider()
            st.header(f"النتيجة النهائية بناءً على الحسابات: {score} / 100")
            
            cols = st.columns(2)
            for i, (title, val, desc) in enumerate(report):
                with cols[i % 2]:
                    st.metric(title, val)
                    st.caption(desc)

    except Exception as e:
        st.error(f"حدث خطأ في الحسابات: {e}")
        st.info("تأكد من توفر القوائم المالية للسهم المختار لآخر سنتين على الأقل.")
