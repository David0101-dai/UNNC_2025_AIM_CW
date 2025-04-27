import json                     # 1. 导入 json 模块，用于读写 JSON 格式的数据
import random                   # 2. 导入 random 模块，用于生成随机数和打乱列表
import time                     # 3. 导入 time 模块，用于记录和计算时间
import os                       # 4. 导入 os 模块，用于处理文件和路径
from datetime import datetime  # 5. 从 datetime 模块中导入 datetime 类，用于获取当前日期时间

start_time = time.time()        # 6. 记录脚本开始执行的时间（用于计算总运行时长）

# 7-11: 定义一个函数，从指定路径读取 JSON 文件并解析为 Python 对象
def read_bin_packing_instances(json_file_path):
    with open(json_file_path, 'r') as file:  # 8. 以只读模式打开 JSON 文件
        instances = json.load(file)          # 9. 使用 json.load 解析文件内容
    return instances                          # 10. 返回解析后的 Python 对象（通常是列表或字典）

# 12-22: 定义 Next-Fit 装箱算法
def next_fit(items, capacity):
    bins = []           # 13. 用来存放所有“已装满”或“部分装满”的箱子
    current_bin = []    # 14. 表示当前正在往里装的箱子

    for item in items:  # 15. 依次遍历每个物品
        if sum(current_bin) + item <= capacity:  # 16. 如果放得下，就装进去
            current_bin.append(item)              # 17. 把物品加到当前箱子里
        else:
            bins.append(current_bin)              # 18. 当前箱子装满或放不下，先把它“封箱”存入 bins
            current_bin = [item]                  # 19. 新建一个箱子，把当前物品放进去
    bins.append(current_bin)  # 20. 循环结束后，别忘了把最后一个正在装的箱子也加入结果
    return bins               # 21. 返回所有箱子的列表

def random_search_fit(items, capacity, fit_fun, iterations=1000):
    #items：待装箱物品列表 capacity：每个箱子的容量上限 fit_fun：具体的装箱算法函数（如 next_fit） iterations：随机打乱并尝试的次数，默认 1000
    best_solution = None
    min_bins = float('inf')

    for _ in range(iterations):
        # 如果不想破坏原列表，可以先复制一份
        tmp_items = items[:]  
        random.shuffle(tmp_items)

        # 正确调用算法
        current_solution = fit_fun(tmp_items, capacity)
        # 计算本次方案用了多少箱
        num_bins = len(current_solution)

        # 比较并更新最优解
        if num_bins < min_bins:
            min_bins = num_bins
            best_solution = current_solution
    return best_solution

# 31-56: 脚本主入口，只有直接运行脚本时才执行以下代码
if __name__ == "__main__":
    random.seed(0)  # 32. 固定随机种子，保证实验可重复

    # 33-34: 计算脚本所在目录，并构造 JSON 文件的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(script_dir, 'CW_ins.json')

    output_filename = '20513824_Yuanhao_Dai.json'  # 35. 定义运行结果要写入的文件名

    instances = read_bin_packing_instances(json_file_path)  # 36. 读取所有测试样例
    total_bins = 0                                         # 37. 统计所有实例共用多少箱

    # 38-42: 准备一个字典，用于输出 JSON，包含运行日期、总耗时和各实例结果
    output_json = {
        'date': datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
        'time': 0,
        'res': []
    }

    # 43-52: 对每个实例执行随机搜索装箱
    for ins in instances:
        start_time_sol = time.time()  # 44. 记录该实例开始处理的时间
        solution = random_search_fit(ins['items'], ins['capacity'], next_fit)
        
        # 46-50: 将单个实例的结果追加到 output_json['res']
        output_json['res'].append({
            'name': ins['name'],
            'capacity': ins['capacity'],
            'solution': solution
        })
        bin_used = len(solution)  # 51. 计算本次方案用了多少箱
        print(f"Instance: {ins['name']}")  # 52. 打印实例名称
        print(f"Bins Used:\t{bin_used} (Time: {time.time()-start_time_sol:.4f}s)")  # 打印箱数和耗时
        total_bins += bin_used  # 53. 累加到总箱数

    # 54-56: 所有实例处理完毕后，计算总时长并写入输出文件
    total_time = time.time() - start_time
    with open(output_filename, 'w+') as f:
        output_json['time'] = total_time
        json.dump(output_json, f, indent=4)

    # 57-60: 打印摘要信息
    print("\n--- Summary ---")
    print(f"Output saved to {output_filename}")
    print(f"Total Used Bins: {total_bins}")
    print(f"Total Execution Time: {total_time:.4f}s")
