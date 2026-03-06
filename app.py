import streamlit as st
import yfinance as yf

st.set_page_config(page_title="محلل لينش المالي", layout="wide")

st.title("📊 الفحص المالي الصارم لأسهم النمو (منهج بيتر لينش)")
ticker = st.text_input("أدخل رمز السهم (مثال: 2222.SE أو NVDA)", value="AAPL")

if st.button("تحليل المؤشرات المالية"):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # 1. استخراج البيانات المالية الأساسية
        peg = info.get('pegRatio')
        pe = info.get('trailingPE')
        growth = info.get('earningsQuarterlyGrowth', 0) * 100
        debt_to_equity = info.get('debtToEquity')
        cash = info.get('totalCashPerShare')
        price = info.get('currentPrice')

        # 2. نظام النقاط المالي (من 100 نقطة)
        score = 0
        checks = []

        # المعيار 1: نسبة PEG (السعر مقابل النمو) - الوزن: 30 نقطة
        if peg and peg < 1.0:
            score += 30
            checks.append(("✅ نسبة PEG", f"{peg}", "ممتاز: السهم يتداول بأقل من قيمة نموه."))
        else:
            checks.append(("❌ نسبة PEG", f"{peg}", "سيء: السعر مرتفع جداً مقارنة بمعدل النمو."))

        # المعيار 2: نمو الأرباح (EPS Growth) - الوزن: 20 نقطة
        if 15 <= growth <= 30:
            score += 20
            checks.append(("✅ نمو الأرباح", f"{growth:.1f}%", "مثالي: نمو قوي ومستدام (طابع أسهم النمو)."))
        elif growth > 30:
            score += 10
            checks.append(("⚠️ نمو الأرباح", f"{growth:.1f}%", "تنبيه: نمو سريع جداً قد يكون غير مستدام."))
        else:
            checks.append(("❌ نمو الأرباح", f"{growth:.1f}%", "ضعيف: لا يصنف كأحد أسهم النمو السريع."))

        # المعيار 3: الملاءة المالية (الديون) - الوزن: 20 نقطة
        if debt_to_equity and debt_to_equity < 35:
            score += 20
            checks.append(("✅ نسبة الديون", f"{debt_to_equity}%", "ممتاز: ميزانية عمومية قوية جداً."))
        else:
            checks.append(("❌ نسبة الديون", f"{debt_to_equity}%", "خطر: ديون مرتفعة قد تسبب أزمة في الركود."))

        # المعيار 4: مكرر الربحية (P/E) مقارنة بالنمو - الوزن: 15 نقطة
        if pe and growth and pe < growth:
            score += 15
            checks.append(("✅ مكرر الربحية", f"{pe:.1f}", f"جيد: المكرر أقل من معدل النمو ({growth:.1f}%)."))
        else:
            checks.append(("❌ مكرر الربحية", f"{pe:.1f}", "سيء: المكرر أعلى من معدل النمو (تضخم سعري)."))

        # المعيار 5: النقد الصافي (Net Cash) - الوزن: 15 نقطة
        if cash and price and (cash / price) > 0.10:
            score += 15
            checks.append(("✅ السيولة للنهم", f"{cash}$", "ممتاز: الشركة تملك كاش وفير لكل سهم (وسادة أمان)."))
        else:
            checks.append(("⚠️ السيولة", f"{cash}$", "مقبول: لا يوجد كاش استثنائي يحمي السهم."))

        # 3. عرض النتائج
        st.header(f"إجمالي تقييم لينش المالي: {score}/100")
        
        if score >= 80: st.success("🎯 سهم نمو بامتياز (فرصة استثمارية قوية)")
        elif score >= 50: st.warning("⚖️ سهم متوسط (يحتاج حذر في سعر الدخول)")
        else: st.error("🛑 سهم لا يطابق شروط أسهم النمو")

        # عرض تفصيلي لكل مؤشر
        for title, val, desc in checks:
            with st.expander(title, expanded=True):
                st.write(f"**القيمة الحالية:** {val}")
                st.write(f"**تحليل لينش:** {desc}")

    except Exception as e:
        st.error("فشل التحليل. تأكد من أن الرمز صحيح (مثل 1120.SE للراجحي أو MSFT لمايكروسوفت).")
