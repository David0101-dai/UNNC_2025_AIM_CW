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

def pso_search(items, capacity,
               num_particles=50, iterations=200,
               w=1.0, c1=1.5, c2=1.5,
               vmax=1.0, time_limit=30):
    n = len(items)
    # 初始化粒子
    swarm = []
    for _ in range(num_particles):
        pos = [random.uniform(-1,1) for _ in range(n)]
        vel = [0.0]*n
        # 解码：按 pos 排序得到顺序
        order = sorted(range(n), key=lambda i: pos[i], reverse=True)
        perm = [items[i] for i in order]
        sol = local_search(best_fit(perm, capacity), capacity)
        cnt = len(sol)
        swarm.append({
            'pos': pos,
            'vel': vel,
            'pbest_pos': pos[:],
            'pbest_count': cnt
        })
    # 全局最优
    gbest_pos = min(swarm, key=lambda p: p['pbest_count'])['pbest_pos'][:]
    gbest_count = min(p['pbest_count'] for p in swarm)
    start = time.time()
    # 迭代
    for it in range(iterations):
        if time.time() - start > time_limit:
            print(f"[PSO] 超时 {time_limit}s，停止于迭代 {it}")
            break
        for p in swarm:
            # 更新速度与位置
            for i in range(n):
                r1, r2 = random.random(), random.random()
                p['vel'][i] = (w*p['vel'][i]
                               + c1*r1*(p['pbest_pos'][i]-p['pos'][i])
                               + c2*r2*(gbest_pos[i]-p['pos'][i]))
                # 限幅
                if p['vel'][i] > vmax: p['vel'][i] = vmax
                if p['vel'][i] < -vmax: p['vel'][i] = -vmax
                p['pos'][i] += p['vel'][i]
            # 解码并评估
            order = sorted(range(n), key=lambda i: p['pos'][i], reverse=True)
            perm = [items[i] for i in order]
            sol = local_search(best_fit(perm, capacity), capacity)
            cnt = len(sol)
            # 更新 pbest
            if cnt < p['pbest_count']:
                p['pbest_count'] = cnt
                p['pbest_pos'] = p['pos'][:]
                # 更新 gbest
                if cnt < gbest_count:
                    gbest_count = cnt
                    gbest_pos = p['pos'][:]
        if it%50==0 or it==iterations-1:
            print(f"Iter {it}, Best bins={gbest_count}")
    # 最后解码全局最优
    order = sorted(range(n), key=lambda i: gbest_pos[i], reverse=True)
    perm = [items[i] for i in order]
    return local_search(best_fit(perm, capacity), capacity)

if __name__=='__main__':
    random.seed(0)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(script_dir, 'CW_ins.json')
    output_filename = '20513824_Yuanhao_Dai.json'

    instances = read_bin_packing_instances(json_file_path)
    total_bins = 0
    output_json = {'date': datetime.today().strftime('%Y-%m-%d %H:%M:%S'), 'time':0, 'res':[]}

    for ins in instances:
        t0sol = time.time()
        solution = pso_search(
            ins['items'], ins['capacity'],
            num_particles=50, iterations=500,
            w=1.0, c1=1.5, c2=1.5,
            vmax=1.0, time_limit=30
        )
        used = len(solution)
        total_bins += used
        output_json['res'].append({'name':ins['name'],'capacity':ins['capacity'],'solution':solution})
        print(f"Instance: {ins['name']}")
        print(f"Bins Used:\t{used} (Time: {time.time()-t0sol:.4f}s)")

    output_json['time']=time.time()-t0
    with open(output_filename,'w+') as f:
        json.dump(output_json,f,indent=4)

    print("\n--- Summary ---")
    print(f"Output saved to {output_filename}")
    print(f"Total Used Bins: {total_bins}")
    print(f"Total Execution Time: {time.time()-t0:.4f}s")
