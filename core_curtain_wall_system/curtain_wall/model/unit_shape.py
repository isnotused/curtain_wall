from model.geometric_element import GeometricElement
from model.shape_generation_logic import ShapeGenerationLogic

class UnitShape:
    """单元件形态生成结果实体"""
    def __init__(self):
        self.shape_id = "" 
        self.几何要素 = []  
        self.生成逻辑 = None  
        self.动态特征值 = 0.0  