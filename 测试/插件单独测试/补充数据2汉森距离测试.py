from math import isclose, sqrt
from pathlib import Path

from 核心系统.流程控制器 import 创建补充数据3流程控制器


项目根目录 = Path(__file__).resolve().parents[2]


def test_补充数据2数值初筛候选均计算BA和VA汉森距离() -> None:
    控制器 = 创建补充数据3流程控制器(项目根目录)
    控制器.执行补充数据2规则筛选流程()
    距离 = 控制器.数据管理器.读取中间结果("补充数据2_汉森距离结果")
    assert len(距离) == 82
    assert 距离["候选编号"].nunique() == 41
    assert set(距离["参照试剂编号"]) == {"BA", "VA"}
    行 = 距离.loc[(距离["候选编号"].eq("#0093")) & (距离["参照试剂编号"].eq("BA"))].iloc[0]
    预期 = sqrt(4 * (行["候选_dD"] - 行["参照_dD"]) ** 2 + (行["候选_dP"] - 行["参照_dP"]) ** 2 + (行["候选_dH"] - 行["参照_dH"]) ** 2)
    assert isclose(行["汉森距离_Ra"], 预期, rel_tol=0, abs_tol=1e-6)
