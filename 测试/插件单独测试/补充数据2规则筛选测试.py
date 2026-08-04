from pathlib import Path

from 核心系统.流程控制器 import 创建补充数据3流程控制器


项目根目录 = Path(__file__).resolve().parents[2]


def test_补充数据2自动数值规则保留20个并恢复论文最终10个() -> None:
    控制器 = 创建补充数据3流程控制器(项目根目录)
    控制器.执行补充数据2规则筛选流程()
    记录 = 控制器.数据管理器.读取最终结果("补充数据2_规则筛选统一记录")
    自动通过 = 记录["自动规则通过"].astype(str).str.lower().eq("true")
    最终10 = 记录["论文最终10候选标签"].eq("是")
    assert int(自动通过.sum()) == 20
    assert int((自动通过 & 最终10).sum()) == 10
    assert int((自动通过 & ~最终10).sum()) == 10
    assert 记录.loc[最终10, "论文最终10对照状态"].eq("已由自动规则恢复").all()
    assert 记录.loc[~自动通过, "自动排除原因"].ne("").all()
