init python:
    import time

    def format_time(seconds):
        """将秒数转换为时:分:秒格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

# 定义角色
define e = Character("艾琳")

# 定义持久化变量（在存档间保持）
default persistent.self_progress = 0
default persistent.opponent_progress = 0
default persistent.self_speed = 1.0
default persistent.opponent_speed = 1.0

# 定义普通变量（每次重新开始都会重置）
default focus_time = 0
default persistent.focus_level = 0  # 0: 未专注, 1: 初级专注, 2: 中级专注
default game_start_time = 0
default last_exit_time = 0
default last_progress_time = 0
default away = False
default away_start_time = 0

# 在文件开头添加变量定义
default persistent.final_result = ""  # 用于存储最终结果
default remaining_opponent = 0

# 游戏开始
label start:
    scene bg room
    with fade

    menu:
        "请选择模式"

        "长专注":
            $ game_start_time = time.time()
            $ persistent.self_progress = 0
            $ persistent.opponent_progress = 0
            $ persistent.self_speed = 1.0
            $ persistent.opponent_speed = 1.0
            jump long_focus

        "冥想":
            jump meditation

        "ADHD":
            jump adhd

# 长专注模式
label long_focus:
    scene bg room
    with dissolve

    # 初始化变量（只在新游戏初始化）
    if not renpy.get_game_runtime():  # 如果是新游戏
        $ persistent.self_progress = 0
        $ persistent.opponent_progress = 0
        $ persistent.self_speed = 1.0
        $ persistent.opponent_speed = 1.0

    # 每次进入都需要重置的变量
    $ focus_time = time.time()
    $ last_exit_time = 0
    $ last_progress_time = time.time()
    $ away = False
    $ away_start_time = 0
    $ persistent.focus_level = 0

    show screen focus_progress
    show screen time_display
    show screen away_button
    show screen game_loop_timer
    show screen temp_pause_button

    # 游戏主循环，等待游戏结束
    while True:
        $ renpy.pause(1)  # 暂停1秒
        $ current_time = time.time()
        if not game_paused:  # 只在非暂停状态下更新进度
            $ elapsed_progress_time = current_time - last_progress_time
            if elapsed_progress_time >= 1:
                if not sneaking_away: # 使用 sneaking_away 来控制己方进度
                    $ last_progress_time = current_time
                    $ persistent.self_progress += 0.03 * persistent.self_speed
                # 对手进度始终更新
                $ persistent.opponent_progress += 0.03 * persistent.opponent_speed

                # 检查里程碑
                $ check_progress_milestone()

                # 计算对手到达终点需要的时间
                $ remaining_opponent = (100 - persistent.opponent_progress) / (0.03 * persistent.opponent_speed)

                # 检查游戏是否结束
                if persistent.self_progress >= 100 or persistent.opponent_progress >= 100:
                    if persistent.self_progress > persistent.opponent_progress:
                        $ renpy.hide_screen("focus_progress")
                        $ renpy.hide_screen("time_display")
                        $ renpy.hide_screen("game_loop_timer")
                        $ renpy.hide_screen("temp_pause_button")
                        jump focus_reward
                    elif abs(persistent.self_progress - persistent.opponent_progress) < 0.1:
                        $ renpy.hide_screen("focus_progress")
                        $ renpy.hide_screen("time_display")
                        $ renpy.hide_screen("game_loop_timer")
                        $ renpy.hide_screen("temp_pause_button")
                        jump start
                    else:
                        $ self_final = persistent.self_progress + (0.03 * persistent.self_speed * remaining_opponent)
                        $ persistent.final_result = "根据当前速度预测:\n对手将在{:.1f}秒后达到100%\n你将达到{:.1f}%\n继续加油！".format(
                            remaining_opponent, self_final)
                        $ renpy.hide_screen("focus_progress")
                        $ renpy.hide_screen("time_display")
                        $ renpy.hide_screen("game_loop_timer")
                        $ renpy.hide_screen("temp_pause_button")
                        jump meditation_guide

# 游戏循环计时器
screen game_loop_timer:
    timer 10 repeat True action Function(update_game_state)

init python:
    def update_game_state():
        global focus_time, last_progress_time, away

        current_time = time.time()

        if not sneaking_away:  # 只在非暂离和非单方离场状态下检查专注时间
            # 检查连续专注时间
            continuous_focus_time = current_time - focus_time
            if persistent.focus_level == 0 and continuous_focus_time >= 29:
                persistent.focus_level = 1
                persistent.self_speed += 0.01
                focus_time = current_time
                renpy.show_screen("status_message", message="进入初级专注状态！")
            elif persistent.focus_level == 1 and continuous_focus_time >= 29:
                persistent.focus_level = 1.2
                persistent.self_speed += 0.02
                focus_time = current_time
            elif persistent.focus_level == 1.2 and continuous_focus_time >= 29:
                persistent.focus_level = 1.4
                persistent.self_speed += 0.03
                focus_time = current_time
                renpy.show_screen("status_message", message="进入中级专注状态！")
            elif persistent.focus_level == 1.4 and continuous_focus_time >= 29:
                persistent.focus_level = 1.6
                persistent.self_speed += 0.04
                focus_time = current_time
            elif persistent.focus_level == 1.6 and continuous_focus_time >= 29:
                persistent.focus_level = 1.8
                persistent.self_speed += 0.05
                focus_time = current_time
            elif persistent.focus_level == 1.8 and continuous_focus_time >= 29:
                persistent.focus_level = 2
                persistent.self_speed += 0.06
                focus_time = current_time
            elif persistent.focus_level == 2 and continuous_focus_time >= 298:
                persistent.self_speed += 0.08
                focus_time = current_time

            # 每次更新进度时存游戏状态
            renpy.save_persistent()

# 状态消息显示屏幕
screen status_message(message):
    timer 1.0 action Hide("status_message")
    frame:
        xalign 0.5
        yalign 0.5
        text message

# 冥想模式
label meditation:
    scene bg meditation
    $ meditation = MeditationState()  # 创建新的冥想态
    show screen meditation_screen
    window hide  # 隐藏对话窗口
    $ renpy.pause(hard=True)  # 使用 hard=True 来禁止点击触发

# 添加冥想奖励页面
label meditation_reward:
    scene bg room
    "恭喜完成冥想"
    jump start

# 在文件末尾添加标签
label show_win_result:
    "[persistent.final_result]"  # 显示计算结果
    jump focus_reward
# 在文件末尾添加标签
label show_tie_result:
    "[persistent.final_result]"  # 显示计算结果
    jump start
label show_fail_result:
    "[persistent.final_result]"  # 显示计算结果
    jump meditation_guide

# 在 script.rpy 中添加引导标签
label meditation_guide:
    scene bg room
    "看来你在专注挑战中遇到了困难..."
    "要不要尝试通过冥想来提升你的专注力呢？"
    menu:
        "好的，想尝试冥想":
            jump meditation
        "不了，我想回到主页":
            jump start

label focus_reward:
    "奖励界面暂未建设完成"
    return

init python:
    def check_progress_milestone():
        # 检查进度差距
        progress_diff = persistent.opponent_progress - persistent.self_progress
        if progress_diff >= 3:
            renpy.show_screen("status_message", message="此时不搏何时搏")
        elif progress_diff >= 2:
            renpy.show_screen("status_message", message="要加把劲了")

        # 检查进度里程碑
        current_progress = int(persistent.self_progress)  # 取整数部分

        # 定义里程碑消息
        milestones = {
            90: "行百里路半九十，胜利就在前方",
            80: "慎终如始，则无败事",
            70: "即今江海一归客，他日云霄万里人",
            60: "行到水穷处，坐看云起时",
            50: "江山方进半程前，正值群游剪水仙",
            40: "粗缯大布裹生涯，腹有诗书气自华",
            30: "加油！轻舟已过万重山",
            20: "明年此日青云去，却笑人间举子忙",
            10: "时人不识凌云木，直待凌云始道高"
        }

        # 确保 last_milestone 存在且有初始值
        if not hasattr(persistent, 'last_milestone'):
            persistent.last_milestone = 0
        elif persistent.last_milestone is None:
            persistent.last_milestone = 0

        # 检查是否达到新的里程碑
        for threshold in sorted(milestones.keys(), reverse=True):  # 从高到低检查
            if current_progress >= threshold and threshold > persistent.last_milestone:
                persistent.last_milestone = threshold
                renpy.show_screen("status_message", message=milestones[threshold])
                break

# ADHD 模式
label adhd:
    scene bg room

    # 初始化变量
    $ current_task = None
    $ current_ad = None
    $ ad_type = None
    $ task_completed = False

    show screen adhd_interface
    show screen adhd_settings_button

    # 等待用户操作
    $ renpy.pause(hard=True)

# ADHD 写作页面
label adhd_writing:
    $ adhd_state = ADHDState("writing")
    show screen adhd_writing_screen
    while True:
        $ renpy.pause(hard=True)

# ADHD 锻炼页面
label adhd_exercise:
    $ adhd_state = ADHDState("exercise")
    show screen adhd_writing_screen
    while True:
        $ renpy.pause(hard=True)

# ADHD 表情管理页面
label adhd_expression:
    $ adhd_state = ADHDState("expression")
    show screen adhd_writing_screen
    while True:
        $ renpy.pause(hard=True)
