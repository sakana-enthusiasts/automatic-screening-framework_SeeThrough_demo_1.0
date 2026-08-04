"""通用候选导入：选择应用配置、逐条控制规则并展示 run_id 结果。"""

from pathlib import Path

import streamlit as st

from 核心系统.流程控制器 import 创建颅骨透明化筛选流程控制器
from 核心系统.运行数据管理 import 运行数据管理器
from 核心系统.通用规则引擎 import 规则注册表
from 插件.数据导入.通用候选表导入插件 import 通用候选表导入插件


项目根目录 = Path(__file__).resolve().parents[1]


def 渲染用户候选导入页面() -> None:
    st.header("用户候选导入与配置化筛选")
    st.caption("仅支持 CSV/XLSX；每次运行生成独立 run_id，原始文件和全部结果均存入该运行目录。")
    上传 = st.file_uploader("选择候选表", type=["csv", "xlsx"])
    if 上传 is None:
        return
    内容 = 上传.getvalue()
    try:
        预览 = 通用候选表导入插件.读取上传内容(上传.name, 内容)
    except Exception as 错误:
        st.error(f"无法读取文件：{错误}")
        return
    st.subheader("字段映射预览")
    st.dataframe(预览.head(20), use_container_width=True, hide_index=True)
    选项 = ["不映射"] + list(预览.columns)
    候选类型 = st.radio("候选类型", ["水相候选（wRIMS）", "有机相候选（oRIMS）", "通用候选"], horizontal=True)
    名称列 = st.selectbox("化学名称列", 选项, index=1 if len(选项) > 1 else 0)
    CAS列 = st.selectbox("CAS列", 选项)
    货号列 = st.selectbox("货号列", 选项)
    编号列 = st.selectbox("用户候选编号列（不选则自动生成）", 选项)
    st.subheader("可选物化字段映射")
    可选 = {
        "水合能力平均值列": "水合评分平均值", "水合能力标准差列": "水合评分标准差", "eRI列": "eRI", "pH列": "预测pH",
        "dD列": "dD", "dP列": "dP", "dH列": "dH", "实测RI列": "实测RI", "气味列": "气味",
        "毒性或安全性列": "毒性或安全性", "实际互溶状态列": "实际互溶状态",
    }
    物化映射 = {键: (None if (列 := st.selectbox(标签, 选项, key=键)) == "不映射" else 列) for 键, 标签 in 可选.items()}
    注册表 = 规则注册表.默认()
    配置选项 = {配置.配置名称: 配置.配置编号 for 配置 in 注册表.配置列表()}
    st.subheader("应用配置与规则")
    配置名称 = st.selectbox("应用配置", list(配置选项))
    配置编号 = 配置选项[配置名称]
    规则启用覆盖 = {}
    for 规则 in 注册表.规则列表(配置编号):
        规则启用覆盖[规则.规则编号] = st.checkbox(
            f"{规则.规则编号}｜{规则.规则名称}（{规则.缺失数据策略}）",
            value=规则.是否启用,
            key=f"规则_{配置编号}_{规则.规则编号}",
        )
    st.caption("规则未启用时输出“跳过”；启用但属性缺失时输出“无法评估”，不会将缺失当作 0、通过或排除。")
    if st.button("保存并运行候选筛选", type="primary"):
        if 名称列 == "不映射":
            st.error("必须指定化学名称列")
            return
        映射 = {
            "化学名称列": 名称列,
            "CAS列": None if CAS列 == "不映射" else CAS列,
            "货号列": None if 货号列 == "不映射" else 货号列,
            "候选编号列": None if 编号列 == "不映射" else 编号列,
            **物化映射,
        }
        设置 = {"应用配置": 配置编号, "规则启用覆盖": 规则启用覆盖, "允许网络身份查询": False}
        try:
            with st.spinner("正在创建独立运行并执行身份、结构、属性与规则步骤…"):
                摘要 = 创建颅骨透明化筛选流程控制器(项目根目录).执行用户候选导入(上传.name, 内容, 映射, 设置, 候选类型, 配置编号)
            st.session_state["当前用户筛选run_id"] = 摘要["run_id"]
            st.success(f"运行完成：{摘要['run_id']}；规则通过 {摘要['规则通过数']}；无法评估 {摘要['无法评估数']}。")
            st.caption(f"报告：{摘要['报告路径']}")
        except Exception as 错误:
            st.error(f"运行失败：{错误}")
    run_id = st.session_state.get("当前用户筛选run_id")
    if run_id:
        管理器 = 运行数据管理器(项目根目录)
        try:
            管理器.激活运行(run_id)
            结果 = 管理器.读取筛选结果("用户导入_规则筛选结果")
            st.subheader(f"运行结果：{run_id}")
            st.dataframe(结果, use_container_width=True, hide_index=True)
        except FileNotFoundError:
            st.info("当前运行尚未生成筛选结果。")
