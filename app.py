import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="محلل بيتر لينش التفصيلي", layout="centered")

st.title("🔬 التقييم التحليلي الدقيق (منهج بيتر لينش)")
st.write("أدخل رمز السهم للحصول على تقييم لكل مؤشر مالي على حدة.")

ticker_symbol = st.text_input("رمز السهم (مثال: 1120.SE أو AAPL)", value="2222.SE")

if st.button("بدء التقييم التفصيلي"):
    with st.spinner('جاري فحص القوائم المالية...'):
        try:
            stock = yf.Ticker(ticker_symbol)
            info = stock.info
            
            # مصفوفة لتخزين النقاط والتقييمات
            results = []
            total_score = 0

            # --- 1. تقييم نسبة PEG (النمو مقابل السعر) ---
            peg = info.get('pegRatio')
            if peg is not None:
                if peg < 0.5: pts, msg, status = 25, "ممتاز جداً: نمو هائل بسعر رخيص", "Success"
                elif peg < 1.0: pts, msg, status = 20, "جيد: السعر عادل مقارنة بالنمو", "Success"
                elif peg < 1.5: pts, msg, status = 10, "مقبول: السعر مرتفع قليلاً", "Warning"
                else: pts, msg, status = 0, "سيء: السعر مبالغ فيه جداً", "Error"
                results.append(["نسبة PEG", peg, pts, msg, status])
                total_score += pts
            else:
                results.append(["نسبة PEG", "غير متوفر", 0, "لا يمكن تقييم السعر دون بيانات النمو", "Off"])

            # --- 2. تقييم الملاءة المالية (الديون) ---
            de = info.get('debtToEquity')
            if de is not None:
                if de < 35: pts, msg, status = 20, "ممتاز: ديون منخفضة جداً (أمان عالي)", "Success"
                elif de < 50: pts, msg, status = 10, "مقبول: ديون معتدلة", "Warning"
                else: pts, msg, status = 0, "خطر: ديون مرتفعة قد ترهق الشركة", "Error"
                results.append(["نسبة الدين/الملكية", f"{de}%", pts, msg, status])
                total_score += pts

            # --- 3. تقييم ملكية المؤسسات (شرط السهم المخفي) ---
            inst = info.get('heldPercentInstitutions', 0) * 100
            if inst > 0:
                if inst < 30: pts, msg, status = 15, "مثالي: المؤسسات لم تكتشف السهم بعد", "Success"
                elif inst < 60: pts, msg, status = 10, "متوسط: السهم بدأ يحظى باهتمام الصناديق", "Warning"
                else: pts, msg, status = 5, "مزدحم: معظم الصناديق تملكه بالفعل", "Info"
                results.append(["ملكية المؤسسات", f"{inst:.1f}%", pts, msg, status])
                total_score += pts

            # --- 4. استدامة نمو الأرباح (EPS Growth) ---
            growth = info.get('earningsQuarterlyGrowth', 0) * 100
            if growth != 0:
                if 15 <= growth <= 30: pts, msg, status = 25, "مثالي: نمو مستدام وقوي", "Success"
                elif growth > 30: pts, msg, status = 15, "تنبيه: نمو سريع جداً قد يكون طفرة مؤقتة", "Warning"
                elif 0 < growth < 15: pts, msg, status = 10, "بطيء: نمو أقل من طموحات لينش", "Info"
                else: pts, msg, status = 0, "سيء: أرباح متراجعة", "Error"
                results.append(["نمو الأرباح", f"{growth:.1f}%", pts, msg, status])
                total_score += pts

            # --- عرض النتائج بشكل منفصل ---
            st.subheader(f"النتيجة الإجمالية: {total_score}/85") # 85 هي مجموع النقاط المتاحة آلياً
            
            for res in results:
                with st.expander(f"🔍 فحص {res[0]}: {res[1]}", expanded=True):
                    col_a, col_b = st.columns([1, 4])
                    col_a.metric("النقاط", f"+{res[2]}")
                    if res[4] == "Success": st.success(res[3])
                    elif res[4] == "Warning": st.warning(res[3])
                    elif res[4] == "Error": st.error(res[3])
                    else: st.info(res[3])

            # نصيحة التقييم النوعي (التي لا تظهر في الأرقام)
            st.divider()
            st.subheader("💡 خطوات التقييم اليدوي (تكملة لينش)")
            st.info("البيانات أعلاه رقمية فقط. لينش يشترط أيضاً: \n1. هل تفهم عمل الشركة؟ \n2. هل الاسم ممل؟ \n3. هل يشتري المطلعون (المدراء) أسهمهم الآن؟")

        except Exception as e:
            st.error(f"حدث خطأ أثناء تحليل {ticker_symbol}. تأكد من صحة الرمز.")
