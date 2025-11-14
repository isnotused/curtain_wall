import pandas as pd
import numpy as np
from utils import print_log, simulate_process
import matplotlib.pyplot as plt

class ParameterInputModule:
    def __init__(self, basic_params, association_rules):
        self.basic_params = basic_params
        self.association_rules = association_rules
        self.processed_params = None
        self.matching_degree = None
        
    def analyze_matching_degree(self):
        """分析参数输入完整性与设计规则匹配程度，用于单元件生成模块"""
        print_log("开始分析参数输入完整性与设计规则匹配程度")
        
        # 计算各项规则的匹配度
        num_samples = len(self.basic_params)
        match_scores = np.zeros(num_samples)
        
        # 宽度与高度比检查
        width_height_ratio = self.basic_params['宽度(m)'] / self.basic_params['高度(m)']
        valid_ratio = (width_height_ratio >= self.association_rules['宽度与高度比']['最小值']) & \
                      (width_height_ratio <= self.association_rules['宽度与高度比']['最大值'])
        match_scores += valid_ratio.astype(int) * 0.25
        
        # 厚度与宽度比检查
        thickness_width_ratio = self.basic_params['厚度(m)'] / self.basic_params['宽度(m)']
        valid_thickness = (thickness_width_ratio >= self.association_rules['厚度与宽度比']['最小值']) & \
                          (thickness_width_ratio <= self.association_rules['厚度与宽度比']['最大值'])
        match_scores += valid_thickness.astype(int) * 0.25
        
        # 曲率与倾斜角度关系检查
        curvature_inclination = self.basic_params['曲率'] / (self.basic_params['倾斜角度(度)'] + 0.1)
        valid_curvature = np.abs(curvature_inclination) <= self.association_rules['曲率与倾斜角度关系']['系数']
        match_scores += valid_curvature.astype(int) * 0.25
        
        # 材料强度与厚度关系检查
        strength_thickness = self.basic_params['材料强度(MPa)'] / (self.basic_params['厚度(m)'] * 1000)
        valid_strength = strength_thickness >= self.association_rules['材料强度与厚度关系']['系数']
        match_scores += valid_strength.astype(int) * 0.25
        
        self.matching_degree = match_scores
        self.basic_params['规则匹配度'] = match_scores
        
        print_log("参数输入完整性与设计规则匹配程度分析完成")
        
        # 生成匹配度分布图表
        plt.figure(figsize=(10, 6))
        plt.hist(match_scores, bins=10, color='skyblue', edgecolor='black')
        plt.title('参数输入与设计规则匹配度分布', fontsize=14)
        plt.xlabel('匹配度', fontsize=12)
        plt.ylabel('样本数量', fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.savefig('charts/参数匹配度分布.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return match_scores
    
    def generate_processed_dataset(self):
        """生成参数输入处理数据集"""
        print_log("开始生成参数输入处理数据集")
        
        # 复制基础参数
        processed_df = self.basic_params.copy()
        
        # 计算衍生参数
        processed_df['面积(m²)'] = processed_df['宽度(m)'] * processed_df['高度(m)']
        processed_df['体积(m³)'] = processed_df['宽度(m)'] * processed_df['高度(m)'] * processed_df['厚度(m)']
        processed_df['重量(kg)'] = processed_df['体积(m³)'] * processed_df['密度(kg/m³)']
        processed_df['强度重量比'] = processed_df['材料强度(MPa)'] / processed_df['重量(kg)']
        
        # 根据匹配度调整参数
        mask = processed_df['规则匹配度'] < 0.7
        processed_df.loc[mask, '厚度(m)'] *= 1.1  # 对匹配度低的样本调整厚度
        processed_df.loc[mask, '材料强度(MPa)'] *= 1.05  # 对匹配度低的样本调整材料强度
        
        self.processed_params = processed_df
        
        print_log("参数输入处理数据集生成完成")
        
        # 生成参数相关性分析图表
        corr_features = ['宽度(m)', '高度(m)', '厚度(m)', '材料强度(MPa)', '重量(kg)']
        corr_matrix = processed_df[corr_features].corr()
        
        plt.figure(figsize=(10, 8))
        plt.imshow(corr_matrix, cmap='coolwarm', interpolation='nearest')
        plt.colorbar(label='相关系数')
        plt.xticks(range(len(corr_features)), corr_features, rotation=45)
        plt.yticks(range(len(corr_features)), corr_features)
        
        # 添加相关系数文本
        for i in range(len(corr_features)):
            for j in range(len(corr_features)):
                plt.text(j, i, f"{corr_matrix.iloc[i, j]:.2f}", 
                         ha='center', va='center', color='white', fontsize=10)
        
        plt.title('参数相关性分析', fontsize=14)
        plt.tight_layout()
        plt.savefig('charts/参数相关性分析.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return processed_df
    
    def run(self):
        """运行参数输入处理模块"""
        print_log("开始执行参数输入处理模块")

        def process_callback(step):
            if step == 25:
                self.analyze_matching_degree()
            elif step == 100:
                self.generate_processed_dataset()
                
        simulate_process(10, 100, "参数输入处理模块", process_callback)
        
        print_log("参数输入处理模块执行完成")
        return self.processed_params