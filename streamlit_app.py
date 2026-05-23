import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go

# إعدادات الصفحة العامة للتطبيق
st.set_page_config(page_title="رادار أسهم ناسداك", layout="wide")

st.title("📈 تطبيق رادار ومؤشرات سوق الأسهم الأمريكية (NASDAQ)")
st.markdown("هذا التطبيق يحلل الأسهم تلقائياً بناءً على استراتيجية المتوسط المتحرك لشهر 20 يوم")

# شريط جانبي لإدخال الأسهم
st.sidebar.header("إعدادات المراقبة")
symbols_input = st.sidebar.text_input("أدخل رموز الأسهم تفصل بينها فاصلة:", "AAPL,MSFT,NVDA,AMZN,GOOGL,AUR")
symbols = [s.strip().upper() for s in symbols_input.split(",")]

# زر لتحديث البيانات
if st.sidebar.button("تحديث الفحص الآلي 🔄"):
    st.rerun()

st.subheader("🔍 جدول الإشارات الحالي للفحص والفرز")

# مصفوفة لتخزين نتائج الفحص
results = []

for ticker in symbols:
    try:
        data = yf.download(ticker, period="3mo", interval="1d", progress=False)
        data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]

        if data.empty: 
            continue  
              
        data['SMA_20'] = ta.sma(data['Close'], length=20)  
        current_price = float(data['Close'].iloc[-1])  
        sma_value = float(data['SMA_20'].iloc[-1])  
          
        if current_price > sma_value:  
            signal = "🟢 شراء (Buy)"  
        else:  
            signal = "🔴 انتظار (Wait)"  
              
        results.append({  
            "السهم": ticker,  
            "السعر الحالي ($)": round(current_price, 2),  
            "المتوسط SMA20 ($)": round(sma_value, 2),  
            "الإشارة الفنية": signal  
        })  
    except:  
        pass

# عرض جدول البيانات داخل التطبيق بشكل أنيق
if results:
    st.table(results)
else:
    st.warning("لم يتم العثور على بيانات. تحقق من رموز الأسهم.")

# قسم لعرض رسم بياني تفصيلي لسهم معين يختاره المستخدم
st.write("---")
st.subheader("📊 الرسم البياني التفصيلي للأسهم")
selected_ticker = st.selectbox("اختر سهماً لعرض التشارت الخاص به بشكل تفاعلي:", symbols)

if selected_ticker:
    try:
        plot_data = yf.download(selected_ticker, period="6mo", interval="1d", progress=False)
        plot_data.columns = [col[0] if isinstance(col, tuple) else col for col in plot_data.columns]
        plot_data['SMA_20'] = ta.sma(plot_data['Close'], length=20)

        fig = go.Figure()  
        fig.add_trace(go.Candlestick(x=plot_data.index, open=plot_data['Open'], high=plot_data['High'],  
                                     low=plot_data['Low'], close=plot_data['Close'], name='السعر'))  
        fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data['SMA_20'], name='متوسط 20 يوم', line=dict(color='blue')))  
        fig.update_layout(title=f"حركة سهم {selected_ticker}", yaxis_title="السعر ($)", xaxis_rangeslider_visible=False)  
          
        st.plotly_chart(fig, use_container_width=True)  
    except Exception as e:  
        st.error(f"تعذر رسم تشارت السهم: {e}")
      
