import time
from utils import print_log
from data_generator import generate_basic_parameters, generate_association_rules, generate_construction_data
from parameter_input import ParameterInputModule
from unit_generation import UnitGenerationModule
from structure_verification import StructureVerificationModule
from error_correction import ErrorCorrectionModule
from data_association import DataAssociationModule

def main():
    """主程序入口，启动幕墙单元件快速生成验证系统"""
    start_time = time.time()
    print_log("===== 幕墙单元件快速生成验证系统启动 =====")

    print_log("接收数据...")
    basic_params = generate_basic_parameters(50)  
    association_rules = generate_association_rules()  
    construction_data = generate_construction_data(50)  
    print_log("数据接收完成")
    
    # 执行参数输入处理模块
    param_module = ParameterInputModule(basic_params, association_rules)
    processed_params = param_module.run()
    
    # 执行单元件生成模块
    unit_module = UnitGenerationModule(processed_params)
    unit_results = unit_module.run()
    
    # 执行结构验证模块
    structure_module = StructureVerificationModule(unit_results)
    optimized_params = structure_module.run()
    
    # 执行误差修正模块
    error_module = ErrorCorrectionModule(optimized_params)
    correction_data = error_module.run()
    
    # 执行数据关联模块
    association_module = DataAssociationModule(correction_data, construction_data)
    association_record = association_module.run()
    
    # 输出最终结果摘要
    print_log("\n===== 系统运行结果摘要 =====")
    print_log(f"总样本数: {len(association_record)}")
    print_log(f"平均规则匹配度: {association_record['规则匹配度'].mean():.2f}")
    print_log(f"平均适配性评分: {association_record['适配性评分'].mean():.2f}")
    print_log(f"平均设计-施工关联度: {association_record['设计-施工关联度'].mean():.2f}")
    print_log(f"平均成本效率: {association_record['成本效率(元/㎡)'].mean():.2f} 元/㎡")
    
    end_time = time.time()
    print_log(f"\n===== 系统运行完成，总耗时: {end_time - start_time:.2f} 秒 =====")

if __name__ == "__main__":
    main()