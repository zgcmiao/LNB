import os 
import json
import re
from mininet.clean import cleanup

ROOT = '/home/lzq/llm4network-benchmark'
RESULTS_DIR = "./results"
EXAM_DIR = "./exams"
SUBJECT = "bgp"
NOW_DIR = os.getcwd()

daemons = """
bgpd=yes
ospfd=yes
ospf6d=yes
ripd=yes
ripngd=yes
isisd=yes
pimd=yes
pim6d=yes
ldpd=yes
nhrpd=yes
eigrpd=yes
babeld=yes
sharpd=yes
staticd=yes
pbrd=yes
bfdd=yes
fabricd=yes
vrrpd=yes
pathd=yes

vtysh_enable=yes

zebra_options="  -A 127.0.0.1 -s 90000000"
mgmtd_options="  -A 127.0.0.1"
bgpd_options="   -A 127.0.0.1"
ospfd_options="  -A 127.0.0.1"
ospf6d_options=" -A ::1"
ripd_options="   -A 127.0.0.1"
ripngd_options=" -A ::1"
isisd_options="  -A 127.0.0.1"
pimd_options="   -A 127.0.0.1"
pim6d_options="  -A ::1"
ldpd_options="   -A 127.0.0.1"
nhrpd_options="  -A 127.0.0.1"
eigrpd_options=" -A 127.0.0.1"
babeld_options=" -A 127.0.0.1"
sharpd_options=" -A 127.0.0.1"
pbrd_options="   -A 127.0.0.1"
staticd_options="-A 127.0.0.1"
bfdd_options="   -A 127.0.0.1"
fabricd_options="-A 127.0.0.1"
vrrpd_options="  -A 127.0.0.1"
pathd_options="  -A 127.0.0.1"
"""

vtysh = """service integrated-vtysh-config"""

class Completion_Parser():  # sudo is required

    def __init__(self):
        pass

    def parse_data(self, data_text:str, data_lines:list):
        idx = []
        nodes = []
        confs = []
        for line in data_lines:
            if "Configuration file of" in line or "Configuration file for" in line:
                idx.append(data_lines.index(line))

        for id in idx:
            line = data_lines[id].strip("\n")
            name = re.findall(r"[RH]\d+", line)
            # print(name)
            nodes.append(name[0])
        # print(idx)
        
        # matches = re.findall(r'(frr defaults datacenter)(.*?)(line vty|```|###|end)', data_text, re.DOTALL)
        # print(matches)
        trunc_text = '\n'.join(data_lines[idx[0]:])
        config_sections = re.split(r'Configuration file of [^\n]+:', trunc_text) if "Configuration file of" in data_text else re.split(r'Configuration file for [^\n]+:', trunc_text)
        def strip_multiple(text, chars_to_remove):
            pattern = f"[{re.escape(''.join(chars_to_remove))}]"
            return re.sub(pattern, '', text)

        config_sections = [strip_multiple(section, ['```','###']) for section in config_sections if section.strip()]
        for config in config_sections:
                confs.append(config)

        return nodes, confs


    def process(self, json_path, file_text:str, title): #parse + verify

        title_items = title.split('&')
        if len(title_items) == 3:
            protocol, lab, mode = title_items[0], title_items[1], title_items[2]
        else:
            protocol, lab, mode = title_items[0], title_items[1], 'hard'
        
        lab_path = lab + '_' + mode if len(title_items) == 3 else lab

        json_diretory_path = '/'.join(json_path.split('/')[:-1])
        lab_path = os.path.join(json_diretory_path, lab_path)
        os.makedirs(lab_path, exist_ok=True)
        if 'verify_res.txt' in os.listdir(lab_path):
             return
        try:
            nodes, confs = self.parse_data(file_text, file_text.split('\n'))
        except Exception as e:
            print(e)

        nodes = ['R1', 'R2', 'R3']
        confs = [''] * 3                       
        for id, node in enumerate(nodes):
                try:
                    with open(f'{lab_path}/{node}.conf', 'w') as f:
                        f.write(confs[id])
                    with open(f'{lab_path}/daemons', 'w') as f:
                        f.write(daemons.strip('\n'))
                    with open(f'{lab_path}/vtysh.conf', 'w') as f:
                        f.write(vtysh.strip('\n'))
                except Exception as e:
                    print(lab_path, e)
                    # if 'verify_res.txt' in os.listdir(lab_path): os.system(f"rm {lab_path}/verify_res.txt")
                    continue

        # exam_path = os.path.join(Conf.BASE_PATH, EXAM_DIR)
        exam_path = os.path.join(ROOT, EXAM_DIR)
        script_path = os.path.join(exam_path, protocol, lab, 'topo.py')
        cmd = f'sudo python3 {script_path} --mode {mode} --conf_path {lab_path} --verify'
        
        cleanup()
        if 'verify_res.txt' not in os.listdir(lab_path):
            print(cmd)
            os.system(cmd)
        # subprocess.Popen(cmd, shell=True)
        # print(result.stdout)
        return 

    def main(self, output_directory_path:str):
        json_path = [os.path.join(output_directory_path, file) for file in os.listdir(output_directory_path) if file.endswith('json')][0]
        
        with open(json_path, 'r') as f:
            lines = f.readlines()

        list_dict_texts = []
        for line in lines:
            list_dict_texts.append(json.loads(line))

        for dict_text in list_dict_texts: 
            file_text = dict_text['answer']
            title = dict_text['title']
            self.process(json_path, file_text, title)
        return
    

class JSON_Topo_Parser():

    def __init__(self):
        pass

    def verify_num_of_nodes(self, dict_item:dict)->bool:
        dict_json = eval(dict_item['prompt'].split('\n')[1])
        length = str(len(dict_json['nodes']))
        ans = dict_item['answer']
        return length in ans

    def verify_ip_intf(self, dict_item:dict)->bool:
        dict_json = eval(dict_item['prompt'].split('\n')[1])
        question = dict_item['prompt'].split('\n')[3]
        intf = re.search(r'of\s+(.*)\?$', question).group(1)
        if '-' in intf:
            node = intf.split('-')[0]
        else:
            node = dict_json['nodes'][0]
        ip = dict_json['nodes_info'][node]['interface_IP'][intf]
        ans = dict_item['answer']
        return ip in ans

    def verify_name_intf(self, dict_item:dict)->bool:
        dict_json = eval(dict_item['prompt'].split('\n')[1])
        question = dict_item['prompt'].split('\n')[3]
        node = re.search(r'of\s+(.*)\?$', question).group(1)
        ans = dict_item['answer']
        list_intf = dict_json['nodes_info'][node]['interfaces']
        for intf in list_intf:
            if intf not in ans:
                return False
        return True
        

    def verify_num_of_links(self, dict_item:dict)->bool:
        dict_json = eval(dict_item['prompt'].split('\n')[1])
        length = str(len(dict_json['links_info']))
        ans = dict_item['answer']
        return length in ans

    def verify_link_existence(self, dict_item:dict)->bool:
        dict_json = eval(dict_item['prompt'].split('\n')[1])
        question = dict_item['prompt'].split('\n')[3]
        intf = re.search(r'interface\s+(.*?)\shas', question).group(1)
        list_links = dict_json['links_info']
        ans = dict_item['answer']
        gd = False
        _intf = ''
        for link in list_links:
            if intf in list(link.values()):
                _values = list(link.values())
                _values.remove(intf)
                _intf = _values[0]
                gd = True
                break

        if _intf:
            return 'Yes' in ans or 'yes' in ans or _intf in ans
        else:
            return 'No' in ans or 'no' in ans


    def main(self, path='lab_output_json_topo'): #/home/lzq/llm-bench/lab_output/json_topo/model/huggyllama-llama-7b
        list_dir = os.listdir(path)
        file = [f for f in list_dir if f.endswith('.json')][0]
        json_path = os.path.join(path, file)
        with open(json_path, 'r') as f:
            lines = f.readlines()

            
        list0, list1, list2, list3, list4 = [], [], [], [], []
        for id, line in enumerate(lines):
            try:
                if id % 5 == 0:
                    list0.append(json.loads(line))     
                elif id % 5 == 1:
                    list1.append(json.loads(line))
                elif id % 5 == 2:
                    list2.append(json.loads(line))
                elif id % 5 == 3:
                    list3.append(json.loads(line))
                else:
                    list4.append(json.loads(line))
            except:
                print(json_path)

            res0 = list(map(self.verify_num_of_nodes, list0))
            res1 = list(map(self.verify_ip_intf, list1))
            res2 = list(map(self.verify_name_intf, list2))
            res3 = list(map(self.verify_num_of_links, list3))
            res4 = list(map(self.verify_link_existence, list4))

            list_all = [res0, res1, res2, res3, res4]

            res = sum(list(map(lambda l: 100*len([r for r in l if r])/len(l), list_all)))/5

            with open(os.path.join(path, 'res.txt'), 'w') as f:
                f.write(str(res))

            # print(model, 100*len([r for r in res0 if r])/len(res0), 100*len([r for r in res1 if r])/len(res1), 100*len([r for r in res2 if r])/len(res2), 100*len([r for r in res3 if r])/len(res3), 100*len([r for r in res4 if r])/len(res4))
            # print(model, round(res,2))


class Safety_Parser(): # GPT-4 api is required

    def __init__(self) -> None:
        pass


if __name__ == '__main__':
    parser = Completion_Parser()
    parser.main('/home/lzq/llm4network-benchmark/lab_output/model/huggyllama-llama-7b')