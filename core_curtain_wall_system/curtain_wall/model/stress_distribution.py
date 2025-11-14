class StressDistribution:
    """应力分布变化量实体"""
    def __init__(self):
        self.max_stress = 0.0  
        self.min_stress = 0.0  
        self.stress_gradient = 0.0 
        self.change_rate = 0.0 