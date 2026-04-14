import numpy as np

def calculate_tarboton_slope(e0, adj, res):
    """
    基于 Tarboton (1997) 的三角形刻面法计算坡度
    adj 顺序: E, SE, S, SW, W, NW, N, NE
    """
    max_slope = 0.0
    # 8个刻面的角度补偿，d1是直角边，d2是对角线边
    d1 = res
    d2 = np.sqrt(2) * res
    
    for i in range(8):
        e1 = adj[i]
        e2 = adj[(i + 1) % 8]
        
        # 简化版 Tarboton 刻面坡度计算
        # s1: 中心到第一个邻居的坡度
        # s2: 第一个邻居到第二个邻居的坡度
        if i % 2 == 0: # 偶数索引是 E, S, W, N (直角三角形边)
            s1 = (e0 - e1) / d1
            s2 = (e1 - e2) / d1
        else: # 奇数索引是对角线方向
            s1 = (e0 - e1) / d2
            s2 = (e1 - e2) / d2 # 简化的几何投影
            
        facet_slope = np.sqrt(s1**2 + s2**2)
        max_slope = max(max_slope, facet_slope)
        
    return float(max_slope)