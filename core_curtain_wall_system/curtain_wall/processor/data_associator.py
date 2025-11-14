import uuid
from datetime import datetime
from model.error_correction_dataset import ErrorCorrectionDataSet
from model.data_association_record import DataAssociationRecord
from service.association_service import AssociationService

class DataAssociator:
    """数据关联模块：生成设计与施工数据关联记录"""
    def __init__(self):
        self.association_service = AssociationService()
    
    def associate(self, error_data_set: ErrorCorrectionDataSet) -> DataAssociationRecord:
        record = DataAssociationRecord()
        record.id = str(uuid.uuid4())
        record.生成时间 = datetime.now()
        
        # 计算关联比例
        关联比例 = self.association_service.calculate_association_ratio(
            error_data_set.参数匹配比值
        )
        record.关联比例 = 关联比例
        
        # 确定关联路径
        record.关联路径 = self.association_service.determine_association_path(关联比例)
        
        # 生成匹配参数集描述
        record.匹配参数集 = self._build_matching_params(error_data_set)
        
        return record
    
    def _build_matching_params(self, data_set: ErrorCorrectionDataSet) -> str:
        """构建匹配参数集描述"""
        return (f"尺寸偏差率:{data_set.尺寸偏差率:.2f}%, "
                f"形态偏移量:{data_set.形态偏移量:.2f}mm, "
                f"参数匹配比值:{data_set.参数匹配比值:.2f}")