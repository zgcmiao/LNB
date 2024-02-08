import argparse
import json
import os
import tempfile
from pathlib import Path

from evaluation_pipeline import PipelineManager
from model import ModelType
from conf import QuestionType, get_enum_item_by_value, LanguageType, MetricName, Conf
from script import detect_model_type
from script.helper.script_helper import get_default_metric
from utils import CommonHelper

# from lab_res_parse import Completion_Parser, JSON_Topo_Parser

LAB_EXAM_FORMAT = '%s.auto.%s-lab-exam.json'
LAB_EXAM_DIR = 'data/question_bank/lab_exam/exams'
JSON_EXAM_DIR = 'data/question_bank/lab_exam/JSON_test_for_LLM_1'
SAFETY_EXAM_DIR = 'data/question_bank/lab_exam/Safe_test'
BASE_PROMPT = "You are a helpful network expert to write network configuration files using FRRouting software."
OUTPUT_FORMAT = """
Configuration file of <name of the first node>:...
###
Configuration file of <name of the second node>:...
###
...
...
###
Configuration file of <name of the last node>:...
"""
DEFAULT_SHOT_TYPE = "zero-shot"



def _list_exam_item_by_subject_qa_completion(data_dir, breakpoint_file=None):
    # print(f'----------{data_dir}------------')
    protocals = os.listdir(data_dir) 
    subject_test_questions = []

    for proc in protocals:
        labs = os.listdir(os.path.join(data_dir,proc))
        for lab in labs:
                exam_dir = os.path.join(data_dir, proc, lab, 'exam.json')
                with open(exam_dir, 'r') as f:
                    dict_exam = json.load(f)
                    dict_exam.update({'protocol': proc, 'lab': lab})
                    exam_info = dict_exam['exam_description']
                    if isinstance(exam_info, dict):
                        dict_exam.update({'with_level': True})
                        levels = list(exam_info.keys())
                        for level in levels:
                            tmp_dict_exam = dict_exam.copy()
                            tmp_dict_exam.update({'level': level, 'exam_description': '\n'.join(exam_info[level])})
                            subject_test_questions.append(tmp_dict_exam)
                    else:
                        dict_exam.update({'with_level': False, 'exam_description': '\n'.join(exam_info)})
                        subject_test_questions.append(dict_exam)

    return subject_test_questions


def _list_exam_item_by_subject_qa_json(data_dir='JSON_test_for_LLM_1'):
    
    list_json_files = os.listdir(data_dir) 
    list_questions = []

    for json_file in list_json_files:
        with open(os.path.join(data_dir, json_file), 'r') as f:
            dict_question = json.load(f)
        id = dict_question['id']
        questions = dict_question['questions']
        for question in questions:
            question_type = question['title']
            content = question['content']
            dict_tmp = {'id': id, 'question_type': question_type, 'content': content}
            list_questions.append(dict_tmp)

    return list_questions

def _list_exam_item_by_subject_qa_safety(data_dir='Safe_test'):
    list_safety_qa = []
    for p in os.listdir(data_dir):
        path = os.path.join(data_dir, p)
        for case in os.listdir(path):
            with open(os.path.join(path, case), 'r') as f:
                _case = f.read()
            list_safety_qa.append({'id': case[:-4], 'property': p, 'question': _case})

    return list_safety_qa
# def _get_cfg_by_subject(subject):
#     with open(DataManager().get_data_file_path(f'subjects/{subject}.json')) as f_cfg:
#         subject_cfg = json.load(f_cfg)
#     return subject_cfg


def _get_output_name(model_name, finetune_weights):
    if finetune_weights:
        if Path(finetune_weights).is_dir():
            output_model_name = Path(finetune_weights).name.replace('/', '-')
        else:
            output_model_name = finetune_weights.replace('/', '-')
    else:
        output_model_name = model_name.replace('/', '-')
    return output_model_name


def run(model_name: str, model_type: ModelType, version: str, subject='completion', data_dir=LAB_EXAM_DIR, output_dir='lab_output', *args, **kwargs):
    """ run qa

    :param model_name: model name
    :param model_type: model type
    # :param subject: subject
    :param data_dir: data dir
    :param output_dir: output dir
    :param args: args dir
    :param kwargs: kwargs
    """
    cot = kwargs.get('cot')
    rag = kwargs.get('rag')
    dry_run = kwargs.get("dry_run")
    pipeline_id = kwargs.get("pipeline_id")
    finetune_weights = kwargs.get("finetune_weights")
    need_merge_weights = kwargs.get("need_merge_weights")
    language_type = kwargs.get("language_type") or LanguageType.EN
    question_type = kwargs.get("question_type") or QuestionType.LAB_EXAM
    metric_name = kwargs.get("metric_name") or get_default_metric(question_type)
    breakpoint_file = kwargs.get("breakpoint_file")
    customized_model_package = kwargs.get("customized_model_package") or ""

    # print(f'-----------------{subject}----------------')
    # subject_cfg = _get_cfg_by_subject(subject)
    # list_subject_test_questions = _list_exam_item_by_subject(subject_cfg, data_dir, breakpoint_file)
    # print(len(_list_exam_item_by_subject_qa(LAB_EXAM_DIR, breakpoint_file)))
    
    def topo_parse(topo_info:dict):  
            nodes, nodes_info, links_info = topo_info["nodes"], topo_info["nodes_info"], topo_info["links_info"]
            topo_description = f"There are {len(nodes)} nodes in topology.\n\n"
            for node in nodes:
                intfs_num = len(nodes_info[node]['interfaces'])
                intfs_string = " ".join(nodes_info[node]['interfaces'])
                node_description = f"{node} has {intfs_num} interfaces: {intfs_string}."
                for intf in nodes_info[node]["interfaces"]:
                    interface_IP = nodes_info[node]["interface_IP"][intf]
                    node_description += f"{intf} has IP address of {interface_IP}, "
                _node_description = node_description[:-2] + "."
                topo_description += (_node_description + "\n")

            links_description = "The network links are between: "
            for link in links_info:
                link_pair = " and ".join(link.split("<->")) + ", "
                links_description += link_pair

            _links_description = links_description[:-2] + "."
            topo_description += (_links_description + "\n\n")
            return topo_description


    def _prompt_gen_qa_frr(item_content:dict):

        exam_dict = item_content
        exam_type, topo_info, exam_description = exam_dict["exam_type"], exam_dict["topo_info"], exam_dict["exam_description"]
        topo_description = topo_parse(topo_info)

        prompt = BASE_PROMPT + "\n" +  \
                f"This task focuses on {exam_type}. The topology information is as follows:\n{topo_description}\n\n" + \
                f"Your task is to write FRR configuration files for network nodes respectively based on the task description:\n {exam_description}\n\n" + \
                f"You must use FRR rules to configure. And the output must obey the following format:\n" + \
                OUTPUT_FORMAT + "\n\n" + \
                f"You must add \'frr defaults datacenter\' at the beginning of each configuration file."
        
        return prompt

    
    # list_subject_test_questions = ["Do you know network configuration?", "Do you know FRRouting?"]
    # list_subject_test_questions = ["Configure BGP between R1-S0 and R2-S0. "]
    # output_dir = "output_simple_qa"
    if subject == 'intent_completion_command_execution':
        list_subject_test_questions = _list_exam_item_by_subject_qa_completion(LAB_EXAM_DIR, breakpoint_file)[:2]
        _prompt_func = _prompt_gen_qa_frr
        output_dir = f'{output_dir}/intent_completion_command_execution'
    elif subject == 'intent_completion_topo_comprehension':
        list_subject_test_questions = _list_exam_item_by_subject_qa_json(JSON_EXAM_DIR)[:2]
        _prompt_func = lambda item_content: item_content
        output_dir = f'{output_dir}/intent_completion_topo_comprehension'
    elif subject == 'operational_safety':
        list_subject_test_questions = _list_exam_item_by_subject_qa_safety(SAFETY_EXAM_DIR)[:2]
        _prompt_func = lambda item_content: item_content
        output_dir = f'{output_dir}/operational_safety'
    # print(list_subject_test_questions)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        data_path = os.path.join(tmpdir, LAB_EXAM_FORMAT % (pipeline_id, subject))
        with open(data_path, 'w') as f_out:
            json.dump(dict(id=subject, title=subject, questions=list_subject_test_questions), f_out)

            input_file_or_directory_path = data_path
            output_directory_path = f"{output_dir}/model/{_get_output_name(model_name, finetune_weights)}/"
            if os.path.exists(output_directory_path):
                os.system(f'rm -rf {output_directory_path}')
            os.makedirs(output_directory_path)

        pipeline_instance = PipelineManager(version).get_pipeline_instance(model_name,
                                                                            model_type,
                                                                            pipeline_params={
                                                                                "name": model_name,
                                                                                "subject": subject,
                                                                                # "shot_type": DEFAULT_SHOT_TYPE,
                                                                                "input_file_or_directory_path": input_file_or_directory_path,
                                                                                "output_directory_path": output_directory_path,
                                                                                "prompt_generator_func": _prompt_func,
                                                                                "dry_run": dry_run,
                                                                                "pipeline_id": pipeline_id,
                                                                                "question_type": question_type,
                                                                                "metric_name": metric_name
                                                                            },
                                                                            model_params={
                                                                                "finetune_weights": finetune_weights,
                                                                                "need_merge_weights": need_merge_weights,
                                                                                "customized_model_package": customized_model_package,
                                                                            }
                                                                            )
        pipeline_instance.run_step_by_processes()

    def lab_completion_post_processing(output_directory_path):
        parser = Completion_Parser()
        parser.main(output_directory_path)
        return

    def lab_json_topo_post_processing(output_directory_path):
        parser = JSON_Topo_Parser()
        parser.main(output_directory_path)
        return 
    
    def lab_safety_post_processing(output_directory_path):
        # to do
        pass
    
    
    def lab_scoring(output_directory_path):
        pass

    # if subject == 'completion':
    #     lab_completion_post_processing(output_directory_path=output_directory_path)
    # elif subject == 'json_topo':
    #     lab_json_topo_post_processing(output_directory_path=output_directory_path)
    # elif subject == 'operation_safety':
    #     lab_safety_post_processing(output_directory_path=output_directory_path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('model_name_or_path')
    parser.add_argument('subject')
    # Need to specify a model category in the `ModelType` enum. e.g.: llama、falcon...
    parser.add_argument('model_type')
    parser.add_argument('--version', default=Conf.DEFAULT_VERSION)
    parser.add_argument('--data_dir', default=None)
    parser.add_argument('--output_dir', default='lab_output')
    parser.add_argument('--cot', action=argparse.BooleanOptionalAction)
    parser.add_argument('--rag', action=argparse.BooleanOptionalAction)
    parser.add_argument('--dry_run', action=argparse.BooleanOptionalAction)
    parser.add_argument('--pipeline_id', default=None)
    # parser.add_argument('--batch_size', type=int)
    # parser.add_argument('--device')
    # parser.add_argument('--device_map')
    # parser.add_argument('--max_new_tokens', type=int, default=10)
    parser.add_argument("--finetune_weights", default=None)
    parser.add_argument("--need_merge_weights", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('--language_type', choices=[v.value for v in LanguageType], default=LanguageType.EN.value)
    parser.add_argument("--question_type", choices=[v.value for v in QuestionType],
                        default=QuestionType.MULTIPLE_CHOICE.value)
    parser.add_argument("--metric_name", choices=[v.value for v in MetricName], help='the metric name')
    parser.add_argument("--breakpoint_file", default=None, help='the breakpoint file path')
    parser.add_argument("--customized_model_package", default='', help="the customized model package path")

    args = parser.parse_args()
    model_name_or_path = args.model_name_or_path
    subject = args.subject
    version = args.version
    model_type = detect_model_type(args.model_type)
    data_dir = args.data_dir
    output_dir = args.output_dir
    dry_run = args.dry_run or False
    pipeline_id = args.pipeline_id if args.pipeline_id else str(CommonHelper.generate_uuid())
    cot = args.cot or False
    rag = args.rag or False
    finetune_weights = args.finetune_weights
    need_merge_weights = args.need_merge_weights
    language_type = get_enum_item_by_value(LanguageType, args.language_type)
    question_type = get_enum_item_by_value(QuestionType, args.question_type)
    metric_name = get_enum_item_by_value(MetricName, args.metric_name)
    breakpoint_file = args.breakpoint_file
    customized_model_package = args.customized_model_package

    assert '..' not in model_name_or_path

    run(model_name_or_path, model_type, version, subject, data_dir, output_dir,
        **{"dry_run": dry_run, "pipeline_id": pipeline_id,
           "cot": cot,
           "rag": rag,
           "finetune_weights": finetune_weights,
           "need_merge_weights": need_merge_weights,
           "language_type": language_type,
           "question_type": question_type,
           "metric_name": metric_name,
           "breakpoint_file": breakpoint_file,
           "customized_model_package": customized_model_package})


if __name__ == "__main__":
    import time

    begin_time = time.time()
    main()
    end_time = time.time()
    time_cost = int(end_time - begin_time)
