from pathlib import Path

from 核心系统.流程控制器 import 创建补充数据3流程控制器


项目根目录 = Path(__file__).resolve().parents[2]


def test_统一记录保留论文结构RDKit与汉森来源字段() -> None:
    控制器 = 创建补充数据3流程控制器(项目根目录)
    控制器.执行补充数据3真实流程()
    统一记录 = 控制器.数据管理器.读取最终结果("补充数据3_化学属性统一记录")
    必需列 = {"论文_dD", "结构映射_SMILES", "RDKit_分子量", "汉森距离_与BA", "汉森距离_与VA", "论文原始字段来源", "分子结构来源", "RDKit描述符来源", "汉森距离来源", "缺失状态", "错误信息"}
    assert len(统一记录) == 12
    assert 必需列.issubset(统一记录.columns)
    assert 统一记录["论文原始字段来源"].eq("SeeThrough Supplementary Data 3").all()
    assert 统一记录["结构映射_SMILES"].notna().all()
