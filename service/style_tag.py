from img2tag import img2vec, vec2score, score2tag

# input imgs_urls: 2D string list, shape=(n, 2)
# output tags: ndarray, shape=(n, 1)

# example input
imgs = [['https://cdn.beams.co.jp/img/goods/11130702146/O/11130702146_C_2.jpg', 'https://images.plurk.com/7k5nTmlsq7eH9jjlqtZ9sN.jpg'], 
        ['https://images.plurk.com/1uLN9b2CWL6F3kXpEHA9c8.jpg', 'https://images.plurk.com/2zklWbyckuRpOzdkHYukcP.jpg'],
        ['https://images.plurk.com/1UJMavsDbuwevBAA0yShWl.jpg', 'https://images.plurk.com/1S4ypjZwxBOlx4dxnREbCA.jpg']]

vecs = img2vec(imgs)
scores = vec2score(vecs)
tags = score2tag(scores)

#print("scores:\n", scores)
#print("tags:", tags)