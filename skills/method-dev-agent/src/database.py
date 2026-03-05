"""
数据库操作模块
Method Development Agent - MVP
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

try:
    from models import Compound, ChromatographicMethod, Experiment
except ImportError:
    from src.models import Compound, ChromatographicMethod, Experiment


class Database:
    """SQLite数据库管理类"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # 默认存储在项目data目录
            current_dir = Path(__file__).parent.parent
            db_path = current_dir / "data" / "method_dev.db"
        
        self.db_path = str(db_path)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 化合物表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS compounds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    cas_number TEXT,
                    molecular_formula TEXT,
                    mw REAL,
                    pka REAL,
                    logp REAL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 色谱方法表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS methods (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    column_type TEXT,
                    column_model TEXT,
                    column_dimensions TEXT,
                    mobile_phase_a TEXT,
                    mobile_phase_b TEXT,
                    gradient_program TEXT,
                    flow_rate REAL DEFAULT 1.0,
                    column_temperature REAL DEFAULT 30.0,
                    injection_volume REAL DEFAULT 10.0,
                    detection_wavelength REAL,
                    detection_method TEXT DEFAULT 'UV',
                    target_compound TEXT,
                    sample_matrix TEXT,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tags TEXT
                )
            """)
            
            # 实验记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS experiments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    method_id INTEGER,
                    experiment_number TEXT NOT NULL,
                    title TEXT,
                    objective TEXT,
                    operator TEXT,
                    actual_conditions TEXT,
                    sample_name TEXT,
                    sample_batch TEXT,
                    sample_preparation TEXT,
                    chromatogram_file TEXT,
                    result_summary TEXT,
                    retention_time REAL,
                    resolution REAL,
                    theoretical_plates INTEGER,
                    tailing_factor REAL,
                    sn_ratio REAL,
                    status TEXT DEFAULT 'draft',
                    success_rating INTEGER DEFAULT 0,
                    observations TEXT,
                    next_steps TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (method_id) REFERENCES methods(id)
                )
            """)
            
            conn.commit()
    
    # ========== 化合物操作 ==========
    
    def add_compound(self, compound: Compound) -> int:
        """添加化合物"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO compounds (name, cas_number, molecular_formula, mw, pka, logp, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (compound.name, compound.cas_number, compound.molecular_formula,
                  compound.mw, compound.pka, compound.logp, compound.notes))
            conn.commit()
            return cursor.lastrowid
    
    def get_compounds(self, search: str = None) -> List[Compound]:
        """获取化合物列表"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if search:
                cursor.execute("""
                    SELECT * FROM compounds 
                    WHERE name LIKE ? OR cas_number LIKE ?
                    ORDER BY created_at DESC
                """, (f"%{search}%", f"%{search}%"))
            else:
                cursor.execute("SELECT * FROM compounds ORDER BY created_at DESC")
            
            rows = cursor.fetchall()
            return [self._row_to_compound(row) for row in rows]
    
    def _row_to_compound(self, row) -> Compound:
        """将数据库行转换为Compound对象"""
        return Compound(
            id=row['id'],
            name=row['name'],
            cas_number=row['cas_number'],
            molecular_formula=row['molecular_formula'],
            mw=row['mw'],
            pka=row['pka'],
            logp=row['logp'],
            notes=row['notes'],
            created_at=row['created_at']
        )
    
    # ========== 方法操作 ==========
    
    def add_method(self, method: ChromatographicMethod) -> int:
        """添加色谱方法"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO methods (
                    name, description, column_type, column_model, column_dimensions,
                    mobile_phase_a, mobile_phase_b, gradient_program,
                    flow_rate, column_temperature, injection_volume,
                    detection_wavelength, detection_method,
                    target_compound, sample_matrix, created_by, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (method.name, method.description, method.column_type, method.column_model,
                  method.column_dimensions, method.mobile_phase_a, method.mobile_phase_b,
                  method.gradient_program, method.flow_rate, method.column_temperature,
                  method.injection_volume, method.detection_wavelength, method.detection_method,
                  method.target_compound, method.sample_matrix, method.created_by, method.tags))
            conn.commit()
            return cursor.lastrowid
    
    def get_methods(self, search: str = None, column_type: str = None) -> List[ChromatographicMethod]:
        """获取方法列表"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM methods WHERE 1=1"
            params = []
            
            if search:
                query += " AND (name LIKE ? OR target_compound LIKE ? OR tags LIKE ?)"
                params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
            
            if column_type:
                query += " AND column_type = ?"
                params.append(column_type)
            
            query += " ORDER BY updated_at DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_method(row) for row in rows]
    
    def get_method_by_id(self, method_id: int) -> Optional[ChromatographicMethod]:
        """根据ID获取方法"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM methods WHERE id = ?", (method_id,))
            row = cursor.fetchone()
            return self._row_to_method(row) if row else None
    
    def _row_to_method(self, row) -> ChromatographicMethod:
        """将数据库行转换为ChromatographicMethod对象"""
        return ChromatographicMethod(
            id=row['id'],
            name=row['name'],
            description=row['description'],
            column_type=row['column_type'],
            column_model=row['column_model'],
            column_dimensions=row['column_dimensions'],
            mobile_phase_a=row['mobile_phase_a'],
            mobile_phase_b=row['mobile_phase_b'],
            gradient_program=row['gradient_program'],
            flow_rate=row['flow_rate'],
            column_temperature=row['column_temperature'],
            injection_volume=row['injection_volume'],
            detection_wavelength=row['detection_wavelength'],
            detection_method=row['detection_method'],
            target_compound=row['target_compound'],
            sample_matrix=row['sample_matrix'],
            created_by=row['created_by'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            tags=row['tags']
        )
    
    # ========== 实验记录操作 ==========
    
    def add_experiment(self, exp: Experiment) -> int:
        """添加实验记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO experiments (
                    method_id, experiment_number, title, objective, operator,
                    actual_conditions, sample_name, sample_batch, sample_preparation,
                    chromatogram_file, result_summary,
                    retention_time, resolution, theoretical_plates, tailing_factor, sn_ratio,
                    status, success_rating, observations, next_steps
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (exp.method_id, exp.experiment_number, exp.title, exp.objective, exp.operator,
                  exp.actual_conditions, exp.sample_name, exp.sample_batch, exp.sample_preparation,
                  exp.chromatogram_file, exp.result_summary,
                  exp.retention_time, exp.resolution, exp.theoretical_plates, 
                  exp.tailing_factor, exp.sn_ratio,
                  exp.status, exp.success_rating, exp.observations, exp.next_steps))
            conn.commit()
            return cursor.lastrowid
    
    def get_experiments(self, method_id: int = None, status: str = None, 
                       search: str = None) -> List[Experiment]:
        """获取实验记录列表"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM experiments WHERE 1=1"
            params = []
            
            if method_id:
                query += " AND method_id = ?"
                params.append(method_id)
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            if search:
                query += " AND (title LIKE ? OR sample_name LIKE ? OR operator LIKE ?)"
                params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
            
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_experiment(row) for row in rows]
    
    def get_experiment_by_id(self, exp_id: int) -> Optional[Experiment]:
        """根据ID获取实验记录"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM experiments WHERE id = ?", (exp_id,))
            row = cursor.fetchone()
            return self._row_to_experiment(row) if row else None
    
    def update_experiment(self, exp: Experiment):
        """更新实验记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE experiments SET
                    title = ?, objective = ?, operator = ?,
                    actual_conditions = ?, sample_name = ?, sample_batch = ?,
                    sample_preparation = ?, chromatogram_file = ?, result_summary = ?,
                    retention_time = ?, resolution = ?, theoretical_plates = ?,
                    tailing_factor = ?, sn_ratio = ?,
                    status = ?, success_rating = ?, observations = ?, next_steps = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (exp.title, exp.objective, exp.operator,
                  exp.actual_conditions, exp.sample_name, exp.sample_batch,
                  exp.sample_preparation, exp.chromatogram_file, exp.result_summary,
                  exp.retention_time, exp.resolution, exp.theoretical_plates,
                  exp.tailing_factor, exp.sn_ratio,
                  exp.status, exp.success_rating, exp.observations, exp.next_steps,
                  exp.id))
            conn.commit()
    
    def _row_to_experiment(self, row) -> Experiment:
        """将数据库行转换为Experiment对象"""
        return Experiment(
            id=row['id'],
            method_id=row['method_id'],
            experiment_number=row['experiment_number'],
            title=row['title'],
            objective=row['objective'],
            operator=row['operator'],
            actual_conditions=row['actual_conditions'],
            sample_name=row['sample_name'],
            sample_batch=row['sample_batch'],
            sample_preparation=row['sample_preparation'],
            chromatogram_file=row['chromatogram_file'],
            result_summary=row['result_summary'],
            retention_time=row['retention_time'],
            resolution=row['resolution'],
            theoretical_plates=row['theoretical_plates'],
            tailing_factor=row['tailing_factor'],
            sn_ratio=row['sn_ratio'],
            status=row['status'],
            success_rating=row['success_rating'],
            observations=row['observations'],
            next_steps=row['next_steps'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    # ========== 统计功能 ==========
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计数据"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            stats = {}
            cursor.execute("SELECT COUNT(*) FROM compounds")
            stats['compounds'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM methods")
            stats['methods'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM experiments")
            stats['experiments'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM experiments WHERE status = 'completed'")
            stats['completed_experiments'] = cursor.fetchone()[0]
            
            return stats
