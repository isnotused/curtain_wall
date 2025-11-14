from model.structure_optimization_params import StructureOptimizationParams
from model.error_correction_dataset import ErrorCorrectionDataSet
from util.math_utils import clamp

class ErrorCorrector:
    """误差修正模块：分析偏差并调整参数，生成修正数据集"""
    def correct(self, struct_params: StructureOptimizationParams) -> ErrorCorrectionDataSet:
        result = ErrorCorrectionDataSet()
        
        # 计算尺寸偏差率与形态偏移量
        偏差率 = self._calculate_size_deviation(struct_params)
        偏移量 = self._calculate_shape_offset(struct_params)
        result.尺寸偏差率 = 偏差率
        result.形态偏移量 = 偏移量
        
        # 分析装配适配速率
        适配速率 = self._analyze_adaptation_rate(偏差率, 偏移量)
        result.适配速率 = 适配速率
        
        # 调整参数匹配比值
        result.参数匹配比值 = self._adjust_param_matching_ratio(适配速率, struct_params)
        
        return result
    
    def _calculate_size_deviation(self, params: StructureOptimizationParams) -> float:
        """计算尺寸偏差率"""
        if params.稳定阈值 == 0:
            return 0
        return abs(params.优化应力值 - params.稳定阈值) / params.稳定阈值 * 100
    
    def _calculate_shape_offset(self, params: StructureOptimizationParams) -> float:
        """计算形态偏移量"""
        return (1 - params.受力均衡系数) * 50  
    
    def _analyze_adaptation_rate(self, 偏差率: float, 偏移量: float) -> float:
        """分析装配适配速率"""
        偏差影响 = 1 - clamp(偏差率 / 10, 0, 1)
        偏移影响 = 1 - clamp(偏移量 / 50, 0, 1)
        return (偏差影响 + 偏移影响) / 2
    
    def _adjust_param_matching_ratio(self, 适配速率: float, params: StructureOptimizationParams) -> float:
        """调整参数匹配比值"""
        return clamp(适配速率 + (params.受力均衡系数 - 0.5) * 0.2, 0.5, 1.0)