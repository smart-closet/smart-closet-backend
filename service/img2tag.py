from service.cnn_embedding import CNN_EMBEDDING  # img2vec
import numpy as np  # img2vec, vec2score, score2tag
import joblib  # vec2score

def img2vec(imgs):
    cnn = CNN_EMBEDDING('resnet50', weights='IMAGENET1K_V2')

    vecs = []
    for img in imgs:
        combined_embedding = cnn.embed_images(img[0], img[1])
        combined_embedding = np.array(combined_embedding)
        vecs.append(combined_embedding)
        
    return vecs


def vec2score(vecs):
    
    a_model = joblib.load('api/models/a_svmodel_compressed.pkl')
    j_model = joblib.load('api/models/j_svmodel_compressed.pkl')
    k_model = joblib.load('api/models/k_svmodel_compressed.pkl')
    t_model = joblib.load('api/models/t_svmodel_compressed.pkl')

    a_scores = a_model.predict(vecs)
    j_scores = j_model.predict(vecs)
    k_scores = k_model.predict(vecs)
    t_scores = t_model.predict(vecs)
    
    all_scores = np.vstack([a_scores, j_scores, k_scores, t_scores]).T
    
    return all_scores


def score2tag(all_scores):
    # 抓出各個 outfits 最高分的 index
    max_indices = np.argmax(all_scores, axis=1)

    # index - tag
    idx_tag = np.array(["美", "日", "韓", "臺"])
    tags = idx_tag[max_indices]
    
    return tags