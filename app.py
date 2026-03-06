import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="محلل لينش المفسر", layout="wide")
st.title("🎯 محلل بيتر لينش: الفحص المالي والمعايير")

ticker_raw = st.text_input("أدخل رمز السهم (مثال: 7020 أو AAPL)", value="7010")
ticker = f"{ticker_raw}.SR" if (ticker_raw.isdigit() and len(ticker_raw) == 4) else ticker_raw

if st.button("تحليل السهم واستعراض المعايير"):
    try:
        with st.spinner('جاري استخراج البيانات وحساب المعادلات...'):
            stock = yf.Ticker(ticker)
            income = stock.financials
            balance = stock.balance_sheet
            cf = stock.cashflow
            info = stock.info

            # --- العمليات الحسابية ---
            eps_growth = (income.loc['Net Income'].pct_change(periods=-1).dropna().mean() * 100)
            pe = info.get('trailingPE') or (info.get('currentPrice') / info.get('trailingEps', 1))
            peg = pe / eps_growth if eps_growth > 0 else 0
            total_debt = balance.loc['Total Debt'].iloc if 'Total Debt' in balance.index else 0
            equity = balance.loc['Stockholders Equity'].iloc
            de_ratio = (total_debt / equity) * 100
            net_cash = (balance.loc['Cash And Cash Equivalents'].iloc - total_debt)
            inv_growth = (balance.loc['Inventory'].pct_change(periods=-1).iloc * 100) if 'Inventory' in balance.index else 0
            rev_growth = (income.loc['Total Revenue'].pct_change(periods=-1).iloc * 100)
            fcf_to_profit = (cf.loc['Free Cash Flow'].iloc / income.loc['Net Income'].iloc) if 'Net Income' in income.index else 0

            # --- إعداد جدول البيانات المفسّر ---
            data = [
                {
                    "المؤشر": "نسبة PEG",
                    "النتيجة": f"{peg:.2f}",
                    "طريقة الحساب": "مكرر الربحية (P/E) ÷ معدل نمو الأرباح",
                    "معيار بيتر لينش": "أقل من 1.0 (عادل) / أقل من 0.5 (لقطة)",
                    "الشرح": "يقيس السعر الذي تدفعه مقابل كل وحدة نمو."
                },
                {
                    "المؤشر": "نمو الأرباح (EPS)",
                    "النتيجة": f"{eps_growth:.1f}%",
                    "طريقة الحساب": "متوسط نمو صافي الدخل السنوي لآخر سنوات",
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
                    "النتيجة": "سليم" if inv_growth < rev_growth else "خطر",
                    "طريقة الحساب": "مقارنة نمو المخزون بنمو المبيعات",
                    "معيار بيتر لينش": "نمو المخزون < نمو المبيعات",
                    "الشرح": "تراكم المخزون أسرع من المبيعات يعني ركوداً."
                },
                {
                    "المؤشر": "النقد الصافي",
                    "النتيجة": f"{net_cash/1e6:.1f}M",
                    "طريقة الحساب": "إجمالي الكاش - إجمالي الديون",
                    "معيار بيتر لينش": "يجب أن يكون موجباً (وسادة أمان)",
                    "الشرح": "الكاش الفائض يقلل من التكلفة الفعلية للسهم."
                },
                {
                    "المؤشر": "جودة الأرباح (FCF)",
                    "النتيجة": f"{fcf_to_profit:.2f}",
                    "طريقة الحساب": "التدفق النقدي الحر ÷ صافي الربح",
                    "معيار بيتر لينش": "أكبر من 1.0",
                    "الشرح": "يؤكد أن الأرباح كاش حقيقي وليست أرقاماً محاسبية."
                }
            ]

            # عرض النتائج في جدول احترافي
            df = pd.DataFrame(data)
            st.table(df)

            # تقييم سريع
            score = 0
            if 0 < peg < 1: score += 40
            if 15 < eps_growth < 35: score += 30
            if de_ratio < 35: score += 30
            
            st.subheader(f"📊 درجة المطابقة التقريبية: {score}%")

    except Exception as e:
        st.error(f"بيانات ناقصة لهذا السهم: {e}")
