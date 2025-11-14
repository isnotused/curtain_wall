import uuid
from model.parameter_input_dataset import ParameterInputDataSet
from model.unit_shape import UnitShape
from model.geometric_element import GeometricElement
from model.shape_generation_logic import ShapeGenerationLogic
from util.math_utils import normalize

class UnitGenerator:
    """单元件生成模块：基于参数生成单元件形态"""
    def generate(self, input_data_set: ParameterInputDataSet) -> UnitShape:
        unit_shape = UnitShape()
        unit_shape.shape_id = str(uuid.uuid4())
        
        # 提取几何构成要素
        要素 = self._extract_geometric_elements(input_data_set)
        unit_shape.几何要素 = 要素
        
        # 定义形态生成逻辑
        逻辑 = self._define_generation_logic(input_data_set)
        unit_shape.生成逻辑 = 逻辑
        
        # 计算动态特征值
        unit_shape.动态特征值 = self._calculate_dynamic_feature(要素, 逻辑)
        
        return unit_shape
    
    def _extract_geometric_elements(self, input_data_set: ParameterInputDataSet) -> list:
        """提取几何构成要素"""
        要素 = []
        
        # 主体框架要素
        frame = GeometricElement()
        frame.type = "框架"
        frame.params["height"] = input_data_set.param_spec_set["height"]
        frame.params["width"] = input_data_set.param_spec_set["width"]
        要素.append(frame)
        
        # 曲面要素
        surface = GeometricElement()
        surface.type = "曲面"
        surface.params["curvature"] = input_data_set.param_spec_set["facade_curvature"]
        要素.append(surface)
        
        return 要素
    
    def _define_generation_logic(self, input_data_set: ParameterInputDataSet) -> ShapeGenerationLogic:
        """定义形态生成逻辑"""
        logic = ShapeGenerationLogic()
        logic.触发条件 = f"参数完整度 >= {input_data_set.完整性指标}"
        logic.约束边界 = "尺寸在规范集范围内"
        logic.优先级 = 1
        return logic
    
    def _calculate_dynamic_feature(self, 要素: list, 逻辑: ShapeGenerationLogic) -> float:
        """计算动态特征值"""
        height = 要素[0].params["height"]
        width = 要素[0].params["width"]
        curvature = 要素[1].params["curvature"]
        return normalize(height * width * curvature, 0, 1000000)