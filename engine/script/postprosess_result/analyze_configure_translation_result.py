# -*- coding: utf-8 -*-

import json
import numpy as np

start_special_token = ["```", "< Huawei >", "'''", "####", " (please fill in the blanks)"]
end_special_token = ["```", "Note: ", "'''", "####", "\n\n\n"]


def decompose_lines(cfg, exist_special_token=False):
    lines = []
    for line in cfg.splitlines():
        if exist_special_token:
            if line in start_special_token:
                continue
            if line in end_special_token:
                break
            lines.append(line.strip())
        else:
            lines.append(line.strip())

    lines = [line for line in lines if line and line[0] != '#' and line[0] != '!']
    return lines


def decompose_blocks(cfg, exist_special_token=False):
    lines = [line for line in cfg.splitlines()]
    blocks = []
    block = []

    for line in lines:
        if exist_special_token:
            if line in start_special_token:
                continue
            if line in end_special_token:
                break
            if line.startswith(' '):
                block.append(line)
            else:
                if len(block) > 0:
                    blocks.append('\n'.join(block))
                    block = [line]
                else:
                    block.append(line)
        else:
            if line.startswith(' '):
                block.append(line)
            else:
                if len(block) > 0:
                    blocks.append('\n'.join(block))
                    block = [line]
                else:
                    block.append(line)

    blocks = set(blocks)
    return blocks


def compute_score_line_level(cfg, cfg_ref):
    ref_lines = decompose_lines(cfg_ref)
    ref_lines_set = set(ref_lines)
    lines = decompose_lines(cfg)
    lines_set = set(lines)

    hit = 0
    for line in lines:
        if line in ref_lines_set:
            hit += 1
            # print(line)
    precision = hit / len(lines)

    hit = 0
    for line in ref_lines:
        if line in lines_set:
            hit += 1
    try:
        recall = hit / len(ref_lines)
    except:
        recall = 0
    if (precision + recall) == 0:
        f1_score = 0
    else:
        f1_score = 2 * precision * recall / (precision + recall)
    return precision, recall, f1_score


def compute_score_block_level(cfg, cfg_ref):
    ref_blocks = decompose_blocks(cfg_ref, False)
    ref_blocks_set = set(ref_blocks)
    blocks = decompose_blocks(cfg)
    blocks_set = set(blocks)

    hit = 0
    for block in blocks:
        if block in ref_blocks_set:
            hit += 1
            # print(block)
    precision = hit / len(blocks)

    hit = 0
    for block in ref_blocks:
        if block in blocks_set:
            hit += 1
    try:
        recall = hit / len(ref_blocks)
    except:
        recall = 0
    if (precision + recall) == 0:
        f1_score = 0
    else:
        f1_score = 2 * precision * recall / (precision + recall)
    return precision, recall, f1_score


def cal_trans_precision_recall(question_path, answer_path, compute_score_func):
    with open(question_path, "r") as question_file:
        question_data = json.load(question_file)
    with open(answer_path, "r") as answer_path:
        list_data = answer_path.readlines()
    dict_title_answer = {}
    for data in list_data:
        data_json = json.loads(data)
        dict_title_answer.update({data_json.get("title"): data_json.get("answer")})
    list_precision = []
    list_recall = []
    list_f1 = []
    for question in question_data:
        title = question.get("title")
        huawei = question.get("huawei")
        trans_answer = dict_title_answer.get(title)
        precision, recall, f1 = compute_score_func(huawei, trans_answer)
        list_precision.append(precision)
        list_recall.append(recall)
        list_f1.append(f1)
    return np.mean(list_precision), np.mean(list_recall), np.mean(list_f1)
