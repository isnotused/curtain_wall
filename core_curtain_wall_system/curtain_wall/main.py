from model.parameter import Parameter
from processor.parameter_input_processor import ParameterInputProcessor
from processor.unit_generator import UnitGenerator
from processor.structure_verifier import StructureVerifier
from processor.error_corrector import ErrorCorrector
from processor.data_associator import DataAssociator

def main():
    # 初始化基础参数
    base_param = Parameter()
    init_base_parameter(base_param)
    
    # 参数输入处理
    input_processor = ParameterInputProcessor()
    input_data_set = input_processor.process(base_param)
    
    # 单元件生成
    generator = UnitGenerator()
    unit_shape = generator.generate(input_data_set)
    
    # 结构验证
    verifier = StructureVerifier()
    struct_opt_params = verifier.verify(unit_shape)
    
    # 误差修正
    corrector = ErrorCorrector()
    error_data_set = corrector.correct(struct_opt_params)
    
    # 数据关联
    associator = DataAssociator()
    record = associator.associate(error_data_set)
    
    # 输出结果
    print(f"幕墙单元件数据关联记录生成完成: {record.id}")

def init_base_parameter(param: Parameter):
    # 初始化基础参数值
    param.height = 3000.0
    param.width = 1500.0
    param.material_strength = 250.0
    param.facade_curvature = 0.05

if __name__ == "__main__":
    main()