import pandas as pd
import numpy as np
from utils import print_log, simulate_process
import matplotlib.pyplot as plt

class DataAssociationModule:
    def __init__(self, correction_data, construction_data):
        self.correction_data = correction_data
        self.construction_data = construction_data
        self.association_data = None
        self.association_record = None
        
    def analyze_association(self):
        """分析设计参数与施工数据的关联关系，根据误差修正数据和施工数据，分析设计参数与施工数据的关联关系"""
        print_log("开始分析设计参数与施工数据的关联关系")
        
        # 合并设计参数与施工数据
        merged_df = pd.merge(self.correction_data, self.construction_data, on='样本编号')
        
        # 分析关联关系
        merged_df['单位面积施工时间'] = merged_df['施工时间(小时)'] / merged_df['面积(m²)']
        merged_df['单位面积人工成本'] = merged_df['人工成本(元)'] / merged_df['面积(m²)']
        merged_df['单位体积材料成本'] = merged_df['材料成本(元)'] / merged_df['体积(m³)']
        
        # 计算关联强度
        merged_df['设计-施工关联度'] = (1 - merged_df['总体偏差指数'] / 10) * \
                                   (0.5 + merged_df['规则匹配度'] / 2) * \
                                   (0.6 + merged_df['适配性评分'] / 20)
        
        self.association_data = merged_df
        
        print_log("设计参数与施工数据的关联关系分析完成")
        return merged_df
    
    def generate_association_record(self):
        """生成幕墙单元件数据关联记录表"""
        print_log("开始生成数据关联记录表")
        
        # 基于关联分析结果生成关联记录表
        record_df = self.analyze_association().copy()
        
        # 筛选关键关联参数
        association_record = record_df[['样本编号', '规则匹配度', '适配性评分', '设计-施工关联度',
                                       '施工时间(小时)', '人工成本(元)', '材料成本(元)',
                                       '单位面积施工时间', '单位面积人工成本']].copy()
        
        # 计算总成本和时间效率
        association_record['总成本(元)'] = association_record['人工成本(元)'] + association_record['材料成本(元)']
        association_record['成本效率(元/㎡)'] = association_record['总成本(元)'] / record_df['面积(m²)']
        
        # 按关联度排序
        association_record = association_record.sort_values('设计-施工关联度', ascending=False)
        
        self.association_record = association_record
        
        print_log("数据关联记录表生成完成")
        
        # 生成关联度与成本效率关系图
        plt.figure(figsize=(10, 6))
        plt.scatter(association_record['设计-施工关联度'], association_record['成本效率(元/㎡)'], 
                   c=association_record['规则匹配度'], cmap='spring', s=50, alpha=0.7)
        plt.colorbar(label='规则匹配度')
        plt.title('设计-施工关联度与成本效率关系', fontsize=14)
        plt.xlabel('设计-施工关联度', fontsize=12)
        plt.ylabel('成本效率(元/㎡)', fontsize=12)
        plt.grid(linestyle='--', alpha=0.7)
        plt.savefig('charts/关联度与成本效率关系.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 生成施工时间分布箱线图
        plt.figure(figsize=(10, 6))
        # 按关联度分组
        association_record['关联度分组'] = pd.cut(association_record['设计-施工关联度'], 
                                              bins=[0, 0.3, 0.6, 1.0], 
                                              labels=['低关联度', '中关联度', '高关联度'])
        
        # 绘制箱线图
        association_record.boxplot(column='单位面积施工时间', by='关联度分组', grid=False, 
                                  patch_artist=True, boxprops=dict(facecolor='lightblue'))
        
        plt.title('不同关联度分组的单位面积施工时间分布', fontsize=14)
        plt.suptitle('')  
        plt.xlabel('关联度分组', fontsize=12)
        plt.ylabel('单位面积施工时间(小时/㎡)', fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.savefig('charts/不同关联度施工时间分布.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return association_record
    
    def run(self):
        """运行数据关联模块"""
        print_log("开始执行数据关联模块")
        
        def process_callback(step):
            if step == 35:
                self.analyze_association()
            elif step == 100:
                self.generate_association_record()
                
        simulate_process(12, 100, "数据关联模块", process_callback)
        
        print_log("数据关联模块执行完成")
        return self.association_record