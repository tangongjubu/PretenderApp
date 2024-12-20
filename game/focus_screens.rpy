# 专注模式相关的所有屏幕和功能

init python:
    # 初始化变量
    game_paused = False
    pause_time = 0
    sneaking_away = False
    away_start_time = 0
    last_exit_time = 0
    continuous_leave_time = 0
    last_penalty_time = 0
    temp_pause = False



    def pause_game():
        """暂停游戏，记录暂停时间"""
        global pause_time
        pause_time = time.time()
        
    def resume_game():
        """继续游戏，调整所有时间相关变量"""
        global focus_time, last_progress_time, game_start_time, persistent, pause_time

        # 计算暂停的时长
        pause_duration = time.time() - pause_time

        # 调整所有时间点，加上暂停的时长
        last_progress_time += pause_duration
        game_start_time += pause_duration

        # 重置专注时间
        focus_time = time.time()

        # 重置专注状态
        persistent.focus_level = 0
        persistent.self_speed = 1.0

    def calculate_final_result():
        """计算最终结果"""
        # 计算到100%需要的时间
        remaining_self = (100 - persistent.self_progress) / (0.03 * persistent.self_speed)
        remaining_opponent = (100 - persistent.opponent_progress) / (0.03 * persistent.opponent_speed)

        # 计算最终进度并设置结果
        if abs(remaining_self - remaining_opponent) < 0.1:
            persistent.final_result = "根据当前速度预测:\n双方将在{:.1f}秒后同时到达终点\n这将是一场平局！".format(
                remaining_self)
            renpy.hide_screen("focus_progress")
            renpy.hide_screen("time_display")
            renpy.hide_screen("away_button")
            renpy.hide_screen("game_loop_timer")
            renpy.hide_screen("temp_pause_button")
            renpy.jump("show_tie_result")
        elif remaining_self < remaining_opponent:
            opponent_final = persistent.opponent_progress + (0.03 * persistent.opponent_speed * remaining_self)
            persistent.final_result = "根据当前速度预测:\n你将在{:.1f}秒后达到100%\n对手将达到{:.1f}%\n恭喜你获胜！".format(
                remaining_self, opponent_final)
            renpy.hide_screen("focus_progress")
            renpy.hide_screen("time_display")
            renpy.hide_screen("away_button")
            renpy.hide_screen("game_loop_timer")
            renpy.hide_screen("temp_pause_button")
            renpy.jump("show_win_result")
        else:
            self_final = persistent.self_progress + (0.03 * persistent.self_speed * remaining_opponent)
            persistent.final_result = "根据当前速度预测:\n对手将在{:.1f}秒后达到100%\n你将达到{:.1f}%\n继续加油！".format(
                remaining_opponent, self_final)
            renpy.hide_screen("focus_progress")
            renpy.hide_screen("time_display")
            renpy.hide_screen("away_button")
            renpy.hide_screen("game_loop_timer")
            renpy.hide_screen("temp_pause_button")
            renpy.jump("show_fail_result")

    def start_sneaking():
        """开始偷溜，暂停自己的计时器和进度"""
        global pause_time, sneaking_away, last_penalty_time
        pause_time = time.time()
        sneaking_away = True
        last_penalty_time = 0  # 重置惩罚时间计数器
        
    def stop_sneaking():
        """结束偷溜，继续计时"""
        global focus_time, last_progress_time, game_start_time, pause_time, sneaking_away, last_penalty_time
        
        # 计算暂停的时长
        pause_duration = time.time() - pause_time
        
        # 调整所有时间点，加上暂停的时长
        last_progress_time += pause_duration
        game_start_time += pause_duration
        
        # 重置专注时间
        focus_time = time.time()
        
        # 如果偷溜时间超过30秒，重置专注等级
        if pause_duration >= 30:
            persistent.focus_level = 0
            persistent.self_speed = 1.0
            
        # 取消偷溜状态
        sneaking_away = False
        last_penalty_time = 0  # 重置惩罚时间计数器

    def should_update_progress():
        """判断是否应该更新进度"""
        return not (game_paused or sneaking_away)

    def check_sneaking_penalty():
        """检查溜走时间并增加对手速度"""
        global pause_time, persistent, last_penalty_time
        
        if not sneaking_away:  # 如果不是溜走状态，不执行
            return
            
        away_duration = time.time() - pause_time
        
        # 检查是否达到新的时间阈值，只在首次达到时增加速度
        if away_duration >= 180 and last_penalty_time < 180:  # 3分钟
            persistent.opponent_speed += 0.10
            last_penalty_time = 180
        elif away_duration >= 120 and last_penalty_time < 120:  # 2分钟
            persistent.opponent_speed += 0.07
            last_penalty_time = 120
        elif away_duration >= 90 and last_penalty_time < 90:  # 90秒
            persistent.opponent_speed += 0.05
            last_penalty_time = 90
        elif away_duration >= 48 and last_penalty_time < 48:  # 48秒
            persistent.opponent_speed += 0.03
            last_penalty_time = 48
        elif away_duration >= 30 and last_penalty_time < 30:  # 30秒
            persistent.opponent_speed += 0.02
            last_penalty_time = 30
        elif away_duration >= 18 and last_penalty_time < 18:  # 18秒
            persistent.opponent_speed += 0.01
            last_penalty_time = 18

# 专注进度屏幕
screen focus_progress():
    frame:
        xalign 0.5
        yalign 0.3
        vbox:
            spacing 20
            text "你的进度: [persistent.self_progress:.1f]%" xalign 0.5
            bar value persistent.self_progress range 100 xsize 800
            text "速度倍率: [persistent.self_speed:.2f]x" xalign 0.5
            text "专注等级: [persistent.focus_level == 0 and '未专注' or (persistent.focus_level == 1 and '初级专注I' or persistent.focus_level == 1.2 and '初级专注II' or persistent.focus_level == 1.4 and '中级专注I' or persistent.focus_level == 1.6 and '中级专注II' or persistent.focus_level == 1.8 and '中级专注III' or persistent.focus_level == 2 and '高级专注')]" xalign 0.5

    frame:
        xalign 0.5
        yalign 0.7
        vbox:
            spacing 20
            text "对手进度: [persistent.opponent_progress:.1f]%" xalign 0.5
            bar value persistent.opponent_progress range 100 xsize 800
            text "速度倍率: [persistent.opponent_speed:.2f]x" xalign 0.5

# 时间显示屏幕
screen time_display():
    # 专注时长（左上角）- 只在非偷溜状态下显示
    if not sneaking_away:
        frame:
            xalign 0.0
            yalign 0.0
            xpadding 30
            ypadding 15
            if not game_paused:
                text "专注时间: [format_time(time.time() - focus_time)]" size 36
            else:
                text "专注时间: [format_time(pause_time - focus_time)]" size 36

    # 总时长（正中上方）- 始终显示
    frame:
        xalign 0.5
        yalign 0.0
        xpadding 30
        ypadding 15
        if not game_paused:
            text "总时间: [format_time(time.time() - game_start_time)]" size 36
        else:
            text "总时间: [format_time(pause_time - game_start_time)]" size 36

# 暂离/回归按钮屏幕
screen away_button():
    # 添加计时器来检查溜走时间
    if sneaking_away:
        timer 1.0 repeat True action Function(check_sneaking_penalty)
        
    frame:
        xalign 0.95
        yalign 0.5
        xpadding 20
        ypadding 10
        vbox:
            spacing 10
            # 添加偷偷溜走按钮
            if not sneaking_away and not game_paused:
                textbutton "偷偷溜走" action [
                    Function(start_sneaking)
                ]
            elif sneaking_away:
                vbox:
                    spacing 5
                    text "已溜走: [format_time(time.time() - pause_time)]" size 24
                    textbutton "悄悄回来" action [
                        Function(stop_sneaking)
                    ]
            
            # 竞赛暂停按钮
            if not game_paused and not sneaking_away:
                textbutton "竞赛暂停" action [
                    SetVariable("game_paused", True),
                    Function(pause_game)
                ]
            elif game_paused and not sneaking_away and not temp_pause:
                textbutton "竞赛继续" action [
                    SetVariable("game_paused", False),
                    Function(resume_game)
                ]
            elif game_paused and not sneaking_away and temp_pause:
                textbutton "竞赛继续" action NullAction() style "temp_pause_button_disabled"

            textbutton "提前结算" action Function(calculate_final_result)

# 临时停赛按钮屏幕
screen temp_pause_button():
    frame:
        xalign 1.0
        yalign 0.0
        xpadding 30
        ypadding 15
        
        # 竞赛暂停状态下按钮不可用
        if game_paused and not sneaking_away and not temp_pause:
            textbutton "暂时停赛" action NullAction() style "temp_pause_button_disabled"
        
        # 正常状态下的按钮
        else:
            if not temp_pause:
                textbutton "暂时停赛" action [
                    SetVariable("temp_pause", True),
                    If(sneaking_away, [
                        Function(stop_sneaking)  # 如果在溜走状态，先结束溜走
                    ]),
                    SetVariable("game_paused", True),
                    Function(pause_game)
                ] style "temp_pause_button"
            else:
                textbutton "返回继续" action [
                    SetVariable("temp_pause", False),
                    SetVariable("game_paused", False),
                    Function(resume_game)
                ] style "temp_pause_button"

style temp_pause_button:
    xpadding 30
    ypadding 15
    size 32
    background "#dddddd"
    hover_background "#bbbbbb"

style temp_pause_button_disabled:
    xpadding 30
    ypadding 15
    size 32
    background "#888888"
    hover_background "#888888"
    color "#666666"
