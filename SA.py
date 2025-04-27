import json
import random
import time
import os
import math
import copy
from datetime import datetime

# 开始计时
start_time = time.time()

def read_bin_packing_instances(json_file_path):
    with open(json_file_path, 'r') as file:
        instances = json.load(file)
    return instances

# Best Fit 算法：直接按照输入顺序放置，不做排序
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

# 模拟退火二次改进
# 在当前解上尝试移动或交换物品，接受更优或以概率接受更差解
def simulated_annealing(bins, capacity, init_temp=1000.0, alpha=0.95, min_temp=1e-3, max_iters=1000):
    current = [list(b) for b in bins]
    best = [list(b) for b in bins]
    curr_count = len(current)
    best_count = curr_count
    temp = init_temp
    iters = 0
    while temp > min_temp and iters < max_iters:
        neighbor = copy.deepcopy(current)
        i = random.randrange(len(neighbor))
        if not neighbor[i]:
            iters += 1
            temp *= alpha
            continue
        item = random.choice(neighbor[i])
        j_choices = [idx for idx in range(len(neighbor)) if idx != i]
        if not j_choices:
            iters += 1
            temp *= alpha
            continue
        j = random.choice(j_choices)
        if sum(neighbor[j]) + item <= capacity:
            neighbor[i].remove(item)
            neighbor[j].append(item)
            neighbor = [b for b in neighbor if b]
        else:
            if neighbor[j]:
                j_item = random.choice(neighbor[j])
                if sum(neighbor[i]) - item + j_item <= capacity and sum(neighbor[j]) - j_item + item <= capacity:
                    neighbor[i].remove(item)
                    neighbor[i].append(j_item)
                    neighbor[j].remove(j_item)
                    neighbor[j].append(item)
        neigh_count = len(neighbor)
        delta = neigh_count - curr_count
        if delta <= 0 or random.random() < math.exp(-delta / temp):
            current = neighbor
            curr_count = neigh_count
            if curr_count < best_count:
                best = [list(b) for b in current]
                best_count = curr_count
        temp *= alpha
        iters += 1
    return best

# 随机搜索 + 局部改进 + 时限控制（不含退火）
def random_search_fit(items, capacity, fit_fun, iterations=1000, time_limit=60):
    best_solution = None
    min_bins = float('inf')
    start_search = time.time()
    for _ in range(iterations):
        if time.time() - start_search > time_limit:
            print(f"[Warning] 搜索超过 {time_limit}s，提前退出随机搜索。")
            break
        tmp_items = items[:]
        random.shuffle(tmp_items)
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

        # 第一步：随机搜索 + 局部搜索
        base_solution = random_search_fit(
            ins['items'], ins['capacity'], best_fit, iterations=1000, time_limit=60
        )
        base_count = len(base_solution)

        # 第二步：退火二次改进
        annealed_solution = simulated_annealing(base_solution, ins['capacity'])
        annealed_count = len(annealed_solution)

        # 如果退火结果更优，则采用；否则保留原解
        if annealed_count < base_count:
            solution = annealed_solution
            bin_used = annealed_count
        else:
            solution = base_solution
            bin_used = base_count

        total_bins += bin_used

        output_json['res'].append({
            'name': ins['name'],
            'capacity': ins['capacity'],
            'solution': solution
        })

        print(f"Instance: {ins['name']}")
        print(f"Bins Used:\t{bin_used} (Base: {base_count}, Annealed: {annealed_count}, Time: {time.time() - start_time_sol:.4f}s)")

    total_time = time.time() - start_time
    output_json['time'] = total_time
    with open(output_filename, 'w+') as f:
        json.dump(output_json, f, indent=4)

    print("\n--- Summary ---")
    print(f"Output saved to {output_filename}")
    print(f"Total Used Bins: {total_bins}")
    print(f"Total Execution Time: {total_time:.4f}s")
