from pathlib import Path

from 核心系统.流程控制器 import 创建补充数据3流程控制器


项目根目录 = Path(__file__).resolve().parents[2]


def test_RDKit为补充数据3全部真实试剂计算必需描述符() -> None:
    控制器 = 创建补充数据3流程控制器(项目根目录)
    控制器.执行补充数据3真实流程()
    描述符 = 控制器.数据管理器.读取中间结果("补充数据3_RDKit描述符结果")
    必需描述符 = {"分子量", "脂水分配指标_MolLogP", "极性表面积_TPSA", "氢键供体数", "氢键受体数", "芳香环数量", "可旋转键数量", "芳香性", "基础官能团"}
    assert 描述符["候选编号"].nunique() == 12
    assert 必需描述符.issubset(set(描述符["描述符名称"]))
    assert 描述符["是否计算成功"].astype(str).str.lower().eq("true").all()
    assert 描述符["工具版本"].notna().all()
