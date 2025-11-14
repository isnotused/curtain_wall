from datetime import datetime

class DataAssociationRecord:
    """数据关联记录表实体"""
    def __init__(self):
        self.id = ""  
        self.生成时间 = None  
        self.关联比例 = 0.0 
        self.关联路径 = ""   
        self.匹配参数集 = "" 