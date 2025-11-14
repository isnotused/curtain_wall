from model.parameter import Parameter
from model.design_rule import DesignRule

class ParameterService:
    """参数处理服务：提供参数校验与转换功能"""
    def validate(self, param: Parameter, rule: DesignRule) -> bool:
        """校验参数是否符合规则"""
        return (rule.min_height <= param.height <= rule.max_height and
                rule.min_width <= param.width <= rule.max_width)
    
    def convert_to_standard_unit(self, param: Parameter):
        """转换参数至标准单位（mm）"""
        param.height *= 1000
        param.width *= 1000