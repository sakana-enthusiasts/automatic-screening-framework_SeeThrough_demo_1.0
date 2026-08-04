"""读取已匹配的PubChem身份，并保存GHS危险提示为独立毒性证据。"""

from datetime import datetime, timezone
import json
import re
from typing import Any

import pandas as pd
import requests

from 插件.插件接口 import 基础插件接口


class PubChem查询插件(基础插件接口):
    插件标识 = "PubChem查询"
    输出标识 = "PubChem_GHS毒性证据"
    缓存文件 = "PubChem_GHS缓存.csv"

    @staticmethod
    def _提取文本(对象: Any) -> list[str]:
        if isinstance(对象, dict):
            输出 = []
            for 键, 值 in 对象.items():
                if 键 in {"String", "Description", "Name"} and isinstance(值, str):
                    输出.append(值)
                输出.extend(PubChem查询插件._提取文本(值))
            return 输出
        if isinstance(对象, list):
            return [文本 for 值 in 对象 for 文本 in PubChem查询插件._提取文本(值)]
        return []

    def _GHS(self, CID: str) -> tuple[dict[str, str], str]:
        地址 = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{CID}/JSON?heading=GHS%20Classification"
        响应 = requests.get(地址, timeout=20)
        if 响应.status_code == 404:
            return {}, "未找到GHS条目"
        响应.raise_for_status()
        原始 = 响应.json()
        文本 = self._提取文本(原始)
        # 只识别形如 H300/H314 的正式危险代码；说明文字、ECHA介绍等不会误入。
        代码 = sorted({值 for 片段 in 文本 for 值 in re.findall(r"\bH\d{3}\b", 片段)})
        说明 = [片段 for 片段 in 文本 if re.search(r"\bH\d{3}\b", 片段)]
        信号词 = sorted({值 for 片段 in 文本 for 值 in re.findall(r"\b(?:Danger|Warning)\b", 片段, flags=re.I)})
        类别 = [片段 for 片段 in 文本 if re.search(r"(?:Acute Toxicity|Skin Corrosion|Eye Damage|Carcinogenicity|Reproductive Toxicity|Specific Target Organ|Flammable)", 片段, flags=re.I)]
        比例 = sorted({值 for 片段 in 文本 for 值 in re.findall(r"\b\d+(?:\.\d+)?%", 片段)})
        来源 = sorted({片段 for 片段 in 文本 if re.search(r"(?:ECHA|EPA|European Chemicals Agency|submission|notifier)", 片段, flags=re.I)})
        return {"H代码": "; ".join(代码), "危险说明": " | ".join(dict.fromkeys(说明))[:3000], "信号词": "; ".join(信号词), "危险类别": " | ".join(dict.fromkeys(类别))[:2000], "报告比例": "; ".join(比例), "提交来源": " | ".join(dict.fromkeys(来源))[:1500], "是否存在不同来源冲突": "是" if len(代码) > 1 else "未见明确冲突", "原始响应": json.dumps(原始, ensure_ascii=False)[:30000]}, ""

    def 执行(self, 数据上下文: dict[str, Any]) -> pd.DataFrame:
        数据管理器 = 数据上下文["数据管理器"]
        身份 = 数据管理器.读取中间结果("补充数据2_41候选身份映射")
        筛选 = 数据管理器.读取筛选结果("补充数据2_规则筛选统一记录")
        最终 = 筛选[筛选["自动规则通过"].astype(str).str.lower().eq("true")][["候选编号", "论文_CAS号"]]
        表 = 最终.merge(身份, on="候选编号", how="left", suffixes=("", "_身份"))
        try:
            缓存 = 数据管理器.读取软件数据库表格(self.缓存文件)
        except FileNotFoundError:
            缓存 = pd.DataFrame(columns=["PubChem CID", "GHS结果", "查询错误", "查询时间"])
        缓存索引 = {str(行["PubChem CID"]): 行.to_dict() for _, 行 in 缓存.iterrows()} if not 缓存.empty else {}
        记录 = []
        for _, 行 in 表.iterrows():
            结构化结果, 错误 = {}, ""
            CID = str(行.get("PubChem CID", ""))
            缓存值 = 缓存索引.get(CID)
            if 缓存值:
                结构化结果 = {键: str(缓存值.get(键, "")) for 键 in ["H代码", "危险说明", "信号词", "危险类别", "报告比例", "提交来源", "是否存在不同来源冲突", "原始响应"]}
                错误 = str(缓存值.get("查询错误", ""))
            elif 数据上下文.get("启用网络毒性查询") and CID:
                try:
                    结构化结果, 错误 = self._GHS(CID)
                except Exception as 异常:
                    错误 = f"查询失败：{type(异常).__name__}: {异常}"
            else:
                错误 = "本次未执行网络查询；GHS仅作危险提示，不等同于实验风险"
            缓存索引[CID] = {"PubChem CID": CID, **结构化结果, "查询错误": 错误, "查询时间": datetime.now(timezone.utc).isoformat()}
            记录.append({"候选编号": 行["候选编号"], "CAS": 行.get("论文_CAS号", 行.get("原始CAS", "")), "PubChem CID": CID, "InChIKey": 行.get("InChIKey", ""), "化合物形式": "盐/水合物/混合物状态见身份映射", "毒性终点": "GHS危险提示", "物种": "不适用", "细胞或组织来源": "不适用", "给药途径": "不适用", "剂量": "", "剂量单位": "", "暴露时长": "", "观察时长": "", "结果": 结构化结果.get("危险说明", "") or 错误, "实验值或预测值": "数据库汇总", "原始数据、数据库汇总或模型预测": "数据库汇总", "数据来源": "PubChem PUG-View GHS Classification", "原始来源链接或编号": f"https://pubchem.ncbi.nlm.nih.gov/compound/{CID}" if CID else "", "可信度": "GHS危险提示；需追溯原始来源", "数据是否与当前实验条件匹配": "否/不适用", "备注": "GHS不自动作为实验风险或淘汰规则", "查询状态": "已查询" if bool(结构化结果.get("H代码") or 结构化结果.get("危险说明")) else "尚未查询或无结果", **结构化结果})
        证据 = pd.DataFrame(记录)
        数据管理器.保存软件数据库表格(self.缓存文件, pd.DataFrame(缓存索引.values()))
        数据管理器.保存中间结果(self.输出标识, 证据)
        return 证据
