import os
import json
import csv
def load_data(prefix_path):
    data_temp = []
    exsit_task = 0
    try:
        for pre in os.listdir(prefix_path):
            mid_path = os.path.join(prefix_path, pre)
            exsit_task+=1
            for path in os.listdir(mid_path):
                file_path = os.path.join(mid_path, path)
                if file_path.endswith(".json"):
                    with open(file_path, 'r') as f:
                        line = json.load(f)
                        # line.pop("messages")
                        line["identity"]=int(pre.split("_")[0])
                        data_temp.append(line)
        print(pre)
    except Exception as e:
        print(e)
    print(f"--评测成功数量:{len(data_temp)}, 正在评测数量:{exsit_task-len(data_temp)},剩余评测数量:{784-exsit_task}--")
    return data_temp

def export_csv(model1_data, model):
    # 将dict转换为csv
    with open(f'./data/result/{model}.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        # 写入表头
        dic = {
            "identity": model1_data[0]["identity"],
            "scene": model1_data[0]["scene"],
            "tasktype": model1_data[0]["tasktype"],
            "instruction_idx": model1_data[0]["instruction_idx"],
            "taskname": model1_data[0]["taskname"],
            "key_actions": model1_data[0]["key_actions"],
            "trajectory_actions": model1_data[0]["trajectory"],
            "success": model1_data[0]["metrics"]["success"],
            "efficiency": model1_data[0]["metrics"]["efficiency"],
            "completeness": model1_data[0]["metrics"]["completeness"],
            
        }
        writer.writerow(dic.keys())
        for line in model1_data:
            dic = {
                "identity": line["identity"],
                "scene": line["scene"],
                "tasktype": line["tasktype"],
                "instruction_idx": line["instruction_idx"],
                "taskname": line["taskname"],
                "key_actions": line["key_actions"],
                "trajectory_actions": [t["action"]+" "+t["object"]+"_"+str(t["success"]) if t["object"] is not None else t["action"] +"_"+ str(t["success"]) for t in line['trajectory'] ],
                "success": line["metrics"]["success"],
                "efficiency": line["metrics"]["efficiency"],
                "completeness": line["metrics"]["completeness"],
                
            }
            writer.writerow(dic.values())


def contrast_keyactions(failed_data, model):
    data = []
    with open(f'./data/result/{model}.jsonl',"w") as f:
        for line in failed_data:
            if "identity" not in line:
                print(model)
            dic = {
                "identity":line["identity"],
                "scene": line["scene"],
                "task_type":f"{line['tasktype']}_{line['scene']}_{line['instruction_idx']}",
                "key_actions": line["key_actions"],
                "model_actions": [t["action"]+" "+t["object"]+"_"+str(t["success"]) if t["object"] is not None else t["action"] +"_"+ str(t["success"]) for t in line['trajectory'] ]
            }
            data.append(dic)
            f.write(json.dumps(dic)+"\n")
    error_type_cls(data)

def model1_vs_model2(model1="", model2=""):

    prefix_path = f"./data/{model1}"
    model1_data= load_data(prefix_path)
    prefix_path = f"./data/{model2}"
    model2_data = load_data(prefix_path)

    model1_data = sorted(model1_data, key=lambda x :x["identity"])
    model2_data = sorted(model2_data, key=lambda x :x["identity"])
    export_csv(model1_data, model1)
    export_csv(model2_data, model2)
    id2line={}
    for line in model1_data:
        id2line[line["identity"]]=line

    id2line2={}
    for line in model2_data:
        id2line2[line["identity"]]=line

    model1_success_model2_failed = []
    model2_success_model1_failed = []
    model2_failed_model1_failed = []
    model1_failed_data = []
    model2_failed_data = []

    for id in id2line2:
        if id not in id2line:
            continue
        
        if id2line[id]["metrics"]["success"] == 0:
            model1_failed_data.append(id2line[id])
        if id2line2[id]["metrics"]["success"] == 0:
            model2_failed_data.append(id2line2[id])
        model1_a = [t["action"]+" "+t["object"]+"_"+str(t["success"]) if t["object"] is not None else t["action"] +"_"+ str(t["success"]) for t in id2line[id]['trajectory'] ]
        model2_a = [t["action"]+" "+t["object"]+"_"+str(t["success"]) if t["object"] is not None else t["action"] +"_"+ str(t["success"]) for t in id2line2[id]['trajectory'] ]
        
        
        dic = {
                "identity": id2line2[id]["identity"],
                "scene": id2line2[id]["scene"],
                "tasktype": id2line2[id]["tasktype"],
                "taskname": id2line2[id]["taskname"],
                "key_actions": id2line[id]["key_actions"],
                "objects":[],
                model1: model1_a,
                model2: model2_a,
            }
        # 模型1正确，模型2错误
        if id2line[id]["metrics"]["success"] == 0 and id2line2[id]["metrics"]["success"]==1:
            model1_success_model2_failed.append(dic)

        # 模型2正确，模型1错误
        if id2line2[id]["metrics"]["success"] == 0 and id2line[id]["metrics"]["success"]==1:
            model2_success_model1_failed.append(dic)

        # 模型1、2都错误
        if id2line2[id]["metrics"]["success"] == 0 and id2line[id]["metrics"]["success"]==0:
            for action in dic["key_actions"]:
                if action+"_1" not in model1_a and action.startswith("navigate"):
                    dic["objects"].append(action.split(" ")[-1])
            model2_failed_model1_failed.append(dic)

    model1_success_model2_failed = sorted(model1_success_model2_failed, key=lambda x: x['identity'])
    model2_success_model1_failed = sorted(model2_success_model1_failed, key=lambda x: x['identity'])
    model2_failed_model1_failed = sorted(model2_failed_model1_failed, key=lambda x: x['identity'])
    

    # print(res[0][0])
    print(len(model1_success_model2_failed))

    print(len(model2_success_model1_failed))
    
    with open(f"./data/result/model1_success_model2_failed.jsonl","w") as f:
        for line in model1_success_model2_failed:
            f.write(json.dumps(line, ensure_ascii=False)+"\n")
    
    with open(f"./data/result/model2_success_model1_failed.jsonl","w") as f:
        for line in model2_success_model1_failed:
            f.write(json.dumps(line, ensure_ascii=False)+"\n")


    with open(f"./data/result/model2_failed_model1_failed.jsonl","w") as f:
        for line in model2_failed_model1_failed:
            f.write(json.dumps(line, ensure_ascii=False)+"\n")
    
    return model1_failed_data, model2_failed_data, model2_failed_model1_failed

def error_type_cls(data):
    print("all:",len(data))
    type1 = [] # 导航到目标容器后又导航到其他地方
    pre_action = ""
    pre_success = ""
    for line in data:
        for action in line["model_actions"]:
            action, success = action.split("_")
            if action.startswith("navigate") \
            and pre_action.startswith("navigate") \
            and pre_action in line["key_actions"] \
            and pre_success == "1":
                if "err_type" in line:
                    line["err_type"].append("type1")
                else:
                    line["err_type"] = ["type1"]
                type1.append(line)
                break
            pre_success = success
            pre_action = action
    print("type1:",len(type1))
    type2 = [] # 导航到非目标容器，进行目标物体操作
    pre_action = ""
    pre_success = ""
    for line in data:
        for action in line["model_actions"]:
            action, success = action.split("_")
            
            if not action.startswith("navigate") \
            and not action.startswith("observe") \
            and not action.startswith("move") \
            and not action.startswith("end") \
            and action in line["key_actions"] \
            and success == "0" \
            and pre_action.startswith("navigate") \
            and pre_action not in line["key_actions"] \
            and pre_success == "1":
                if "err_type" in line:
                    line["err_type"].append("type2")
                else:
                    line["err_type"] = ["type2"]
                type2.append(line)
                break
            pre_success = success
            pre_action = action
    print("type2:",len(type2))

    type3 = [] # 模拟器导航到目标容器失败
    for line in data:
        for action in line["model_actions"]:
            action, success = action.split("_")
            if action.startswith("navigate") and action in line["key_actions"] and success =="0":
                if "err_type" in line:
                    line["err_type"].append("type3")
                else:
                    line["err_type"] = ["type3"]
                type3.append(line)
                break
    print("type3:",len(type3))

    type4 = [] # 未探索到目标容器
    for line in data:
        for action in line["key_actions"]:
            if action.startswith("navigate") \
            and action not in [a.split("_")[0] for a in line["model_actions"]]:
                if "err_type" in line:
                    line["err_type"].append("type4")
                else:
                    line["err_type"] = ["type4"]
                type4.append(line)
                break
    print("type4:",len(type4))

    type5 = [] # 模拟器导航到目标容器成功，操作目标物体失败
    pre_success=""
    pre_action=""

    def pre_key_action(key_actions, action):
        # 获取数组某个元素的index
        index = [i for i in range(len(key_actions)) if key_actions[i] == action][0]
        return key_actions[index-1]

    for line in data:
        for action in line["model_actions"]:
            action, success = action.split("_")
            if not action.startswith("navigate") \
            and not action.startswith("observe") \
            and not action.startswith("end") \
            and not action.startswith("move") \
            and not action.startswith("put") \
            and action in line["key_actions"] \
            and success == "0" \
            and pre_action == pre_key_action(line["key_actions"], action)\
            and pre_success == "1":
                if "err_type" in line:
                    line["err_type"].append("type5")
                else:
                    line["err_type"] = ["type5"]
                type5.append(line)
                break
            pre_action=action
            pre_success=success
    print("type5:",len(type5))

    othertype=[]
    for line in data:
        if "err_type" not in line:
            othertype.append(line)
    
    print("othertype:",len(othertype))


if __name__=="__main__":
    model1=""
    model2=""
    model1_failed_data, model2_failed_data, model2_failed_model1_failed = model1_vs_model2(model1, model2)
    print(model1_failed_data[0].keys())
    print(model1)
    contrast_keyactions(model1_failed_data, model1)
    print("-"*200)
    print(model2)
    contrast_keyactions(model2_failed_data, model2)

    objects = {}
    # 将dict转换为csv
    with open(f'./data/result/all_falied_data.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        # 写入表头
        dic = model2_failed_model1_failed[0]
        writer.writerow(dic.keys())
        for line in model2_failed_model1_failed:
            for obj in line['objects']:
                if obj =="end":
                    continue
                if obj not in objects:
                    objects[obj]=0
                objects[obj]+=1
            writer.writerow(line.values())


    # import matplotlib.pyplot as plt
    # from collections import Counter
    # count = Counter(data)
    # labels, values = zip(*sorted(count.items()))  # 排序后拆分键值对

    # # 设置柱状图
    # plt.figure(figsize=(10, 6))  # 可选：设置图表大小
    # plt.bar(labels, values, color='blue')  # 绘制柱状图

    # # 添加标题和标签
    # plt.title('错误样本中未完成动作的物品分布')
    # plt.xlabel('物品类型')
    # plt.ylabel('个数')

    # # 显示图表
    # plt.save("/home/zwq/liugangao/projects/embodied_o1/x.png")
    # objects2 = [(obj, objects[obj]) for obj in objects]
    # objects = sorted(objects2, key=lambda x: x[1])
    # print(objects)
    # for obj in objects:
        # print(obj[0], obj[1])
    # for obj,count in objects.items():
        # print(obj,":",count)

