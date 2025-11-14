from model.unit_shape import UnitShape
from model.structure_optimization_params import StructureOptimizationParams
from model.force_point import ForcePoint
from model.stress_distribution import StressDistribution
from service.structure_service import StructureService
from util.math_utils import max_val, min_val, standard_deviation, clamp

class StructureVerifier:
    """结构验证模块：分析受力与应力分布，生成优化参数集"""
    def __init__(self):
        self.structure_service = StructureService()
    
    def verify(self, unit_shape: UnitShape) -> StructureOptimizationParams:
        # 提取受力点
        force_points = self._extract_force_points(unit_shape)
        
        # 分析应力分布
        stress = self._analyze_stress_distribution(force_points, unit_shape)
        
        # 生成优化参数集
        return self._generate_optimization_params(force_points, stress)
    
    def _extract_force_points(self, unit_shape: UnitShape) -> list:
        """提取受力点"""
        points = []
        height = unit_shape.几何要素[0].params["height"]
        width = unit_shape.几何要素[0].params["width"]
        
        # 生成四角受力点
        for i in range(4):
            p = ForcePoint()
            p.id = f"FP-{i}"
            p.x = 0 if i % 2 == 0 else width
            p.y = 0 if i < 2 else height
            p.force_value = self.structure_service.calculate_force(
                p.x, p.y, height, width
            )
            points.append(p)
        return points
    
    def _analyze_stress_distribution(self, points: list, unit_shape: UnitShape) -> StressDistribution:
        """分析应力分布"""
        stress = StressDistribution()
        forces = [p.force_value for p in points]
        
        stress.max_stress = max_val(forces)
        stress.min_stress = min_val(forces)
        stress.stress_gradient = (stress.max_stress - stress.min_stress) / unit_shape.几何要素[0].params["width"]
        stress.change_rate = standard_deviation(forces) / stress.max_stress * 100 if stress.max_stress != 0 else 0
        
        return stress
    
    def _generate_optimization_params(self, points: list, stress: StressDistribution) -> StructureOptimizationParams:
        """生成优化参数集"""
        params = StructureOptimizationParams()
        
        # 计算受力均衡系数
        avg_force = sum(p.force_value for p in points) / len(points)
        std_force = standard_deviation([p.force_value for p in points])
        params.受力均衡系数 = 1 - (std_force / avg_force) if avg_force != 0 else 0
        
        # 设置稳定阈值
        params.稳定阈值 = 200.0
        
        # 计算优化应力值
        params.优化应力值 = clamp(stress.max_stress, 0, params.稳定阈值)
        
        params.验证指标数量 = 4  
        
        return params