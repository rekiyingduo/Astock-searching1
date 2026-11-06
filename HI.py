import streamlit as st
import akshare as ak
import pandas as pd

st.title("📈 A股行情查询工具")
st.write("数据来源：akshare（国内免费源，A股全覆盖）")

# A股代码：纯6位数字，不用加后缀
symbol = st.text_input("输入A股代码（例如 603111=康尼机电，600519=茅台）", value="603111")

start_date = st.text_input("开始日期（YYYYMMDD）", value="20250101")
end_date = st.text_input("结束日期（YYYYMMDD）", value="20251231")

if st.button("查询行情"):
    try:
        # ① 拉历史行情
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq"          # 前复权
        )

        if df.empty:
            st.error("没查到数据。请检查：①代码是否为纯6位数字；②日期区间内是否有交易日。")
        else:
            # ② 把"日期"列转成 datetime，并设为索引（这样图表横轴才是时间）
            df["日期"] = pd.to_datetime(df["日期"])
            df = df.set_index("日期")

            # ③ 基础信息（另一只接口，取公司概况）
            try:
                info = ak.stock_individual_info_em(symbol=symbol)
                # 返回的是两列：item / value，转成字典方便取值
                info_dict = dict(zip(info["item"], info["value"]))
                st.write(f"公司名称：{info_dict.get('股票简称', 'N/A')}")
                st.write(f"所属行业：{info_dict.get('行业', 'N/A')}")
                st.write(f"总市值：{info_dict.get('总市值', 'N/A')}")
                st.write(f"上市时间：{info_dict.get('上市时间', 'N/A')}")
            except Exception as e:
                st.warning(f"公司概况获取失败：{e}")

            # ④ 画收盘价折线图
            st.subheader("收盘价走势")
            st.line_chart(df["收盘"])

            # ⑤ 展示表格（akshare 返回中文列名）
            st.subheader("历史行情数据")
            st.dataframe(df[["开盘", "收盘", "最高", "最低", "成交量"]])

    except Exception as e:
        st.error(f"请求出错：{e}")
