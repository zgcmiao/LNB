import argparse
import json
import os.path
import time

# import openai
from script import openai
import tqdm


def main(model_name, data_path, output_path, chat_mode, batch_size):
    if chat_mode and batch_size != 1:
        raise ValueError('`batch_size` must be 1 in chat mode')
    with open(data_path) as f_data:
        q_list = json.load(f_data)
    messages = [{
        "role": "system",
        "content": "You are an AI research assistant. You use a tone that is technical and scientific."
    }]
    id_titles = set()
    if os.path.exists(output_path):
        with open(output_path, 'r') as f:
            lines = [line.strip('\n') for line in f.readlines()]
        json_lines = [json.loads(line) for line in lines]
        id_titles = {(d['id'], d['title']) for d in json_lines}

    batches = []
    batch = []
    for q in q_list:
        if (q['id'], q['title']) in id_titles:
            continue
        batch.append(q)
        if len(batch) >= batch_size:
            batches.append(batch)
            batch = []

    for batch in tqdm.tqdm(batches):
        while True:
            try:
                if chat_mode:
                    cur_messages = messages + [{"role": "user", "content": batch[0]['prompt']}]
                    response = openai.ChatCompletion.create(
                        model=model_name,
                        messages=cur_messages,
                    )
                else:
                    response = openai.Completion.create(
                        model=model_name,
                        prompt=[q['prompt'] for q in batch]
                    )
                break
            except Exception as e:
                print(e)
                time.sleep(5)

        assert len(response['choices']) == len(batch), 'size of choices mismatch with prompt batch'
        with open(output_path, 'a') as fo:
            for q, a in zip(batch, response['choices']):
                res_dict = {}
                res_dict['id'] = q['id']
                res_dict['title'] = q['title']
                if chat_mode:
                    res_dict['answer'] = a['message']['content']
                else:
                    res_dict['answer'] = a['text']
                fo.write(json.dumps(res_dict, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data_path')
    parser.add_argument('output_path')
    parser.add_argument('api_key')
    parser.add_argument('--model_name', default='gpt-3.5-turbo')
    parser.add_argument('--chat_mode', action='store_true')
    parser.add_argument('--batch_size', type=int, default=1)
    args = parser.parse_args()

    openai.api_key = args.api_key
    main(model_name=args.model_name, data_path=args.data_path, output_path=args.output_path, chat_mode=args.chat_mode,
         batch_size=args.batch_size)
