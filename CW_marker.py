import json
import os  # 用于处理文件路径

def read_json(json_file_path):
    with open(json_file_path, 'r') as file:
        instances = json.load(file)
    return instances

if __name__ == "__main__":
     # 确定脚本真正所在的目录：
    script_dir     = os.path.dirname(os.path.abspath(__file__))
    instances_path = os.path.join(script_dir, 'CW_ins.json')
    solution_path  = os.path.join(script_dir, '20513824_Yuanhao_Dai.json')

    instances = read_json(instances_path)
    solution  = read_json(solution_path)

    best_known = [
        52,
        59,
        24,
        27,
        47,
        49,
        36,
        52,
        417,
        375
    ]

    # check 
    passed = True
    if solution.get('time', float('inf')) > 300:
        print("Time exceed limit!")
        passed = False
    else:
        results = solution['res']
        total_bin_num = 0
        total_mark    = 0
        total_bonus   = 0

        for ins, res, bk in zip(instances, results, best_known):
            items    = ins['items']
            capacity = ins['capacity']
            name     = ins['name']

            sol       = res['solution']
            sol_items = []
            bin_num   = len(sol)

            # 名称校验
            if name != res.get('name', ''):
                print(f"\n--- Error ---\nInstance: {name}\tInstance name error!\n")
                passed = False

            # 容量校验 & 收集所有放入的物品
            for b in sol:
                if sum(b) > capacity:
                    print(f"\n--- Error ---\nInstance: {name}\tCapacity error!\n")
                    passed = False
                sol_items += b

            # 物品完整性校验
            if sorted(items) != sorted(sol_items):
                print(f"\n--- Error ---\nInstance: {name}\tItem list error!\n")
                passed = False

            # 评分逻辑
            gap  = bin_num - bk
            mark = 0
            bonus = 0
            if gap < 0:
                bonus = 3
                mark  = 3
            elif gap == 0:
                mark = 3
            elif gap <= 1:
                mark = 2
            elif gap <= 2:
                mark = 1
            elif gap <= 3:
                mark = 0.5

            print(f"Instance: {name}\tMark: {mark}\tBonus: {bonus}\tBins used/Best known: {bin_num}/{bk}")
            total_bin_num += bin_num
            total_mark    += mark
            total_bonus   += bonus

    # 打印总结
    print("\n--- Summary ---")
    print(f"Total Bin:    {total_bin_num}")
    print(f"Run Time:     {round(solution.get('time',0),2)} s")
    if passed:
        print(f"Bonus mark:   {total_bonus}")
        print(f"Total mark:   {total_mark + total_bonus} / 30")
        print("Passed")
    else:
        print("Total mark:   0 / 30")
        print("Failed")
