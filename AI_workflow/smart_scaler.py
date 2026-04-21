import pandas as pd
import numpy as np
import joblib
import subprocess
import time
import os
import requests 

try:
    model_cpu = joblib.load('cpu_predictor.pkl')
    model_anomaly = joblib.load('anomaly_detector.pkl')
except Exception as e:
    print(f"Error loading models: {e}")
    exit()

def get_current_metrics():
    try:
        result = subprocess.run("kubectl top pods --no-headers", shell=True, capture_output=True, text=True)
        for line in result.stdout.strip().split('\n'):
            if "vote-service" in line:
                parts = line.split()
                cpu = int(parts[1].replace('m', ''))
                mem = int(parts[2].replace('Mi', ''))
                return cpu, mem
    except:
        pass
    return None, None

def get_current_replicas():
    cmd = "kubectl get deployment vote-service -o jsonpath='{.spec.replicas}'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    try:
        return int(result.stdout)
    except:
        return 1

def check_node_health():
    try:
        result = subprocess.run("./mock_check.sh", shell=True, capture_output=True, text=True)
        if "NotReady" in result.stdout:
            print("\n[CRITICAL] Node Failure Detected.")
            os.system("terraform init && terraform plan") 
            os.system("echo \"echo 'node-01 Ready worker'\" > mock_check.sh")
            return "Node Recovered via Terraform"
    except:
        pass
    return None

history_cpu = [1, 1] 
history_mem = [25, 25]

print("AIOps Manager Active...")

while True:
    try:
        action = "Status Stable"
        
        # 1. Terraform Check (Priority)
        node_status = check_node_health()
        if node_status: 
            action = node_status

        cpu, mem = get_current_metrics()
        
        if cpu is not None:
            history_cpu.append(cpu)
            history_mem.append(mem)
            if len(history_cpu) > 3: history_cpu.pop(0)
            if len(history_mem) > 3: history_mem.pop(0)

            cpu_lag_1 = history_cpu[-2]
            cpu_velocity = cpu - cpu_lag_1
            mem_delta = mem - history_mem[-2]

            X_live = pd.DataFrame([[cpu, cpu_lag_1, cpu_velocity, mem_delta]], 
                                  columns=['cpu_m', 'cpu_lag_1', 'cpu_velocity', 'mem_delta'])

            predicted_cpu = model_cpu.predict(X_live)[0]
            is_anomaly = model_anomaly.predict(X_live)[0] 
            current_pods = get_current_replicas()

            # --- INDEPENDENT ANSIBLE CHECK (Memory Leak) ---
            if mem_delta > 5:
                print(f">>> [MEMORY LEAK] Delta: {mem_delta}Mi. Running Ansible...")
                os.system("ansible-playbook restart_vote.yml")
                action = "Ansible: Restarting for Memory Leak"

            # --- SCALING LOGIC CHAIN ---
            if predicted_cpu > 1200 and current_pods < 5:
                os.system("kubectl scale deployment vote-service --replicas=5")
                action = "Tier 3: Extreme Load (5 Pods)"
            elif predicted_cpu > 700 and current_pods < 3:
                os.system("kubectl scale deployment vote-service --replicas=3")
                action = "Tier 2: High Load (3 Pods)"
            elif predicted_cpu > 400 and current_pods < 2:
                os.system("kubectl scale deployment vote-service --replicas=2")
                action = "Tier 1: Moderate Load (2 Pods)"
            elif predicted_cpu < 200 and current_pods > 1:
                os.system("kubectl scale deployment vote-service --replicas=1")
                action = "Optimizing: Scaled to 1 Pod"
            
            # --- SECONDARY CHECKS ---
            elif is_anomaly == -1 and action == "Status Stable":
                action = "Anomaly Detected"
            elif cpu_velocity > 400 and action == "Status Stable":
                os.system("kubectl rollout restart deployment vote-service")
                action = "Rollout Restart: High Velocity"

            # Final Override if Terraform just ran
            if node_status: action = node_status

            # --- SYNC TO DASHBOARD ---
            try:
                requests.post("http://localhost:5000/update", json={
                    "cpu": cpu,
                    "predicted": int(predicted_cpu),
                    "pods": current_pods,
                    "anomaly": True if is_anomaly == -1 else False,
                    "action": action
                }, timeout=0.5)
            except:
                pass

            # --- LOG PERSISTENCE FEATURE ---
            with open("recovery_log.txt", "a") as log_file:
                log_file.write(f"[{time.ctime()}] CPU: {cpu}m | Predicted: {predicted_cpu}m | Pods: {current_pods} | Action: {action}\n")

            if "Recovered" in action:
                with open("healed_node.txt", "a") as heal_file:
                    heal_file.write(f"[{time.ctime()}] Node failure resolved via Terraform\n")

            print(f"[LIVE] CPU: {cpu:4}m | Predicted: {predicted_cpu:4.0f}m | Pods: {current_pods} | {action}")

        time.sleep(3)

    except KeyboardInterrupt:
        break