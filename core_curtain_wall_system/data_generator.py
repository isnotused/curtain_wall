import numpy as np
import pandas as pd

def generate_basic_parameters(num_samples=50):
    """生成幕墙设计基础参数信息，用于参数输入处理模块"""
    # 生成单元件尺寸约束参数
    width = np.random.uniform(0.5, 2.0, num_samples)  # 宽度，单位：米
    height = np.random.uniform(1.0, 3.5, num_samples)  # 高度，单位：米
    thickness = np.random.uniform(0.1, 0.3, num_samples)  # 厚度，单位：米
    
    # 生成建筑立面形态特征
    curvature = np.random.uniform(-0.5, 0.5, num_samples)  # 曲率
    inclination = np.random.uniform(0, 15, num_samples)  # 倾斜角度，单位：度
    
    # 生成材料参数
    material_strength = np.random.uniform(200, 400, num_samples)  # 材料强度，单位：MPa
    density = np.random.uniform(2500, 3000, num_samples)  # 密度，单位：kg/m³
    
    # 组合成数据框
    params_df = pd.DataFrame({
        '样本编号': range(1, num_samples + 1),
        '宽度(m)': width,
        '高度(m)': height,
        '厚度(m)': thickness,
        '曲率': curvature,
        '倾斜角度(度)': inclination,
        '材料强度(MPa)': material_strength,
        '密度(kg/m³)': density
    })
    
    return params_df

def generate_association_rules():
    """生成参数关联规则数据"""
    rules = {
        '宽度与高度比': {'最小值': 0.3, '最大值': 0.8},
        '厚度与宽度比': {'最小值': 0.05, '最大值': 0.2},
        '曲率与倾斜角度关系': {'系数': 0.03},
        '材料强度与厚度关系': {'系数': 150}
    }
    return rules

def generate_construction_data(num_samples=50):
    """生成施工数据"""
    construction_time = np.random.uniform(2, 8, num_samples)  # 施工时间，单位：小时
    labor_cost = np.random.uniform(500, 1500, num_samples)  # 人工成本，单位：元
    material_cost = np.random.uniform(1000, 3000, num_samples)  # 材料成本，单位：元
    
    construction_df = pd.DataFrame({
        '样本编号': range(1, num_samples + 1),
        '施工时间(小时)': construction_time,
        '人工成本(元)': labor_cost,
        '材料成本(元)': material_cost
    })
    
    return construction_df