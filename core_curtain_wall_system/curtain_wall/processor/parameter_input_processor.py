from model.parameter import Parameter
from model.parameter_input_dataset import ParameterInputDataSet
from model.design_rule import DesignRule
from util.math_utils import clamp
from util.system_config import 完整性合格阈值

class ParameterInputProcessor:
    """参数输入处理模块：分析参数完整性与规则匹配度，生成处理数据集"""
    def process(self, param: Parameter) -> ParameterInputDataSet:
        result = ParameterInputDataSet()
        
        # 提取设计规则
        rule = self._get_design_rule()
        
        # 分析参数输入完整性
        完整性指标 = self._calculate_completeness(param, rule)
        result.完整性指标 = 完整性指标
        
        # 分析规则匹配度
        匹配度 = self._calculate_matching_degree(param, rule)
        result.规则匹配度 = 匹配度
        
        # 生成参数规范集与关联映射
        result.param_spec_set = self._build_param_spec_set(param, rule)
        result.关联映射关系 = self._build_mapping(param)
        
        return result
    
    def _get_design_rule(self) -> DesignRule:
        """获取设计规则"""
        rule = DesignRule()
        rule.min_height = 2000.0
        rule.max_height = 4000.0
        rule.min_width = 1000.0
        rule.max_width = 2000.0
        return rule
    
    def _calculate_completeness(self, param: Parameter, rule: DesignRule) -> float:
        """计算参数输入完整性"""
        total_params = 4
        valid_count = 0
        
        if rule.min_height <= param.height <= rule.max_height:
            valid_count += 1
        if rule.min_width <= param.width <= rule.max_width:
            valid_count += 1
        if param.material_strength > 0:
            valid_count += 1
        if param.facade_curvature >= 0:
            valid_count += 1
            
        return valid_count / total_params
    
    def _calculate_matching_degree(self, param: Parameter, rule: DesignRule) -> float:
        """计算规则匹配度"""
        height_mid = (rule.min_height + rule.max_height) / 2
        width_mid = (rule.min_width + rule.max_width) / 2
        
        height_deviation = abs(param.height - height_mid)
        width_deviation = abs(param.width - width_mid)
        
        height_ratio = height_deviation / (rule.max_height - rule.min_height)
        width_ratio = width_deviation / (rule.max_width - rule.min_width)
        
        return 1 - (height_ratio + width_ratio) / 2
    
    def _build_param_spec_set(self, param: Parameter, rule: DesignRule) -> dict:
        """构建参数规范集"""
        return {
            "height": clamp(param.height, rule.min_height, rule.max_height),
            "width": clamp(param.width, rule.min_width, rule.max_width),
            "material_strength": param.material_strength,
            "facade_curvature": param.facade_curvature
        }
    
    def _build_mapping(self, param: Parameter) -> dict:
        """构建关联映射关系"""
        return {
            "height": "结构高度约束",
            "width": "结构宽度约束",
            "material_strength": "受力计算参数",
            "facade_curvature": "形态生成参数"
        }