import json
import os
import re


def get_answer(answer, cot):
    r1 = r'(.)*Answer( )?: (([A-I](,)? )*(and )?([A-I])?)'
    r2 = r'(.)*Answer:The correct ((option)|(answers)) for this question would be ([A-I](,)? )*(and )?([A-I])?'
    r3 = r'(.)*The correct option here would be (([A-I])+)'
    r4 = r'(.)*答案：(([A-I])+)'
    r5 = r'(.)*The correct answers are (([A-I](,)? )*(and )?([A-I])?)'
    r6 = r'(\d)\.( |\n)*Answer( )*:(([A-I](,)? )*(and )?([A-I])+)'
    r7 = r'(\d)\.( |\n)*(([A-I](,)? )*(and )?([A-I])+)'
    r8 = r'\(([A-I])\)'
    r9 = r'\"([A-I])'
    r10 = r'(.)*The correct answer is( |: \n)([A-I])'
    r11 = r'(.)*The answer is( |: \n)([A-I])'
    r12 = r'(\n)*( )*([A-I])\.'
    r13 = r'The answer to the question is ([A-I])'
    r14 = r'([A-I])  '
    r15 = r'([A-I]) ---(-)*'
    r16 = r"answer is ([a-dA-D]+)"
    r17 = r'(.)*答案(是|为)?(选项)?(:| |：)?([A-I])'
    r18 = r'(.)*正确的选项是([A-I])'
    r19 = r'(.)*(选项)?([A-I])是(本题的)?正确答案'
    r20 = r'([A-I]):'
    r21 = r'\'([A-I])'
    r22 = r'([A-I]),'
    r23 = r'([A-I])</s>'
    r24 = r"answer to the question is ([a-dA-D]+)"
    r25 = r"answer is( |: \n)([a-dA-D]+)"
    r26 = r'(.)*Answer:The correct ((option)|(answers)) for this question would have been ([A-I](,)? )*(and )?([A-I])?'
    r27 = r'(.)*The correct option here would hive been (([A-I])+)'
    r28 = r'(.)*正确(答案|选项)?(是|为)?(:|：)?(\s)?(([A-I])+)'
    r29 = r'(.)*答(:|：)?(\s)?(选)?(\s)?(正确答案|【正确答案】)?(:|：)?(\s)?(([A-I])+)'

    re_list = [
        {'pattern': r1, 'group_num': 3},
        {'pattern': r2, 'group_num': 5},
        {'pattern': r3, 'group_num': 2},
        {'pattern': r4, 'group_num': 2},
        {'pattern': r5, 'group_num': 2},
        {'pattern': r6, 'group_num': 4},
        {'pattern': r7, 'group_num': 3},
        {'pattern': r8, 'group_num': 1},
        {'pattern': r9, 'group_num': 1},
        {'pattern': r10, 'group_num': 3},
        {'pattern': r11, 'group_num': 3},
        {'pattern': r12, 'group_num': 3},
        {'pattern': r13, 'group_num': 1},
        {'pattern': r14, 'group_num': 1},
        {'pattern': r15, 'group_num': 1},
        {'pattern': r17, 'group_num': 5},
        {'pattern': r18, 'group_num': 2},
        {'pattern': r19, 'group_num': 3},
        {'pattern': r20, 'group_num': 1},
        {'pattern': r21, 'group_num': 1},
        {'pattern': r22, 'group_num': 1},
        {'pattern': r23, 'group_num': 1},
        {'pattern': r28, 'group_num': 6},
        {'pattern': r29, 'group_num': 9},
    ]

    cot_re_list = [
        {'pattern': r16, 'group_num': 1},
        {'pattern': r24, 'group_num': 1},
        {'pattern': r25, 'group_num': 1},
        {'pattern': r10, 'group_num': 3},
        {'pattern': r11, 'group_num': 3},
        {'pattern': r12, 'group_num': 3},
        {'pattern': r13, 'group_num': 1},
        {'pattern': r1, 'group_num': 3},
        {'pattern': r2, 'group_num': 5},
        {'pattern': r3, 'group_num': 2},
        {'pattern': r26, 'group_num': 5},
        {'pattern': r27, 'group_num': 2},
        {'pattern': r4, 'group_num': 2},
        {'pattern': r5, 'group_num': 2},
        {'pattern': r6, 'group_num': 4},
        {'pattern': r7, 'group_num': 3},
        {'pattern': r8, 'group_num': 1},
        {'pattern': r9, 'group_num': 1},
        {'pattern': r14, 'group_num': 1},
        {'pattern': r15, 'group_num': 1},
        {'pattern': r17, 'group_num': 5},
        {'pattern': r18, 'group_num': 2},
        {'pattern': r19, 'group_num': 3},
    ]

    print("------------RAW------------")
    if cot:
        answer = re.sub('Question:(.*)', '',
                        answer, flags=re.IGNORECASE | re.DOTALL)
    print(answer)

    group_num = 0
    match = None
    rl = cot_re_list if cot else re_list
    for r in rl:
        matching = re.search if cot else re.match
        match = matching(r['pattern'], answer, re.S)
        if match:
            group_num = r['group_num']
            break
    if not match:
        return []

    ans_str = match.group(group_num)

    ans_str = ans_str.replace(', ', '')
    ans_str = ans_str.replace(' and ', '')
    ans_str = ans_str.replace(' & ', '')
    ans_str = ans_str.replace(' ', '')

    if len(ans_str) == 1:
        return [ans_str]
    else:
        return [k for k in ans_str]


def filter_question(question):
    if question.get('with_images', False):
        return False
    if isinstance(question.get("answer", {}), dict) and not isinstance(question.get("answer", {}).get("choice", ""), str):
        return False
    if isinstance(question.get("answer", {}), dict) and len(question.get("answer", {}).get("choice", "")) > 1:
        return False
    return True


def get_questions_from_exam_file_path(list_exam_file_path, breakpoint_file=None):
    continue_key = None
    if breakpoint_file and os.path.isfile(breakpoint_file):
        with open(breakpoint_file) as f:
            lines = f.readlines()
            last_line = lines[-1].replace('\n', '')
            last_question = json.loads(last_line)
            continue_key = f'{last_question["id"]}_{last_question["title"]}'

    find_breakpoint_flag = False
    list_questions = []
    for exam_path in list_exam_file_path:
        with open(exam_path, encoding='utf-8') as f_in:
            exam_data = json.load(f_in)
            exam_id = exam_data['id']
            questions = exam_data['questions']
            for q in filter(filter_question, questions):
                q['exam_id'] = exam_id
                if continue_key and not find_breakpoint_flag:
                    if f'{exam_id}_{q["title"]}' == continue_key:
                        find_breakpoint_flag = True
                    else:
                        continue
                else:
                    list_questions.append(q)
    return list_questions
