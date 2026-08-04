from pathlib import Path

from 核心系统.流程控制器 import 创建补充数据3流程控制器


项目根目录 = Path(__file__).resolve().parents[2]


def test_补充数据3所有真实试剂均有经核对的可读结构() -> None:
    控制器 = 创建补充数据3流程控制器(项目根目录)
    控制器.执行补充数据3真实流程()
    结构结果 = 控制器.数据管理器.读取中间结果("补充数据3_结构映射结果")
    assert len(结构结果) == 12
    assert 结构结果["结构状态"].eq("已获得").all()
    assert 结构结果["结构映射_来源URL"].str.startswith("https://pubchem.ncbi.nlm.nih.gov/compound/").all()
    assert 结构结果["结构映射_人工核对状态"].str.contains("CAS").all()
