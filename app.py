import streamlit as st
import yfinance as yf

# إعدادات واجهة المستخدم
st.set_page_config(page_title="محلل بيتر لينش المالي", layout="wide")

st.title("📊 الفحص المالي لأسهم النمو (منهج بيتر لينش)")
st.write("أدخل رمز السهم (مثال: 7020 للأسهم السعودية أو NVDA للأمريكية)")

# خانة الإدخال مع التصحيح التلقائي للرموز السعودية
ticker_input = st.text_input("أدخل رمز السهم", value="7020")

# معالجة الرمز تلقائياً
if ticker_input.isdigit() and len(ticker_input) == 4:
    ticker = f"{ticker_input}.SR"
else:
    ticker = ticker_input

if st.button("تحليل المؤشرات المالية"):
    try:
        with st.spinner(f'جاري فحص بيانات {ticker}...'):
            stock = yf.Ticker(ticker)
            info = stock.info
            
            if not info or 'currentPrice' not in info:
                st.error("❌ لم نتمكن من العثور على بيانات لهذا الرمز. تأكد من صحته (مثال: 7020 أو AAPL).")
            else:
                # 1. استخراج المؤشرات المالية
                peg = info.get('pegRatio')
                pe = info.get('trailingPE')
                # نمو الأرباح المتوقع أو التاريخي
                growth = info.get('earningsQuarterlyGrowth', 0)
                if growth: growth *= 100 
                
                debt_to_equity = info.get('debtToEquity')
                cash_per_share = info.get('totalCashPerShare')
                price = info.get('currentPrice')

                # 2. نظام النقاط (100 نقطة)
                score = 0
                results = []

                # --- معيار 1: نسبة PEG (30 نقطة) ---
                if peg and peg > 0:
                    if peg < 1.0:
                        score += 30
                        results.append(("✅ نسبة PEG", f"{peg}", "ممتاز: سعر السهم رخيص مقارنة بنموه."))
                    else:
                        results.append(("❌ نسبة PEG", f"{peg}", "سيء: السعر متضخم مقارنة بالنمو المتوقع."))
                else:
                    results.append(("⚠️ نسبة PEG", "غير متوفرة", "لا توجد بيانات كافية لتقييم السعر مقابل النمو."))

                # --- معيار 2: نمو الأرباح EPS (20 نقطة) ---
                if growth and growth > 0:
                    if 15 <= growth <= 30:
                        score += 20
                        results.append(("✅ نمو الأرباح", f"{growth:.1f}%", "مثالي: نمو قوي ومستدام (أحد أسهم النمو السريع)."))
                    elif growth > 30:
                        score += 10
                        results.append(("⚠️ نمو الأرباح", f"{growth:.1f}%", "خطر: نمو سريع جداً قد لا يستمر."))
                    else:
                        results.append(("❌ نمو الأرباح", f"{growth:.1f}%", "ضعيف: نمو أقل من معايير بيتر لينش لأسهم النمو."))
                else:
                    results.append(("⚠️ نمو الأرباح", "غير متوفرة", "يجب مراجعة نمو الأرباح يدوياً من موقع 'أرقام'."))

                # --- معيار 3: الديون (20 نقطة) ---
                if debt_to_equity is not None:
                    if debt_to_equity < 35:
                        score += 20
                        results.append(("✅ نسبة الديون", f"{debt_to_equity:.1f}%", "ممتاز: ميزانية قوية جداً وديون منخفضة."))
                    else:
                        results.append(("❌ نسبة الديون", f"{debt_to_equity:.1f}%", "خطر: ديون مرتفعة تزيد من مخاطر الإفلاس."))
                else:
                    results.append(("⚠️ الديون", "غير متوفرة", "تأكد من نسبة الديون يدوياً من القوائم المالية."))

                # --- معيار 4: P/E مقابل النمو (15 نقطة) ---
                if pe and growth and growth > 0:
                    if pe < growth:
                        score += 15
                        results.append(("✅ مكرر الربحية", f"{pe:.1f}", f"جيد: مكرر الربحية أقل من معدل النمو ({growth:.1f}%)."))
                    else:
                        results.append(("❌ مكرر الربحية", f"{pe:.1f}", "سيء: المكرر أعلى من معدل النمو."))
                else:
                    results.append(("⚠️ مكرر الربحية", "بيانات ناقصة", "لا يمكن المقارنة بين المكرر والنمو حالياً."))

                # --- معيار 5: السيولة النقدية (15 نقطة) ---
                if cash_per_share and price:
                    cash_ratio = (cash_per_share / price) * 100
                    if cash_ratio > 10:
                        score += 15
                        results.append(("✅ السيولة", f"{cash_per_share}$", "ممتاز: الشركة تملك كاش وفير يحمي السهم."))
                    else:
                        results.append(("⚠️ السيولة", f"{cash_per_share}$", "عادية: لا يوجد فائض كاش استثنائي."))

                # 3. عرض النتائج النهائية
                st.divider()
                st.header(f"النتيجة النهائية: {score} / 100")
                
                if score >= 75: st.success("🌟 سهم نمو واعد جداً (تطابق عالي مع معايير لينش)")
                elif score >= 50: st.warning("⚖️ سهم متوسط (يتطلب دراسة نوعية أعمق)")
                else: st.error("🛑 سهم لا يطابق شروط النمو السريع لبيتر لينش")

                # عرض التفاصيل
                st.subheader("تفاصيل فحص المؤشرات المالية:")
                for title, val, desc in results:
                    with st.expander(title, expanded=True):
                        st.write(f"**القيمة المستخرجة:** {val}")
                        st.write(f"**التحليل:** {desc}")

    except Exception as e:
        st.error(f"فشل التحليل بسبب: {e}")
        st.info("تأكد من كتابة الرمز بشكل صحيح. مثال: 7020 للسعودي، أو AAPL للأمريكي.")

st.sidebar.markdown("""
### 💡 نصيحة بيتر لينش:
*البيانات المالية هي نصف القصة فقط. النصف الآخر هو أن تفهم ماذا تبيع الشركة ولماذا يحبها الناس.*
""")
