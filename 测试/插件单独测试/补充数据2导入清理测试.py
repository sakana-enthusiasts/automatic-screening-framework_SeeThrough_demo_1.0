from pathlib import Path

from 核心系统.流程控制器 import 创建补充数据3流程控制器


项目根目录 = Path(__file__).resolve().parents[2]


def test_补充数据2清理后严格得到1619个候选() -> None:
    控制器 = 创建补充数据3流程控制器(项目根目录)
    控制器.执行补充数据2规则筛选流程()
    审计 = 控制器.数据管理器.读取中间结果("补充数据2_导入清理审计")
    记录 = 控制器.数据管理器.读取最终结果("补充数据2_规则筛选统一记录")
    assert int(审计.loc[审计["项目"].eq("原始数据行数"), "数量"].iloc[0]) == 1632
    assert int(审计.loc[审计["项目"].eq("副表头行"), "数量"].iloc[0]) == 1
    assert int(审计.loc[审计["项目"].eq("C# 对照/非候选行"), "数量"].iloc[0]) == 12
    assert len(记录) == 1619
    assert 记录["候选编号"].str.fullmatch(r"#\d{4}").all()
