class AssociationService:
    """数据关联服务：提供关联比例计算与路径确定功能"""
    def calculate_association_ratio(self, param_matching_ratio: float) -> float:
        """计算设计参数与施工数据的关联比例"""
        return param_matching_ratio * 0.9 + 0.1  
    
    def determine_association_path(self, association_ratio: float) -> str:
        """确定目标关联路径"""
        if association_ratio >= 0.8:
            return "直接关联路径（高匹配）"
        elif association_ratio >= 0.5:
            return "间接关联路径（中匹配）"
        else:
            return "待优化关联路径（低匹配）"