import json
import random
import time
import os
from datetime import datetime

# 开始计时
start_time = time.time()

def read_bin_packing_instances(json_file_path):
    with open(json_file_path, 'r') as file:
        instances = json.load(file)
    return instances

# Best Fit 算法
def best_fit(items, capacity):
    bins = []
    bins_contents = []
    for item in items:
        best_bin = -1
        min_space_left = capacity + 1
        for i in range(len(bins)):
            space_left = capacity - bins[i]
            if space_left >= item and space_left < min_space_left:
                best_bin = i
                min_space_left = space_left
        if best_bin != -1:
            bins[best_bin] += item
            bins_contents[best_bin].append(item)
        else:
            bins.append(item)
            bins_contents.append([item])
    return bins_contents

# First‐Improvement 局部合并
def first_improvement(bins, capacity):
    for i in range(len(bins)):
        for j in range(len(bins)):
            if i == j:
                continue
            if sum(bins[i]) + sum(bins[j]) <= capacity:
                new_bins = []
                for k in range(len(bins)):
                    if k == i:
                        new_bins.append(bins[i] + bins[j])
                    elif k != j:
                        new_bins.append(bins[k])
                return new_bins
    return None

# 局部搜索
def local_search(bins, capacity, max_iters=100):
    for _ in range(max_iters):
        improved = first_improvement(bins, capacity)
        if improved is None:
            break
        bins = improved
    return bins

# 随机搜索 + 局部改进 + 时限控制
def random_search_fit(items, capacity, fit_fun, iterations=1000, time_limit=30):
    best_solution = None
    min_bins = float('inf')
    start_search = time.time()  # 记录本次搜索开始时间

    for _ in range(iterations):
        # 超过时间限制，提前退出
        if time.time() - start_search > time_limit:
            print(f"[Warning] 搜索超过 {time_limit}s，提前退出随机搜索。")
            break

        tmp_items = items[:]       # 复制列表
        random.shuffle(tmp_items)

        # 先 Best Fit，再局部合并
        sol = fit_fun(tmp_items, capacity)
        sol = local_search(sol, capacity)

        if len(sol) < min_bins:
            min_bins = len(sol)
            best_solution = sol

    return best_solution

if __name__ == "__main__":
    random.seed(0)

    script_dir      = os.path.dirname(os.path.abspath(__file__))
    json_file_path  = os.path.join(script_dir, 'CW_ins.json')
    output_filename = '20513824_Yuanhao_Dai.json'

    instances = read_bin_packing_instances(json_file_path)

    total_bins = 0
    output_json = {
        'date': datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
        'time': 0,
        'res': []
    }

    for ins in instances:
        start_time_sol = time.time()

        # 传入 time_limit=30，单次随机搜索不超过 30 秒
        solution = random_search_fit(
            ins['items'], ins['capacity'],
            best_fit, iterations=1000, time_limit=30
        )
        bin_used = len(solution)
        total_bins += bin_used

        output_json['res'].append({
            'name': ins['name'],
            'capacity': ins['capacity'],
            'solution': solution
        })

        print(f"Instance: {ins['name']}")
        print(f"Bins Used:\t{bin_used} (Time: {time.time() - start_time_sol:.4f}s)")

    total_time = time.time() - start_time
    output_json['time'] = total_time
    with open(output_filename, 'w+') as f:
        json.dump(output_json, f, indent=4)

    print("\n--- Summary ---")
    print(f"Output saved to {output_filename}")
    print(f"Total Used Bins: {total_bins}")
    print(f"Total Execution Time: {total_time:.4f}s")
