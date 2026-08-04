"""展示毒性证据，不合成跨物种/途径的安全总分。"""

from pathlib import Path
import pandas as pd
import streamlit as st

from 核心系统.数据管理接口 import 文件数据访问管理器

项目根目录 = Path(__file__).resolve().parents[1]


def _读(管理器: 文件数据访问管理器, 标识: str):
    try:
        return 管理器.读取筛选结果(标识)
    except FileNotFoundError:
        return None


def 渲染毒性评估页面() -> None:
    st.header("毒性证据与模式视图")
    st.caption("GHS仅为危险提示；人、鼠、体内、体外、预测结果不合并为单一安全分数。当前实验给药途径尚未配置，软件不会猜测。")
    管理器 = 文件数据访问管理器(项目根目录)
    st.subheader("当前实验条件（默认未配置，不作推断）")
    with st.form("实验条件"):
        物种 = st.selectbox("当前实验物种", ["未配置", "小鼠", "大鼠", "其他"])
        途径 = st.text_input("当前给药途径")
        时长 = st.text_input("暴露时长")
        模式 = st.selectbox("单次或重复暴露", ["未配置", "单次", "重复"])
        终点 = st.text_input("主要关注终点")
        if st.form_submit_button("保存实验条件"):
            管理器.保存软件数据库表格("当前实验条件.csv", pd.DataFrame([{"当前实验物种": "" if 物种 == "未配置" else 物种, "当前给药途径": 途径, "暴露时长": 时长, "暴露模式": "" if 模式 == "未配置" else 模式, "主要关注终点": 终点}]))
            st.success("已保存。下次重新运行完整筛选时会按此条件生成相关性视图。")
    证据 = _读(管理器, "毒性原始证据")
    if 证据 is None:
        st.info("请先在“规则筛选”页面重跑完整筛选，以生成20个自动候选的毒性证据框架。")
        return
    for 标题, 标识 in [("20个候选毒性原始证据", "毒性原始证据"), ("当前动物实验模式", "当前动物实验模式结果"), ("未来人体口服模式", "未来人体口服模式结果"), ("项目基准物比较", "项目基准物清单"), ("数据缺口", "当前动物实验模式结果"), ("毒性终点字典", "毒性终点字典"), ("证据相关性优先级", "毒性证据相关性优先级表")]:
        数据 = _读(管理器, 标识)
        if 数据 is not None:
            st.subheader(标题)
            st.dataframe(数据, use_container_width=True, hide_index=True)
    try:
        状态 = 管理器.读取中间结果("CompTox毒性查询状态")
        st.subheader("CompTox接口状态")
        st.dataframe(状态, use_container_width=True, hide_index=True)
    except FileNotFoundError:
        pass
