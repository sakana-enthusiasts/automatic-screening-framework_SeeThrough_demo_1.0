from pathlib import Path

from 核心系统.流程控制器 import 创建补充数据3流程控制器


项目根目录 = Path(__file__).resolve().parents[2]


def test_补充数据3真实导入为12条统一候选基础记录() -> None:
    控制器 = 创建补充数据3流程控制器(项目根目录)
    控制器.执行补充数据3真实流程()
    记录 = 控制器.数据管理器.读取中间结果("补充数据3_统一候选基础记录")
    assert len(记录) == 12
    assert set(记录.loc[记录["试剂角色"].eq("有机相参照"), "候选编号"]) == {"BA", "VA"}
    assert int(记录["试剂角色"].eq("水相候选").sum()) == 10
    assert set(["论文_dD", "论文_dP", "论文_dH"]).issubset(记录.columns)
