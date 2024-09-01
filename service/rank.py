# import os
import random
# from service.rank_utils import generate_description_with_retry, generate_bert_embeddings
from dotenv import load_dotenv

def rank(top_list, bottom_list):
    try:
        results = []

        # 載入 API key
        load_dotenv()
        # api_key = os.getenv("API_KEY")

        for top_item in top_list:
            for bottom_item in bottom_list:
                top_name = top_item['name']
                bottom_name = bottom_item['name']
                # top_url = top_item['image_url']
                # bottom_url = bottom_item['image_url']
                
                # 生成描述
                # description = generate_description_with_retry(top_url, bottom_url, api_key)
                # print(f"Generated Description for {top_name} and {bottom_name}: {description}")

                # 生成 BERT 嵌入
                # descriptions = [description]
                # embeddings = generate_bert_embeddings(descriptions)

                # 產生評分
                # scores = evaluate_model('api/models/BERT_model_1.pt', embeddings)

                # 將結果加入結果列表
                result = {
                    'topID': top_name,
                    'bottomID': bottom_name,
                    'score': random.random()
                }
                results.append(result)

        # 根據分數由大到小排序結果
        results.sort(key=lambda x: x['score'], reverse=True)

        print("Final Results (Ranked by Score):", results)
        return results

    except Exception as e:
        print("An error occurred:", str(e))
        return []