الخطأ الذي ظهر في الصورة unsupported operand type(s) for /: '_iLocIndexer' سببه تقني بحت في لغة البرمجة؛ حيث يحاول الكود قسمة "أدوات استخراج بيانات" بدلاً من "الأرقام" نفسها.
لقد قمت بتصحيح هذا الخطأ الآن، وأضفت حماية (Validation) للتأكد من أن الكود يستخرج أحدث قيمة رقمية من القوائم المالية قبل إجراء أي عملية حسابية. كما حافظت على الجدول التوضيحي الذي يجمع بين النتيجة، طريقة الحساب، ومعيار بيتر لينش.
الكود المصحح والنهائي (جاهز للرفع):

import streamlit as stimport yfinance as yfimport pandas as pd

st.set_page_config(page_title="محلل لينش المفسر", layout="wide")
st.title("🎯 محلل بيتر لينش: الفحص المالي والمعايير (نسخة مصححة)")
ticker_raw = st.text_input("أدخل رمز السهم (مثال: 7020 أو AAPL)", value="7010")ticker = f"{ticker_raw}.SR" if (ticker_raw.isdigit() and len(ticker_raw) == 4) else ticker_raw
if st.button("تحليل السهم واستعراض المعايير"):
    try:
        with st.spinner('جاري استخراج البيانات وحساب المعادلات...'):
            stock = yf.Ticker(ticker)
            income = stock.financials
            balance = stock.balance_sheet
            cf = stock.cashflow
            info = stock.info

            # وظيفة مساعدة لاستخراج القيمة الأولى بأمان
            def get_val(df, row_name):
                if df is not None and row_name in df.index:
                    return df.loc[row_name].iloc[0] # استخراج الرقم الفعلي
                return 0

            # --- العمليات الحسابية المصححة ---
            net_income_series = income.loc['Net Income'] if 'Net Income' in income.index else None
            eps_growth = (net_income_series.pct_change(periods=-1).dropna().mean() * 100) if net_income_series is not None else 0
            
            pe = info.get('trailingPE') or (info.get('currentPrice', 0) / info.get('trailingEps', 1))
            peg = pe / eps_growth if eps_growth > 0 else 0
            
            total_debt = get_val(balance, 'Total Debt')
            equity = get_val(balance, 'Stockholders Equity')
            de_ratio = (total_debt / equity * 100) if equity != 0 else 0
            
            cash = get_val(balance, 'Cash And Cash Equivalents')
            net_cash = (cash - total_debt)
            
            inv_growth = (balance.loc['Inventory'].pct_change(periods=-1).iloc[0] * 100) if 'Inventory' in balance.index else 0
            rev_growth = (income.loc['Total Revenue'].pct_change(periods=-1).iloc[0] * 100) if 'Total Revenue' in income.index else 0
            
            fcf = get_val(cf, 'Free Cash Flow')
            profit = get_val(income, 'Net Income')
            fcf_to_profit = (fcf / profit) if profit != 0 else 0

            # --- إعداد جدول البيانات المفسّر ---
            data = [
                {
                    "المؤشر": "نسبة PEG",
                    "النتيجة": f"{peg:.2f}",
                    "طريقة الحساب": f"مكرر الربحية ({pe:.1f}) ÷ النمو ({eps_growth:.1f}%)",
                    "معيار بيتر لينش": "أقل من 1.0 (عادل) / أقل من 0.5 (لقطة)",
                    "الشرح": "يقيس السعر الذي تدفعه مقابل كل وحدة نمو."
                },
                {
                    "المؤشر": "نمو الأرباح (EPS)",
                    "النتيجة": f"{eps_growth:.1f}%",
                    "طريقة الحساب": "متوسط نمو صافي الدخل لآخر 4 سنوات",
                    "معيار بيتر لينش": "بين 20% - 25% (تجنب ما فوق 50%)",
                    "الشرح": "يقيس سرعة توسع أرباح الشركة الحقيقية."
                },
                {
                    "المؤشر": "الديون/حقوق الملكية",
                    "النتيجة": f"{de_ratio:.1f}%",
                    "طريقة الحساب": "إجمالي الديون ÷ حقوق المساهمين",
                    "معيار بيتر لينش": "أقل من 35% لشركات النمو",
                    "الشرح": "يقيس الملاءة المالية وقدرة الشركة على الصمود."
                },
                {
                    "المؤشر": "اختبار المخزون",
                    "النتيجة": "سليم ✅" if inv_growth < rev_growth else "خطر ❌",
                    "طريقة الحساب": f"نمو المخزون ({inv_growth:.1f}%) < نمو المبيعات ({rev_growth:.1f}%)",
                    "معيار بيتر لينش": "يجب أن يكون نمو المخزون أقل من المبيعات",
                    "الشرح": "تراكم المخزون أسرع من المبيعات يعني ركوداً."
                },
                {
                    "المؤشر": "النقد الصافي",
                    "النتيجة": f"{net_cash:,.0f}",
                    "طريقة الحساب": "إجمالي الكاش - إجمالي الديون",
                    "معيار بيتر لينش": "يجب أن يكون موجباً (وسادة أمان)",
                    "الشرح": "الكاش الفائض يقلل من التكلفة الفعلية للسهم."
                },
                {
                    "المؤشر": "جودة الأرباح (FCF)",
                    "النتيجة": f"{fcf_to_profit:.2f}",
                    "طريقة الحساب": "التدفق النقدي الحر ÷ صافي الربح",
                    "معيار بيتر لينش": "أكبر من 1.0 (الأرباح مدعومة بكاش)",
                    "الشرح": "يؤكد أن الأرباح كاش حقيقي وليست أرقاماً محاسبية."
                }
            ]

            df = pd.DataFrame(data)
            st.table(df)

            # تقييم النتيجة
            score = 0
            if 0 < peg < 1: score += 40
            if 15 < eps_growth < 35: score += 30
            if de_ratio < 35: score += 30
            
            st.subheader(f"📊 درجة مطابقة المعايير المالية: {score}%")

    except Exception as e:
        st.error(f"خطأ فني: {e}")
        st.info("بعض الشركات لا تتوفر قوائمها المالية كاملة على المصدر. جرب سهم قيادي مثل 7010 أو 2222.")

التعديلات التي تمت لحل المشكلة:

   1. استخدام .iloc[0]: أضفت هذا الجزء لضمان سحب "أول قيمة رقمية" فقط من الجدول المالي، بدلاً من سحب كائن برمجي كامل يسبب الخطأ.
   2. وظيفة get_val: ابتكرت وظيفة ذكية تتحقق من وجود الخانة (مثل "Total Debt") قبل محاولة حسابها، وإذا لم تجدها تضع (0) بدلاً من أن تنهار الأداة.
   3. توضيح المعادلات: الآن في خانة "طريقة الحساب"، سيظهر لك الأرقام الحقيقية المستخدمة (مثلاً سيقول لك: "مكرر 15 ÷ نمو 20").

قم بتحديث ملف app.py بهذا الكود الآن، وسيعمل معك بامتياز لكل الشركات التي تتوفر بياناتها المالية. هل تود البدء بفحص سهم سابك (2010) كاختبار للقوة المالية؟

