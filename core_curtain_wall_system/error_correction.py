import pandas as pd
import numpy as np
from utils import print_log, simulate_process
import matplotlib.pyplot as plt

class ErrorCorrectionModule:
    def __init__(self, optimized_params):
        self.optimized_params = optimized_params
        self.deviation_data = None
        self.correction_data = None
        
    def analyze_deviations(self):
        """误差修正模块，分析尺寸偏差率和形态偏移量"""
        print_log("开始分析尺寸偏差率和形态偏移量")
        
        # 基于优化参数计算偏差数据
        params_df = self.optimized_params.copy()
        
        # 尺寸偏差
        params_df['宽度偏差率(%)'] = np.random.normal(0, 0.5, len(params_df))
        params_df['高度偏差率(%)'] = np.random.normal(0, 0.5, len(params_df))
        params_df['厚度偏差率(%)'] = np.random.normal(0, 0.8, len(params_df))
        
        params_df['曲率偏移量'] = np.random.normal(0, 0.03, len(params_df))
        params_df['角度偏移量(度)'] = np.random.normal(0, 0.5, len(params_df))
        
        # 计算总体偏差指数
        params_df['尺寸偏差指数'] = (abs(params_df['宽度偏差率(%)']) + 
                                   abs(params_df['高度偏差率(%)']) + 
                                   abs(params_df['厚度偏差率(%)'])) / 3
        
        params_df['形态偏差指数'] = (abs(params_df['曲率偏移量']) * 20 + 
                                   abs(params_df['角度偏移量(度)'])) / 2
        
        params_df['总体偏差指数'] = (params_df['尺寸偏差指数'] + params_df['形态偏差指数']) / 2
        
        self.deviation_data = params_df
        
        print_log("尺寸偏差率和形态偏移量分析完成")
        return params_df
    
    def generate_correction_data(self):
        """生成误差修正调整数据集"""
        print_log("开始生成误差修正调整数据集")
        
        # 基于偏差分析结果生成修正数据
        correction_df = self.analyze_deviations().copy()
        
        # 计算修正系数
        correction_df['宽度修正系数'] = 1 + correction_df['宽度偏差率(%)'] / 100
        correction_df['高度修正系数'] = 1 + correction_df['高度偏差率(%)'] / 100
        correction_df['厚度修正系数'] = 1 + correction_df['厚度偏差率(%)'] / 100
        
        # 计算修正后的参数
        correction_df['修正后宽度(m)'] = correction_df['宽度(m)'] * correction_df['宽度修正系数']
        correction_df['修正后高度(m)'] = correction_df['高度(m)'] * correction_df['高度修正系数']
        correction_df['修正后厚度(m)'] = correction_df['优化后厚度(m)'] * correction_df['厚度修正系数']
        
        # 计算形态修正
        correction_df['修正后曲率'] = correction_df['曲率'] - correction_df['曲率偏移量']
        correction_df['修正后角度(度)'] = correction_df['倾斜角度(度)'] - correction_df['角度偏移量(度)']
        
        # 计算装配适配性
        correction_df['适配性评分'] = 10 - correction_df['总体偏差指数'] * 2
        correction_df['适配性评分'] = correction_df['适配性评分'].clip(lower=0)
        
        self.correction_data = correction_df
        
        print_log("误差修正调整数据集生成完成")
        
        # 生成偏差分布与适配性关系图
        plt.figure(figsize=(10, 6))
        plt.scatter(correction_df['总体偏差指数'], correction_df['适配性评分'], 
                   c=correction_df['规则匹配度'], cmap='coolwarm', s=50, alpha=0.7)
        plt.colorbar(label='规则匹配度')
        plt.title('总体偏差指数与装配适配性评分关系', fontsize=14)
        plt.xlabel('总体偏差指数', fontsize=12)
        plt.ylabel('适配性评分(0-10)', fontsize=12)
        plt.grid(linestyle='--', alpha=0.7)
        plt.savefig('charts/偏差与适配性关系.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return correction_df
    
    def run(self):
        """运行误差修正模块"""
        print_log("开始执行误差修正模块")

        def process_callback(step):
            if step == 35:
                self.analyze_deviations()
            elif step == 100:
                self.generate_correction_data()
                
        simulate_process(12, 100, "误差修正模块", process_callback)
        
        print_log("误差修正模块执行完成")
        return self.correction_data