class StructureService:
    """结构分析服务：提供受力计算功能"""
    def calculate_force(self, x: float, y: float, height: float, width: float) -> float:
        """计算指定坐标点的受力值"""
        edge_factor = 1.5 if x in (0, width) or y in (0, height) else 1.0
        return (height * width) / 1000 * edge_factor