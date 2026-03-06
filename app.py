import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="محلل لينش الصارم", layout="wide")
st.title("🎯 المحلل المالي لأسهم النمو (بيتر لينش)")

ticker_raw = st.text_input("أدخل رمز السهم (مثال: 7020 أو NVDA)", value="7020")
ticker = f"{ticker_raw}.SR" if (ticker_raw.isdigit() and len(ticker_raw) == 4) else ticker_raw

if st.button("بدء الفحص المالي المعمق"):
    try:
        with st.spinner('جاري تحليل القوائم المالية...'):
            stock = yf.Ticker(ticker)
            income = stock.financials
            balance = stock.balance_sheet
            cf = stock.cashflow
            info = stock.info

            # --- الحسابات المالية الدقيقة (Formulas) ---
            
            # 1. نمو الأرباح (EPS Growth) - متوسط آخر 3 سنوات
            eps_growth = (income.loc['Net Income'].pct_change(periods=-1).dropna().mean() * 100)
            
            # 2. نسبة PEG (P/E / Growth)
            pe = info.get('trailingPE') or (info.get('currentPrice') / info.get('trailingEps', 1))
            peg = pe / eps_growth if eps_growth > 0 else 0
            
            # 3. نسبة الدين إلى حقوق المساهمين (D/E)
            total_debt = balance.loc['Total Debt'].iloc[0] if 'Total Debt' in balance.index else 0
            equity = balance.loc['Stockholders Equity'].iloc[0]
            de_ratio = (total_debt / equity) * 100
            
            # 4. النقد الصافي (Net Cash)
            cash = balance.loc['Cash And Cash Equivalents'].iloc[0]
            net_cash = cash - total_debt
            market_cap = info.get('marketCap', 1)
            net_cash_pct = (net_cash / market_cap) * 100
            
            # 5. اختبار المخزون مقابل المبيعات
            rev_growth = (income.loc['Total Revenue'].pct_change(periods=-1).iloc[0] * 100)
            inv_growth = 0
            if 'Inventory' in balance.index:
                inv_growth = (balance.loc['Inventory'].pct_change(periods=-1).iloc[0] * 100)
            
            # 6. التدفق النقدي الحر (Free Cash Flow) مقابل الأرباح
            latest_fcf = cf.loc['Free Cash Flow'].iloc[0] if 'Free Cash Flow' in cf.index else 0
            latest_profit = income.loc['Net Income'].iloc[0]
            fcf_to_profit = latest_fcf / latest_profit if latest_profit != 0 else 0

            # --- نظام التقييم بالنقاط (100 نقطة) ---
            score = 0
            analysis = []

            # تقييم PEG (20 نقطة)
            if 0 < peg < 0.5: score += 20; analysis.append(("✅ PEG (لقطة)", f"{peg:.2f}", "سعر مذهل مقارنة بالنمو."))
            elif peg < 1.0: score += 15; analysis.append(("✅ PEG (عادل)", f"{peg:.2f}", "سعر عادل للنمو."))
            else: analysis.append(("❌ PEG (متضخم)", f"{peg:.2f}", "السعر يسبق النمو بكثير."))

            # تقييم النمو (20 نقطة)
            if 15 <= eps_growth <= 30: score += 20; analysis.append(("✅ نمو الأرباح", f"{eps_growth:.1f}%", "نمو مثالي ومستدام."))
            elif eps_growth > 50: score += 5; analysis.append(("⚠️ نمو مفرط", f"{eps_growth:.1f}%", "خطر! النمو العالي جداً يجذب المنافسين."))
            else: analysis.append(("❌ نمو ضعيف", f"{eps_growth:.1f}%", "لا يصنف كـ 'سهم نمو سريع'."))

            # تقييم الديون (20 نقطة)
            if de_ratio < 35: score += 20; analysis.append(("✅ الديون/حقوق الملكية", f"{de_ratio:.1f}%", "ميزانية قوية وآمنة."))
            else: analysis.append(("❌ ديون مرتفعة", f"{de_ratio:.1f}%", "تجاوز الحد الآمن لشركات النمو."))

            # تقييم النقد الصافي (15 نقطة)
            if net_cash > 0: score += 15; analysis.append(("✅ النقد الصافي", "إيجابي", f"تمتلك كاش يتجاوز ديونها بـ {net_cash/1e6:.1f}M."))
            else: analysis.append(("⚠️ نقد صافي سالـب", "سلبي", "الديون تتجاوز الكاش المتوفر."))

            # تقييم المخزون (15 نقطة)
            if inv_growth < rev_growth: score += 15; analysis.append(("✅ حركة المخزون", "سليمة", "المبيعات تسبق المخزون (طلب قوي)."))
            else: analysis.append(("❌ تراكم المخزون", "خطر", "المخزون ينمو أسرع من المبيعات (ركود بضاعة)."))

            # تقييم التدفق النقدي (10 نقاط)
            if fcf_to_profit > 1: score += 10; analysis.append(("✅ جودة الأرباح", "حقيقية", "التدفق النقدي الحر أعلى من الأرباح الورقية."))
            else: analysis.append(("⚠️ جودة الأرباح", "محاسبية", "الأرباح الورقية أعلى من الكاش الحقيقي المولد."))

            # --- عرض النتائج النهائية ---
            st.header(f"النتيجة النهائية: {score} / 100")
            if score >= 80: st.success("🌟 سهم نمو بامتياز (Tenbagger)")
            elif score >= 50: st.warning("⚖️ سهم متوسط - يحتاج لمراجعة نوعية")
            else: st.error("🛑 سهم لا يطابق معايير بيتر لينش")

            # عرض النتائج في بطاقات
            cols = st.columns(3)
            for i, (title, val, desc) in enumerate(analysis):
                with cols[i % 3]:
                    st.info(f"**{title}**\n\nالقيمة: {val}\n\n{desc}")

    except Exception as e:
        st.error(f"حدث خطأ في جلب البيانات: {e}")
        st.info("تأكد من توفر القوائم المالية الكاملة لهذا السهم.")
