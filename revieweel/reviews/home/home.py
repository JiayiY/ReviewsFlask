import eel
import os
import subprocess

eel.init('web')                     # 初始化包含web文件的文件夹
@eel.expose                         # 向js暴露函数
def show_Emotion():
    subprocess.check_call('python lstm_test.py', shell=True, cwd='E:\\reviewanalysisgra\\revieweel\\reviews\\lstm')
    subprocess.check_call('snapshot pieEmotion.html', shell=True,
                          cwd='E:\\reviewanalysisgra\\revieweel\\reviews\\home\\web')
    subprocess.check_call('rename output.png pieEmotion.png', shell=True,
                          cwd='E:\\reviewanalysisgra\\revieweel\\reviews\\home\\web')

@eel.expose                         # 向js暴露函数
def show_StarLine():
    subprocess.check_call('python visual.py', shell=True, cwd='E:\\reviewanalysisgra\\revieweel\\reviews')
    subprocess.check_call('snapshot lineStar.html', shell=True,
                          cwd='E:\\reviewanalysisgra\\revieweel\\reviews\\home\\web')
    subprocess.check_call('rename output.png lineStar.png', shell=True,
                          cwd='E:\\reviewanalysisgra\\revieweel\\reviews\\home\\web')

eel.start('main.html')             # Start (this blocks and enters loop)