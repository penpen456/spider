import os

os.mkdir('./test')
# open函数不会自动创建目录
with open('./test/1.txt', 'w') as f:
    f.write('123')
