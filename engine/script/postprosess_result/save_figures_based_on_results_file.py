import math
from collections import defaultdict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


model_6_7b_list = [
    'tiiuae-falcon-7b',
    'tiiuae-falcon-7b-instruct',
    'huggyllama-llama-7b',
    'meta-llama-Llama-2-7b-chat-hf',
    'meta-llama-Llama-2-7b-hf',
    'thudm-chatglm2-6b',
    'thudm-chatglm-6b',
]

model_13b_list = [
    'baichuan-inc-baichuan-13b-base',
    'baichuan-inc-baichuan-13b-chat',
    'huggyllama-llama-13b',
    'meta-llama-llama-2-13b-chat-hf',
    'meta-llama-llama-2-13b-hf'
]

model_30_70b_list = [
    'huggyllama-llama-30b',
    'huggyllama-llama-65b',
    'meta-llama-llama-2-70b-chat-hf',
    'meta-llama-llama-2-70b-hf',
    'mistralai-mixtral-8x7b-instruct-v0.1',
    'mistralai-mixtral-8x7b-v0.1',
    'tiiuae-falcon-40b',
    'tiiuae-falcon-40b-instruct',
]


model_gpt_4_list = [
    'gpt-4'
]

model_to_draw_list = {
    '6-7B': model_6_7b_list,
    '13B': model_13b_list,
    '30-70B': model_30_70b_list,
    'GPT-4': model_gpt_4_list,
}


def nested_dict():
    """
    recursive dict
    """
    return defaultdict(nested_dict)


def draw_and_save_figure(file_path, shot_type_to_draw, subject_to_draw, labels, result_path):
    logits_result_data_df = pd.read_excel(file_path, sheet_name='Sheet3')

    mcq_shot_type_data = nested_dict()

    for index, row in logits_result_data_df.iterrows():
        subject = row['Subject']
        shot_type = row['Shot Type']
        model = row['Model']
        label = row['Label']
        accuracy = row['Accuracy or Score']
        if subject == subject_to_draw and shot_type == shot_type_to_draw:
            mcq_shot_type_data[model][label] = accuracy

    # draw figure
    plt.rcParams['font.sans-serif'] = 'Microsoft YaHei'
    plt.rcParams['font.size'] = '25'
    plt.rcParams['axes.unicode_minus'] = False

    N = len(labels)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False)

    angles = np.concatenate((angles, [angles[0]]))
    labels = np.concatenate((labels, [labels[0]]))

    fig = plt.figure(figsize=(15, 6))
    ax = fig.add_subplot(111, polar=True)

    for name, model_to_draw in model_to_draw_list.items():
        values_min = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        values_max = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for model, value in mcq_shot_type_data.items():
            if model_to_draw and model not in model_to_draw:
                continue
            value_keys = value.keys()
            value_keys = [int(i) for i in value_keys if not math.isnan(i)]
            for i in range(10):
                if i not in value_keys:
                    value[i] = 0
            index = 0
            for k in sorted(value):
                if math.isnan(k):
                    continue
                if value[k] > values_max[index]:
                    values_max[index] = value[k]
                if value[k] < values_min[index] or values_min[index] == 0:
                    values_min[index] = value[k]
                index += 1

        values_min = np.concatenate((values_min, [values_min[0]]))
        values_max = np.concatenate((values_max, [values_max[0]]))
        if name == 'GPT-4':
            if values_max[0] != 0:
                ax.plot(angles, values_max, 'o-', lw=1, label=name)
        else:
            ax.fill_between(angles, values_min, values_max, alpha=0.25, label=name)

    # Add labels for each feature
    ax.set_thetagrids(angles * 180/np.pi, labels)
    ax.set_theta_zero_location('N')
    ax.set_rlim(0, 100)
    ax.set_rlabel_position(0)
    # Set the range
    ax.set_ylim(0, 1)
    plt.yticks(size=25 * 0.7)
    ax.grid(True, color='grey')

    # Adjust label position
    rstep = int(ax.get_theta_direction())
    if rstep > 0:
        rmin = 0
        rmax = len(angles)
    else:
        rmin = len(angles) - 1
        rmax = -1

    for label, i in zip(ax.get_xticklabels(), range(rmin, rmax, rstep)):
        angle_rad = angles[i] + ax.get_theta_offset()
        if angle_rad < 2:
            ha = 'center'
            va = "bottom"
        elif 4.5 < angle_rad < 5:
            ha = 'center'
            va = "top"
        elif angle_rad <= np.pi / 2:
            ha = 'left'
            va = "bottom"
        elif np.pi / 2 < angle_rad <= np.pi:
            ha = 'right'
            va = "bottom"
        elif np.pi < angle_rad <= (3 * np.pi / 2):
            ha = 'right'
            va = "top"
        else:
            ha = 'left'
            va = "top"
        label.set_verticalalignment(va)
        label.set_horizontalalignment(ha)
        if angle_rad < 2:
            label.set_y(-0.05)

    # Set legend position
    plt.legend(loc=(1.5, -0.13))
    # save and show figure
    plt.savefig(result_path)
    plt.show()


if __name__ == '__main__':
    labels = ['IP Networking', 'Transport Protocols', 'Network\nManagement', 'Internetworking', 'Data &\nApplications',
              'Link Layer', 'Network Security', 'Network\nOptimization', 'Enterprise\nNetworking',
              '    Design &\n    Architecture']
    logits_result_file_path = '/home/xxx/logits_match/mcq-zero-shot_five-shot-MetricName.Exact_results.xlsx'
    logits_rag_result_file_path = '/home/xxx/rag/logits_match/mcq-zero-shot_five-shot-MetricName.Exact_results.xlsx'
    logits_rag_new_result_file_path = '/home/xxx/rag_new/logits_match/mcq-zero-shot_five-shot-MetricName.Exact_results.xlsx'

    draw_and_save_figure(logits_result_file_path, 'zero-shot', 'mcq', labels, 'mcq_zero_shot.pdf')
    draw_and_save_figure(logits_result_file_path, 'five-shot', 'mcq', labels, 'mcq_five_shot.pdf')
    draw_and_save_figure(logits_rag_result_file_path, 'zero-shot', 'mcq', labels, 'mcq_rag_zero_shot.pdf')
    draw_and_save_figure(logits_rag_new_result_file_path, 'zero-shot', 'mcq', labels, 'mcq_rag_new_zero_shot.pdf')
