import pandas as pd
import numpy as np
from utils import print_log, simulate_process
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class UnitGenerationModule:
    def __init__(self, processed_params):
        self.processed_params = processed_params
        self.geometric_features = None
        self.shape_generation_results = None 
    
    def extract_geometric_features(self):
        """单元件生成模块，提取单元件几何构成要素和形态生成逻辑"""
        print_log("开始提取单元件几何构成要素和形态生成逻辑")
        
        # 基于处理后的参数提取几何特征
        features_df = self.processed_params.copy()
        
        # 计算几何构成要素
        features_df['宽高比'] = features_df['宽度(m)'] / features_df['高度(m)']
        features_df['厚宽比'] = features_df['厚度(m)'] / features_df['宽度(m)']
        features_df['形态复杂度'] = np.abs(features_df['曲率']) * 10 + features_df['倾斜角度(度)'] / 5
        
        # 确定形态生成逻辑参数
        features_df['生成速率系数'] = 1.0 + features_df['规则匹配度'] * 0.5
        features_df['扩展系数'] = 0.8 + features_df['形态复杂度'] * 0.02
        
        self.geometric_features = features_df
        
        print_log("单元件几何构成要素和形态生成逻辑提取完成")
        return features_df
    
    def generate_unit_shape(self):  
        """生成单元件形态生成结果"""
        print_log("开始生成单元件形态")
        
        # 基于几何特征生成形态参数
        shape_df = self.geometric_features.copy()
        
        # 计算形态生成结果参数
        shape_df['单元件表面积(m²)'] = 2 * (shape_df['宽度(m)'] * shape_df['高度(m)'] + 
                                        shape_df['宽度(m)'] * shape_df['厚度(m)'] + 
                                        shape_df['高度(m)'] * shape_df['厚度(m)'])
        
        # 考虑曲率对形态的影响
        shape_df['有效面积系数'] = 1.0 + np.abs(shape_df['曲率']) * 0.3
        shape_df['实际表面积(m²)'] = shape_df['单元件表面积(m²)'] * shape_df['有效面积系数']
        
        # 计算形态生成路径参数
        shape_df['生成路径长度'] = np.sqrt(shape_df['宽度(m)']**2 + shape_df['高度(m)']** 2) * (1 + shape_df['倾斜角度(度)'] / 90)
        
        self.shape_generation_results = shape_df  
        
        print_log("单元件形态生成完成")
        
        # 生成形态特征散点图
        plt.figure(figsize=(10, 6))
        plt.scatter(shape_df['宽高比'], shape_df['形态复杂度'], 
                   c=shape_df['规则匹配度'], cmap='viridis', s=50, alpha=0.7)
        plt.colorbar(label='规则匹配度')
        plt.title('单元件宽高比与形态复杂度关系', fontsize=14)
        plt.xlabel('宽高比', fontsize=12)
        plt.ylabel('形态复杂度', fontsize=12)
        plt.grid(linestyle='--', alpha=0.7)
        plt.savefig('charts/单元件形态特征散点图.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 生成3D形态展示图
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        scatter = ax.scatter(shape_df['宽度(m)'], shape_df['高度(m)'], shape_df['厚度(m)'],
                           c=shape_df['实际表面积(m²)'], cmap='plasma', s=50, alpha=0.7)
        
        ax.set_xlabel('宽度(m)', fontsize=10)
        ax.set_ylabel('高度(m)', fontsize=10)
        ax.set_zlabel('厚度(m)', fontsize=10)
        plt.colorbar(scatter, ax=ax, label='实际表面积(m²)')
        plt.title('单元件三维尺寸与表面积关系', fontsize=14)
        plt.savefig('charts/单元件三维尺寸分布图.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return shape_df
    
    def run(self):
        """运行单元件生成模块"""
        print_log("开始执行单元件生成模块")
        
        def process_callback(step):
            if step == 30:
                self.extract_geometric_features()
            elif step == 100:
                self.generate_unit_shape()  
                
        simulate_process(12, 100, "单元件生成模块", process_callback)
        
        print_log("单元件生成模块执行完成")
        return self.shape_generation_results  