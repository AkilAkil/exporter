# import pdb
import time
import re
from prometheus_client import start_http_server
from prometheus_client import Gauge
import os
import platform
import subprocess
from threading import Thread


# pdb.set_trace()
# f = open('./input.txt', 'r')

# start_http_server(8000)

# i = Info('my_build_version', 'Description of info')
# i.info({'version': '1.2.3', 'buildhost': 'foo@bar'})


rx_pps = Gauge('flexran_rx_pps', 'Flexran Received traffic in pps')
tx_pps = Gauge('flexran_tx_pps', 'Flexran Transmitted traffic in pps')
rx_kbps = Gauge('flexran_rx_kbps', 'Flexran Received traffic in kbps')
tx_kbps = Gauge('flexran_tx_kbps', 'Flexran Transmitted traffic in kbps')
ic_labels_list=["CPU_core", "metric","hostname"]
core_met = Gauge('CPU', 'Number of objects', ic_labels_list)
cores = os.getenv("CORES_TO_MONITOR" ,  "0,3")
hostname=platform.node()

def main():
    start_http_server(8000)
    Thread(target = gather_metrics).start()
    Thread(target = parse_core_metrics).start()
    while True:
        pass
        


def parse_core_metrics():
    while True:
        try:
            output = subprocess.getoutput("mpstat -P " + cores + " 1 1")
        except subprocess.CalledProcessError as exc:
            print("Internal error: " + str(exc))
            print(exc.output)
        output = output.partition("Average")[0]
        row=output.split('\n')
        all_cores = row[3:]
        idx = row[2].split().index("CPU")  
        met_name = row[2].split()[idx:]
        for each in range(len(all_cores)):
            met = all_cores[each].split()[idx:]
            if met:
                for i in range(len(met_name)):
                    core_met.labels( "core" + met[0], met_name[i], hostname).set(float(met[i]))
        time.sleep(5)


def gather_metrics():


    print("collecting metrics...")
    
    # Parse Line
    time_check_pattern = "(?<=l1app \[)(.*?)(?=\s*\])"
    packets_check_pattern = "(?<=(Rx|Tx): )(.*?)(?=\])"
    for line in follow_log():
        if line.startswith("==== l1app"):
            result = re.findall(time_check_pattern, line)[0]
            print(result)
        if line.startswith("            "):
            result = re.findall(packets_check_pattern, line)
            if len(result) > 0:
               print(result[0])
               values = result[0][1].split()
               if result[0][0] == "Rx":
                 rx_pps.set(float(values[0].replace(',','')))
                 rx_kbps.set(float(values[2].replace(',','')))
               elif result[0][0] == "Tx":
                 tx_pps.set(float(values[0].replace(',','')))
                 tx_kbps.set(float(values[2].replace(',','')))
               # i.info({"Type":result[0][0], "pps": values[0], "kbps": values[2]})
       # i.info({'version': '1.2.3', 'buildhost': 'foo@bar'})


def follow_log():
    if not os.path.isfile('/applogs/l1.txt'):
        with open('/applogs/l1.txt', 'w+') as f:
            print("Created file: "+f.name)
    with open('/applogs/l1.txt', 'r', encoding='iso-8859-1') as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = ''
            while len(line) == 0 or line[-1] != '\n':
                tail = f.readline() # .decode('utf-8')
                if tail == '':
                    break
                    time.sleep(0.1)  # avoid busy waiting
                    continue
                line += tail
            yield line

if __name__ == '__main__':
    main()

