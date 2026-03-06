"""
数据模型定义
Method Development Agent - MVP
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class ExperimentStatus(Enum):
    """实验状态"""
    DRAFT = "草稿"
    IN_PROGRESS = "进行中"
    COMPLETED = "已完成"
    FAILED = "失败"


class ColumnType(Enum):
    """色谱柱类型"""
    C18 = "C18 (反相)"
    C8 = "C8 (反相)"
    PHENYL = "苯基柱"
    HILIC = "HILIC"
    NORMAL_PHASE = "正相"


@dataclass
class Compound:
    """化合物信息"""
    id: Optional[int] = None
    name: str = ""
    cas_number: str = ""
    molecular_formula: str = ""
    mw: float = 0.0
    pka: Optional[float] = None
    logp: Optional[float] = None
    notes: str = ""
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'cas_number': self.cas_number,
            'molecular_formula': self.molecular_formula,
            'mw': self.mw,
            'pka': self.pka,
            'logp': self.logp,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


@dataclass
class ChromatographicMethod:
    """色谱方法"""
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    
    # 色谱条件
    column_type: str = ""
    column_model: str = ""
    column_dimensions: str = ""  # e.g., "4.6×150mm, 5μm"
    
    mobile_phase_a: str = ""
    mobile_phase_b: str = ""
    gradient_program: str = ""  # e.g., "10-90%B in 20min"
    
    flow_rate: float = 1.0  # mL/min
    column_temperature: float = 30.0  # °C
    injection_volume: float = 10.0  # μL
    detection_wavelength: Optional[float] = None  # nm
    detection_method: str = "UV"  # UV, MS, etc.
    
    # 元数据
    target_compound: str = ""  # 主要目标化合物
    sample_matrix: str = ""  # 样品基质
    created_by: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tags: str = ""  # 逗号分隔的标签
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'column_type': self.column_type,
            'column_model': self.column_model,
            'column_dimensions': self.column_dimensions,
            'mobile_phase_a': self.mobile_phase_a,
            'mobile_phase_b': self.mobile_phase_b,
            'gradient_program': self.gradient_program,
            'flow_rate': self.flow_rate,
            'column_temperature': self.column_temperature,
            'injection_volume': self.injection_volume,
            'detection_wavelength': self.detection_wavelength,
            'detection_method': self.detection_method,
            'target_compound': self.target_compound,
            'sample_matrix': self.sample_matrix,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'tags': self.tags
        }


@dataclass
class Experiment:
    """实验记录"""
    id: Optional[int] = None
    method_id: Optional[int] = None
    experiment_number: str = ""  # e.g., "EXP-20240226-001"
    
    # 基本信息
    title: str = ""
    objective: str = ""  # 实验目的
    operator: str = ""
    
    # 实验条件（可能偏离标准方法）
    actual_conditions: str = ""  # JSON格式存储实际使用的条件
    
    # 样品信息
    sample_name: str = ""
    sample_batch: str = ""
    sample_preparation: str = ""  # 样品前处理方法
    
    # 结果
    chromatogram_file: str = ""  # 色谱图文件路径
    result_summary: str = ""  # 结果摘要
    
    # 性能指标
    retention_time: Optional[float] = None
    resolution: Optional[float] = None
    theoretical_plates: Optional[int] = None
    tailing_factor: Optional[float] = None
    sn_ratio: Optional[float] = None
    
    # 评估
    status: str = "draft"  # draft, completed, failed
    success_rating: int = 0  # 1-5
    observations: str = ""  # 观察记录
    next_steps: str = ""  # 下一步计划
    
    # 时间戳
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'method_id': self.method_id,
            'experiment_number': self.experiment_number,
            'title': self.title,
            'objective': self.objective,
            'operator': self.operator,
            'sample_name': self.sample_name,
            'sample_batch': self.sample_batch,
            'status': self.status,
            'success_rating': self.success_rating,
            'observations': self.observations,
            'next_steps': self.next_steps,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
