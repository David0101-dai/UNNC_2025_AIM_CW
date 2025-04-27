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

# Best Fit 解码（无需排序）
def best_fit(items, capacity):
    bins = []
    contents = []
    for x in items:
        idx = -1
        min_space = capacity + 1
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

# 计算某个排列的箱子数（适应度低则好）
def decode_and_count(indiv, items, capacity):
    permuted = [items[i] for i in indiv]
    sol = best_fit(permuted, capacity)
    return sol, len(sol)

# 轮盘赌选择
def roulette_wheel_select(population, scores):
    total = sum(scores)
    if total == 0:
        return random.choice(population)
    pick = random.uniform(0, total)
    cum = 0
    for indiv, score in zip(population, scores):
        cum += score
        if cum >= pick:
            return indiv
    return population[-1]

# 单点交叉 + 简单修复为排列
def crossover(parent1, parent2):
    n = len(parent1)
    pt = random.randint(1, n-1)
    child = parent1[:pt] + [g for g in parent2 if g not in parent1[:pt]]
    return child

# 交换变异
def mutate(indiv):
    a, b = random.sample(range(len(indiv)), 2)
    indiv[a], indiv[b] = indiv[b], indiv[a]

# 遗传算法主过程
def genetic_fit(items, capacity,
                pop_size=100, generations=500,
                crossover_rate=0.8, mutation_rate=0.1,
                time_limit=60):
    n = len(items)
    # 初始化种群：随机排列
    population = [random.sample(range(n), n) for _ in range(pop_size)]
    best_solution, best_count = None, float('inf')
    start = time.time()

    for gen in range(generations):
        # 时间终止
        if time.time() - start > time_limit:
            print(f"[GA] 超时 {time_limit}s，停止于代 {gen}")
            break
        # 评估适应度（反转箱数，使得较少箱获得更大权重）
        decoded = [decode_and_count(ind, items, capacity) for ind in population]
        counts = [cnt for sol, cnt in decoded]
        max_cnt = max(counts)
        # 分数 = max_cnt - cnt + 1
        scores = [max_cnt - cnt + 1 for cnt in counts]
        # 更新全局最优
        for sol, cnt in decoded:
            if cnt < best_count:
                best_solution, best_count = sol, cnt
        # 生成新种群
        new_pop = []
        while len(new_pop) < pop_size:
            p1 = roulette_wheel_select(population, scores)
            if random.random() < crossover_rate:
                p2 = roulette_wheel_select(population, scores)
                child = crossover(p1, p2)
            else:
                child = p1.copy()
            if random.random() < mutation_rate:
                mutate(child)
            new_pop.append(child)
        population = new_pop

    return best_solution

if __name__ == '__main__':
    random.seed(0)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(script_dir, 'CW_ins.json')
    output_filename = '20513824_Yuanhao_Dai.json'

    instances = read_bin_packing_instances(json_file_path)
    total_bins = 0
    output_json = {'date': datetime.today().strftime('%Y-%m-%d %H:%M:%S'), 'time': 0, 'res': []}

    for ins in instances:
        t0_sol = time.time()
        solution = genetic_fit(
            ins['items'], ins['capacity'],
            pop_size=100, generations=1000,
            crossover_rate=0.8, mutation_rate=0.1,
            time_limit=60
        )
        used = len(solution)
        total_bins += used
        output_json['res'].append({'name': ins['name'], 'capacity': ins['capacity'], 'solution': solution})
        print(f"Instance: {ins['name']}")
        print(f"Bins Used:\t{used} (Time: {time.time()-t0_sol:.4f}s)")

    output_json['time'] = time.time() - t0
    with open(output_filename, 'w+') as f:
        json.dump(output_json, f, indent=4)

    print("\n--- Summary ---")
    print(f"Output saved to {output_filename}")
    print(f"Total Used Bins: {total_bins}")
    print(f"Total Execution Time: {time.time()-t0:.4f}s")
