import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.title("📊 통계 수업: 데이터 탐구 & 시각화 연습 앱")

st.write("""
이 앱은 통계 수업 시간에 **데이터를 탐구하고 다양한 시각화를 직접 실습**할 수 있도록 만들어졌어요!  
구글 시트 데이터를 자동으로 불러오고 기초 통계량, 히스토그램, 상자그림, 산점도 등 다양한 그래프를 제공합니다.  
""")

# 1. 구글 시트 URL (고정 입력)
sheet_url = "https://docs.google.com/spreadsheets/d/1dCdajzIRGXOGPsbcp16ig2Z4aoTRGCUK51Rwfhv8Nbk/edit?gid=0#gid=0"

def convert_to_csv_url(url: str):
    if "edit?gid=" in url:
        base = url.split("/edit")[0]
        gid = url.split("gid=")[1]
        return f"{base}/export?format=csv&gid={gid}"
    return url

csv_url = convert_to_csv_url(sheet_url)

# 2. 데이터 불러오기
try:
    df = pd.read_csv(csv_url)
    st.success("구글 시트에서 데이터를 성공적으로 불러왔어요! 🎉")
except Exception as e:
    st.error("데이터 불러오기 실패… 구글시트 공유 설정을 확인해주세요.")
    st.stop()

st.subheader("📄 불러온 데이터 미리보기")
st.dataframe(df)

numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

if len(numeric_cols) == 0:
    st.error("수치형 데이터가 없어 시각화를 할 수 없어요 😢")
    st.stop()

# ===============================================
# 3. 기초 통계량
# ===============================================
st.subheader("📌 기초 통계량 요약")

selected_col = st.selectbox("기초 통계량을 볼 수치를 선택하세요", numeric_cols)

desc = df[selected_col].describe()
st.write(desc)

# ===============================================
# 4. 히스토그램
# ===============================================
st.subheader("📊 히스토그램")

bin_count = st.slider("막대 개수 (Bins)", 5, 50, 20)

hist = (
    alt.Chart(df)
    .mark_bar()
    .encode(
        x=alt.X(f"{selected_col}:Q", bin=alt.Bin(maxbins=bin_count)),
        y='count()'
    )
    .properties(height=300)
)
st.altair_chart(hist, use_container_width=True)

# ===============================================
# 5. 여러 변수 상자그림 비교
# ===============================================
st.subheader("🟦 여러 변수 상자그림(Boxplot) 비교")

multi_cols = st.multiselect(
    "상자그림으로 비교할 변수를 선택하세요 (여러 개 선택 가능)",
    numeric_cols,
    default=numeric_cols[:2] if len(numeric_cols) > 1 else numeric_cols
)

if len(multi_cols) == 0:
    st.warning("최소 한 개 이상의 변수를 선택해주세요!")
else:
    # 데이터를 long-form으로 변환 (Altair boxplot 용)
    df_melt = df[multi_cols].melt(var_name="변수", value_name="값")

    box_multi = (
        alt.Chart(df_melt)
        .mark_boxplot()
        .encode(
            x="변수:N",
            y="값:Q",
            color="변수:N"
        )
        .properties(height=350)
    )

    st.altair_chart(box_multi, use_container_width=True)


# ===============================================
# 6. 산점도(두 변수 선택)
# ===============================================
st.subheader("🔵 산점도 (Scatter Plot)")

x_col = st.selectbox("X축 선택", numeric_cols, index=0)
y_col = st.selectbox("Y축 선택", numeric_cols, index=1 if len(numeric_cols) > 1 else 0)

scatter = (
    alt.Chart(df)
    .mark_circle(size=70)
    .encode(
        x=x_col,
        y=y_col,
        tooltip=numeric_cols
    )
    .properties(height=350)
)

st.altair_chart(scatter, use_container_width=True)

st.write("✨ 자유롭게 변수를 바꿔보면서 데이터의 분포와 관계를 탐구해보세요!")
