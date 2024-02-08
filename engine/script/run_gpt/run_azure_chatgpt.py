import argparse
import json
import os.path
import time
import tqdm
from openai.types.chat import ChatCompletion

from script.run_gpt.azure_openai_proxy import AzureOpenAIProxy


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

    client = azure_openai_client_proxy.get_client()
    for batch in tqdm.tqdm(batches):
        while True:
            try:
                cur_messages = messages + [{"role": "user", "content": batch[0]['prompt']}]
                response = client.chat.completions.create(
                    model=model_name,
                    messages=cur_messages,
                )
                break
            except Exception as e:
                print(e)
                time.sleep(5)

        assert isinstance(response, ChatCompletion)
        assert len(getattr(response, "choices")) == len(batch), 'size of choices mismatch with prompt batch'
        with open(output_path, 'a') as fo:
            for q, a in zip(batch, getattr(response, "choices")):
                res_dict = {}
                res_dict['id'] = q['id']
                res_dict['title'] = q['title']
                res_dict['answer'] = getattr(getattr(a, "message"), "content")
                fo.write(json.dumps(res_dict, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data_path')
    parser.add_argument('output_path')
    parser.add_argument('api_key')
    parser.add_argument('--model_name', default='gpt35-turbo-1106-sdp-0np4wbKT')
    parser.add_argument('--chat_mode', action='store_true')
    parser.add_argument('--batch_size', type=int, default=1)
    parser.add_argument('--api_endpoint')

    args = parser.parse_args()
    azure_openai_client_proxy = AzureOpenAIProxy(args.api_endpoint)
    azure_openai_client_proxy.azure_api_key = args.api_key
    main(model_name=args.model_name, data_path=args.data_path, output_path=args.output_path, chat_mode=args.chat_mode,
         batch_size=args.batch_size)
