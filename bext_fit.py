import json
import random
import time
import os  # 新增
from datetime import datetime

# 开始计时
start_time = time.time()

def read_bin_packing_instances(json_file_path):
    with open(json_file_path, 'r') as file:
        instances = json.load(file)  # 从 JSON 文件中加载实例数据
    return instances

# Best Fit 算法
def best_fit(items, capacity):
    bins = []  # 存放每个箱子的已用空间
    bins_contents = []  # 存放每个箱子的物品内容

    for item in items:
        # 寻找最适合的箱子
        best_bin = -1
        min_space_left = capacity + 1  # 初始化为比任何箱子都大的值

        # 遍历每个箱子，寻找剩余空间最小且仍能容纳当前物品的箱子
        for i in range(len(bins)):
            space_left = capacity - bins[i]
            if space_left >= item and space_left < min_space_left:
                best_bin = i
                min_space_left = space_left
        
        # 如果找到了合适的箱子，放入该箱子
        if best_bin != -1:
            bins[best_bin] += item
            bins_contents[best_bin].append(item)  # 将物品添加到该箱子的物品列表
        else:
            # 否则，创建一个新箱子
            bins.append(item)
            bins_contents.append([item])  # 新箱子里只有当前物品

    return bins_contents  # 返回每个箱子中的物品列表

# 随机搜索函数，重复多次找到最优解
def random_search_fit(items, capacity, fit_fun, iterations=1000):
    best_solution = None
    min_bins = float('inf')

    for _ in range(iterations):
        random.shuffle(items)  # 随机打乱物品
        current_solution = fit_fun(items, capacity)

        # 如果当前解使用的箱子比之前少，则更新最优解
        if len(current_solution) < min_bins:
            best_solution = current_solution
            min_bins = len(current_solution)
    
    return best_solution

if __name__ == "__main__":
    random.seed(0)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(script_dir, 'CW_ins.json')

    output_filename = '20513824_Yuanhao_Dai.json'  # 输出的 JSON 文件路径
    instances = read_bin_packing_instances(json_file_path)  # 读取实例数据

    total_bins = 0  # 用过的箱子数量
    output_json = {}
    output_json['date'] = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    output_json['time'] = 0
    output_json['res'] = []

    # Main Content
    #######################################################################
    for ins in instances:
        start_time_sol = time.time()
        
        # 找到解决方案
        solution = random_search_fit(ins['items'], ins['capacity'], best_fit)
        
        # 保存和打印输出
        output_json['res'].append({})
        output_json['res'][-1]['name'] = ins['name']
        output_json['res'][-1]['capacity'] = ins['capacity']
        output_json['res'][-1]['solution'] = solution
        bin_used = len(solution)

        print(f"Instance: {ins['name']}")
        print(f"Bins Used:\t{bin_used} (Time: {time.time() - start_time_sol:.4f}s)")
        total_bins += len(solution)
    ########################################################################

    total_time = time.time() - start_time
    
    with open(output_filename, 'w+') as f:
        output_json['time'] = total_time
        json.dump(output_json, f, indent=4)

    print("\n--- Summary ---")
    print(f"Output saved to {output_filename}")
    print(f"Total Used Bins: {total_bins}")
    print(f"Total Execution Time: {total_time:.4f}s")
