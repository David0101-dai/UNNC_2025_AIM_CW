import json
import random
import time
import os
from datetime import datetime

# 开始计时
t0 = time.time()

def read_bin_packing_instances(json_file_path):
    with open(json_file_path, 'r') as f:
        return json.load(f)

# Best Fit 算法（解码使用）
def best_fit(items, capacity):
    bins = []
    contents = []
    for x in items:
        idx, min_space = -1, capacity + 1
        for i, used in enumerate(bins):
            space = capacity - used
            if space >= x and space < min_space:
                idx, min_space = i, space
        if idx >= 0:
            bins[idx] += x
            contents[idx].append(x)
        else:
            bins.append(x)
            contents.append([x])
    return contents

# 局部搜索改进
from math import inf

def first_improvement(bins, capacity):
    for i in range(len(bins)):
        for j in range(len(bins)):
            if i != j and sum(bins[i]) + sum(bins[j]) <= capacity:
                merged = bins[i] + bins[j]
                new_bins = [merged if k==i else bins[k] for k in range(len(bins)) if k!=j]
                return new_bins
    return None

def local_search(bins, capacity, max_iters=100):
    for _ in range(max_iters):
        nxt = first_improvement(bins, capacity)
        if not nxt:
            break
        bins = nxt
    return bins

# PSO 搜索：位置向量 -> 排序解码

# Hyper-Heuristic Search: 选择多种装箱策略（LLH）并用 ε-贪心调度 + 重启
LLH_FUNCS = []
def next_fit(items, capacity):
    bins, contents, current = [], [], []
    for x in items:
        if sum(current) + x <= capacity:
            current.append(x)
        else:
            bins.append(sum(current)); contents.append(list(current))
            current = [x]
    if current:
        bins.append(sum(current)); contents.append(list(current))
    return contents

# First Fit 算法
# 按输入顺序放置，填入第一个能放下的箱子

def first_fit(items, capacity):
    bins = []
    contents = []
    for x in items:
        placed = False
        for i in range(len(bins)):
            if bins[i] + x <= capacity:
                bins[i] += x
                contents[i].append(x)
                placed = True
                break
        if not placed:
            bins.append(x)
            contents.append([x])
    return contents

# 准备 LLH 函数列表
LLH_FUNCS = [
    lambda it, C: best_fit(it, C),                           # Best Fit
    lambda it, C: best_fit(sorted(it, reverse=True), C),     # Best Fit Decreasing
    lambda it, C: first_fit(it, C),                          # First Fit
    lambda it, C: next_fit(it, C)                            # Next Fit
]
NUM_LLH = len(LLH_FUNCS)

def select_llh(scores, epsilon):
    # ε-贪心：探索 or 利用
    if random.random() < epsilon:
        return random.randrange(NUM_LLH)
    # 利用：选得分最高
    max_score = max(scores)
    # 多重最优打平随机
    best = [i for i,s in enumerate(scores) if s == max_score]
    return random.choice(best)


def hyper_heuristic_search(items, capacity,
                            epsilon=0.15, max_restarts=100):
    best_sol, best_bins = None, float('inf')
    # 全局 LLH 累积得分（可选用于统计）
    global_scores = [0.0]*NUM_LLH
    for r in range(max_restarts):
        # 重启时本地得分重置
        scores = [0.0]*NUM_LLH
        # 当前最好解为全局最好
        current_best_bins = best_bins
        # 按顺序应用策略直到无改进
        while True:
            idx = select_llh(scores, epsilon)
            # 随机打乱输入顺序，增加多样
            perm = items[:]
            random.shuffle(perm)
            # 调用选中 LLH
            sol = LLH_FUNCS[idx](perm, capacity)
            sol = local_search(sol, capacity)
            cnt = len(sol)
            # 如果得到改进
            if cnt < current_best_bins:
                current_best_bins = cnt
                best_local = sol
                # 提升该 LLH 得分
                scores[idx] += float(best_bins - cnt)
                global_scores[idx] += float(best_bins - cnt)
            else:
                break
        # 重启后比较全局
        if current_best_bins < best_bins:
            best_bins = current_best_bins
            best_sol = best_local
    return best_sol


# --- Main入口 ---
if __name__ == '__main__':
    random.seed(0)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(script_dir, 'CW_ins.json')
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
        solution = hyper_heuristic_search(
            ins['items'], ins['capacity'],
            epsilon=0.15, max_restarts=100
        )
        bin_used = len(solution)
        total_bins += bin_used

        output_json['res'].append({
            'name': ins['name'],
            'capacity': ins['capacity'],
            'solution': solution
        })

        print(f"Instance: {ins['name']}")
        print(f"Bins Used:	{bin_used} (Time: {time.time() - start_time_sol:.4f}s)")

    total_time = time.time() - t0
    output_json['time'] = total_time
    with open(output_filename, 'w+') as f:
        json.dump(output_json, f, indent=4)

    print("\n--- Summary ---")
    print(f"Output saved to {output_filename}")
    print(f"Total Used Bins: {total_bins}")
    print(f"Total Execution Time: {total_time:.4f}s")
