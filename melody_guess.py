#!/usr/bin/env python3

from music21 import stream, note, duration, tempo
import random
import sys
import subprocess
import tempfile
import time
from threading import Thread


def sleep_and_echo(sleep_time, str):
    time.sleep(sleep_time)
    print(str)
    

def play_midi(midi_file, padding_count, total_duration, bpm):
    # 每个四分音符的时值是 60s/bpm
    note_duration = 60 / bpm
    start_echo = Thread(target=sleep_and_echo, args=(padding_count * note_duration, "⭐ 开始了哦！", ))
    end_echo = Thread(target=sleep_and_echo, args=(total_duration * note_duration, "⭐ 结束了哦！", ))
    start_echo.start()
    end_echo.start()
    subprocess.run(
        ["timidity", midi_file],
        stdout=subprocess.DEVNULL,  # 丢弃标准输出
    )


def get_random_note_duration(note_duration, special_pattern_rate):
    special_pattern = (
        (0.5, 0.5) if 0.5 in note_duration else None,
        (0.25, 0.25, 0.25, 0.25) if 0.25 in note_duration else None,
        (0.25, 0.25, 0.25, 0.25) if 0.25 in note_duration else None,
    )
    special_pattern = tuple(x for x in special_pattern if x is not None)
    if special_pattern and random.random() < special_pattern_rate:
        return random.choice(special_pattern)
    else:
        return (random.choice(note_duration), )


def main(note_count, note_duration, special_pattern_rate, bpm):
    # 创建一个乐谱流
    melody_stream = stream.Stream()

    # 添加速度标记
    metronome = tempo.MetronomeMark(number=bpm)
    melody_stream.append(metronome)
    
    padding_count = 4
    print(f'首先播放{padding_count}个四分音符，接下来是随机的音符时值')
    # 添加四个4分音符
    for _ in range(padding_count):
        n = note.Note('C4')
        n.duration = duration.Duration(1.0)  # 4分音符
        melody_stream.append(n)

    i = 0
    while i < note_count:
        # 随机选择时值类型
        selected_durations = get_random_note_duration(note_duration, special_pattern_rate)
        while len(selected_durations) + i > note_count:
            selected_durations = get_random_note_duration(note_duration, special_pattern_rate)
        i += len(selected_durations)
        
        for d in selected_durations:
            n = note.Note('C4')
            n.duration = duration.Duration(d)

            # 将音符添加到流中
            melody_stream.append(n)

    # 创建随机名称midi文件
    midi_file = tempfile.mktemp(suffix='.mid', dir='.')
    melody_stream.write('midi', midi_file)

    play_midi(midi_file, padding_count, melody_stream.duration.quarterLength, bpm)

    # 等待用户输入他听到的时值
    user_input = input("请输入你听到的时值（以空格分隔），或输入`?`表示再听一遍，输入`x`表示放弃：")

    while user_input == '?':
        play_midi(midi_file, padding_count, melody_stream.duration.quarterLength, bpm)
        user_input = input("现在感觉怎么样：")
    
    if user_input == 'x':
        print('放弃了哦！')
    else:
        for guess, target in zip(user_input.split(' '), melody_stream.notes[padding_count:]):
            if target.duration.quarterLength == float(guess):
                print('hit GOOD trap #', target.duration.quarterLength)
            else:
                print('hit BAD trap  #', target.duration.quarterLength)

    again = input("再次播放乐谱？(y/n): ")
    if again.lower() == 'y':
        print('答案是：', end='')
        for target in melody_stream.notes[padding_count:]:
            print(target.duration.quarterLength, end=' ')
        print()
        sys.stdout.flush()

        play_midi(midi_file, padding_count, melody_stream.duration.quarterLength, bpm)

    # 删除临时文件
    subprocess.run(['rm', midi_file])
    print('删除临时文件:', midi_file)

    
if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: music.py <note_count> <note_duration> <special_pattern_rate> <bpm>")
        print("Example: python music.py 10 0.5,1.0,2.0 0.3 60")
        sys.exit(1)

    try:
        # argv[1] 是音符数量
        note_count = int(sys.argv[1]) 
        # argv[2] 是一个以逗号分割的时值列表
        note_duration = list(map(float, sys.argv[2].split(',')))
        # argv[3] 是special pattern的概率
        special_pattern_rate = float(sys.argv[3])
        # argv[4] 是BPM
        bpm = int(sys.argv[4])
    except ValueError:
        print("参数错误，请检查输入格式")
        sys.exit(1)

    print('音符数量:', note_count)
    print('时值列表:', note_duration)
    print('SP概率:', special_pattern_rate)
    print('BPM:', bpm)

    # 运行主函数
    main(note_count, note_duration, special_pattern_rate, bpm)
