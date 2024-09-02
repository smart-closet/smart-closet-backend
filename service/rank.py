from service.rank_utils import generate_description_with_retry, generate_bert_embeddings, evaluate_model

def rank(top_list, bottom_list):
    try:
        results = []

        for top_item in top_list:
            for bottom_item in bottom_list:
                top_url = top_item['image_url']
                bottom_url = bottom_item['image_url']
                
                # 生成描述
                description = generate_description_with_retry(top_url, bottom_url)

                # 生成 BERT 嵌入
                descriptions = [description]
                embeddings = generate_bert_embeddings(descriptions)

                # 產生評分
                scores = evaluate_model('api/models/BERT_model_1.pt', embeddings)

                # 將結果加入結果列表
                result = {
                    'top': top_item,
                    'bottom': bottom_item,
                    'score': scores[0]
                }
                results.append(result)

        # 根據分數由大到小排序結果
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    except Exception as e:
        print("An error occurred:", str(e))
        return []