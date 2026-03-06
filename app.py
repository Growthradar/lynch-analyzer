import streamlit as st
import yfinance as yf
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="محلل بيتر لينش الذكي", layout="wide")

st.title("📈 أداة تحليل الأسهم وفق معايير بيتر لينش")
st.write("قم بإدخال رمز السهم (مثلاً: 2222.SE للأسهم السعودية أو AAPL للأمريكية)")

# مدخلات المستخدم
ticker_input = st.text_input("رمز السهم", value="2222.SE")

if st.button("تحليل السهم"):
    with st.spinner('جاري جلب البيانات من Yahoo Finance...'):
        try:
            stock = yf.Ticker(ticker_input)
            info = stock.info
            
            # استخراج المؤشرات الأساسية
            peg = info.get('pegRatio', 0)
            de_ratio = info.get('debtToEquity', 0)
            inst_own = info.get('heldPercentInstitutions', 0) * 100
            eps_growth = info.get('earningsQuarterlyGrowth', 0) * 100
            current_price = info.get('currentPrice', 0)
            
            # --- منطق حساب النقاط (100 نقطة) ---
            score = 0
            analysis_log = []

            # 1. اختبار PEG (30 نقطة)
            if 0 < peg < 1:
                score += 30
                analysis_log.append("✅ نسبة PEG ممتازة (أقل من 1)")
            elif peg >= 1:
                analysis_log.append("❌ السهم متضخم سعرياً مقارنة بنموه (PEG > 1)")

            # 2. اختبار الديون (20 نقطة)
            if 0 < de_ratio < 35:
                score += 20
                analysis_log.append("✅ ميزانية قوية جداً (ديون منخفضة)")
            else:
                analysis_log.append("⚠️ تنبيه: الديون مرتفعة أو غير واضحة")

            # 3. الملكية المؤسسية (20 نقطة) - شرط لينش (الأقل أفضل)
            if inst_own < 30:
                score += 20
                analysis_log.append("✅ السهم 'مخفي' عن المؤسسات الكبرى (فرصة اكتشاف)")
            else:
                analysis_log.append("ℹ️ السهم مملوك بكثافة للمؤسسات")

            # 4. نمو الأرباح (30 نقطة)
            if 15 <= eps_growth <= 25:
                score += 30
                analysis_log.append("✅ نمو أرباح مستدام ومثالي (15% - 25%)")
            elif eps_growth > 25:
                score += 15
                analysis_log.append("⚠️ نمو سريع جداً قد لا يستمر")

            # --- عرض النتائج ---
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.metric("إجمالي النقاط", f"{score}/100")
                if score >= 80: st.success("تصنيف: سهم نمو بامتياز (Tenbagger)")
                elif score >= 50: st.warning("تصنيف: سهم جيد للمراقبة")
                else: st.error("تصنيف: مخاطرة عالية / لا يطابق المعايير")
            
            with col2:
                st.subheader("تقرير التحليل الميداني:")
                for item in analysis_log:
                    st.write(item)

            # عرض جدول البيانات الخام
            st.divider()
            st.subheader("بيانات السهم الحالية")
            st.json({
                "السعر الحالي": current_price,
                "نسبة PEG": peg,
                "الدين إلى حقوق الملكية": de_ratio,
                "ملكية المؤسسات %": inst_own,
                "نمو الأرباح الربع سنوي %": eps_growth
            })

        except Exception as e:
            st.error(f"حدث خطأ في جلب البيانات: {e}")
            st.info("تأكد من كتابة الرمز بشكل صحيح (مثال للأسهم السعودية: 1120.SE لراجحي)")

st.sidebar.info("""
**ملاحظة:** 
تعتمد هذه الأداة على بيانات Yahoo Finance. للأسهم السعودية، يتم تحديث البيانات المالية دورياً من تداول، ولكن يفضل دائماً مطابقتها مع موقع 'أرقام' للتأكد من ملكية كبار الملاك بدقة.
""")
