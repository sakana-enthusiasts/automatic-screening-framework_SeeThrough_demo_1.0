from pathlib import Path

from streamlit.testing.v1 import AppTest

from 核心系统.流程控制器 import 创建补充数据3流程控制器


项目根目录 = Path(__file__).resolve().parents[2]


def test_规则筛选页面展示真实统计候选和标签审计() -> None:
    创建补充数据3流程控制器(项目根目录).执行补充数据2规则筛选流程()
    应用 = AppTest.from_file(str(项目根目录 / "启动程序.py"))
    应用.run(timeout=30)
    应用.radio[0].set_value("规则筛选").run(timeout=30)
    assert any(组件.label == "清理后真实候选" and str(组件.value) == "1619" for 组件 in 应用.metric)
    assert any(组件.label == "论文最终10恢复" and str(组件.value) == "10/10" for 组件 in 应用.metric)
    assert len(应用.dataframe) >= 3
