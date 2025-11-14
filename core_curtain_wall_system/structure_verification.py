import pandas as pd
import numpy as np
from utils import print_log, simulate_process
import matplotlib.pyplot as plt

class StructureVerificationModule:
    def __init__(self, unit_generation_results):
        self.unit_generation_results = unit_generation_results
        self.force_points = None
        self.stress_distribution = None
        self.optimized_params = None
        
    def extract_force_and_stress(self):
        """提取幕墙单元件结构受力点和应力分布变化量"""
        print_log("开始提取结构受力点和应力分布变化量")
        
        # 基于单元件形态生成结果计算受力和应力参数
        results_df = self.unit_generation_results.copy()
        
        # 计算受力点参数
        results_df['自重载荷(N)'] = results_df['重量(kg)'] * 9.81
        results_df['风载荷系数'] = 1.2 + np.abs(results_df['曲率']) + results_df['倾斜角度(度)'] / 30
        results_df['总载荷(N)'] = results_df['自重载荷(N)'] * results_df['风载荷系数']
        
        # 计算应力分布
        results_df['受力点数量'] = 4 + (results_df['形态复杂度'] // 2).astype(int)
        results_df['平均应力(MPa)'] = results_df['总载荷(N)'] / (results_df['面积(m²)'] * 1000000) * 1.5
        results_df['最大应力(MPa)'] = results_df['平均应力(MPa)'] * (1.2 + results_df['形态复杂度'] * 0.1)
        
        # 计算应力分布变化量
        results_df['应力变化率'] = np.random.normal(0.05, 0.02, len(results_df))
        
        self.force_points = results_df[['样本编号', '总载荷(N)', '受力点数量']]
        self.stress_distribution = results_df[['样本编号', '平均应力(MPa)', '最大应力(MPa)', '应力变化率']]
        
        print_log("结构受力点和应力分布变化量提取完成")
        return results_df
    
    def generate_optimized_parameters(self):
        """结构验证模块，生成结构验证优化参数集"""
        print_log("开始生成结构验证优化参数集")
        
        # 基于受力和应力分析结果生成优化参数
        verification_df = self.extract_force_and_stress().copy()
        
        # 计算安全系数
        verification_df['安全系数'] = verification_df['材料强度(MPa)'] / verification_df['最大应力(MPa)']
        
        # 确定需要优化的样本
        verification_df['需要优化'] = verification_df['安全系数'] < 1.5
        
        # 计算优化参数
        verification_df['优化厚度系数'] = np.where(
            verification_df['需要优化'], 
            1.2 + (1.5 - verification_df['安全系数']) * 0.5, 
            1.0
        )
        
        verification_df['优化强度系数'] = np.where(
            verification_df['需要优化'], 
            1.1 + (1.5 - verification_df['安全系数']) * 0.3, 
            1.0
        )
        
        # 计算优化后的参数
        verification_df['优化后厚度(m)'] = verification_df['厚度(m)'] * verification_df['优化厚度系数']
        verification_df['优化后强度(MPa)'] = verification_df['材料强度(MPa)'] * verification_df['优化强度系数']
        verification_df['优化后安全系数'] = verification_df['优化后强度(MPa)'] / verification_df['最大应力(MPa)']
        
        self.optimized_params = verification_df
        
        print_log("结构验证优化参数集生成完成")
        
        # 生成应力与安全系数关系图
        plt.figure(figsize=(10, 6))
        safe_samples = verification_df[~verification_df['需要优化']]
        unsafe_samples = verification_df[verification_df['需要优化']]
        
        plt.scatter(safe_samples['最大应力(MPa)'], safe_samples['安全系数'], 
                   c='green', label='安全样本', alpha=0.7)
        plt.scatter(unsafe_samples['最大应力(MPa)'], unsafe_samples['安全系数'], 
                   c='red', label='需优化样本', alpha=0.7)
        plt.axhline(y=1.5, color='black', linestyle='--', label='安全阈值')
        plt.title('最大应力与安全系数关系', fontsize=14)
        plt.xlabel('最大应力(MPa)', fontsize=12)
        plt.ylabel('安全系数', fontsize=12)
        plt.legend()
        plt.grid(linestyle='--', alpha=0.7)
        plt.savefig('charts/应力与安全系数关系.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return verification_df
    
    def run(self):
        """运行结构验证模块"""
        print_log("开始执行结构验证模块")
        
        def process_callback(step):
            if step == 40:
                self.extract_force_and_stress()
            elif step == 100:
                self.generate_optimized_parameters()
                
        simulate_process(14, 100, "结构验证模块", process_callback)
        
        print_log("结构验证模块执行完成")
        return self.optimized_params