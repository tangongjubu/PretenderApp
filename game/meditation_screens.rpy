init python:
    import time
    from collections import deque
    
    class MeditationState:
        def __init__(self):
            self.start_time = time.time()
            self.is_active = True
            self.duration = 5 * 60  # 5分钟
            self.is_paused = False
            self.speed = 1.0
            self.current_pos = [0.0, 0.7]  # 当前位置 [x, y]
            self.trail_positions = deque(maxlen=200)
            self.rotation = 0
            self.last_update = time.time()  # 上次更新时间
            self.music_on = False  # 音乐状态
            self.pause_start = 0  # 记录暂停开始时间
            self.total_pause_time = 0  # 记录总暂停时间
            
        def toggle_speed(self):
            """循环切换速度"""
            if self.speed == 1.0:
                self.speed = 1.5
            elif self.speed == 1.5:
                self.speed = 2.0
            else:
                self.speed = 1.0
                
        def update_position(self):
            """更新小球位置"""
            if self.is_paused:
                self.last_update = time.time()
                return
                
            current_time = time.time()
            dt = current_time - self.last_update  # 计算时间差
            self.last_update = current_time
            
            # 更新位置
            x, y = self.current_pos
            x += 0.05 * self.speed * dt  # 使用时间差来计算位置增量
            
            # 根据x位置计算y位置
            if x <= 0.33:
                # 向右上
                progress = x / 0.33
                y = 0.7 - (0.4 * progress)
            elif x <= 0.66:
                # 向右
                y = 0.3
            elif x <= 1.0:
                # 向右下
                progress = (x - 0.66) / 0.34
                y = 0.3 + (0.4 * progress)
            else:
                # 重置位置
                x = 0.0
                y = 0.7
                
            self.current_pos = [x, y]
            self.trail_positions.append([x, y])
            
            # 更新旋转角度
            self.rotation = (self.rotation + 180 * self.speed * dt) % 360  # 使用时间差来计算旋转角度
            
        def get_meditation_time(self):
            """获取冥想时间"""
            if self.is_paused:
                return int(self.pause_start - self.start_time - self.total_pause_time)
            return int(time.time() - self.start_time - self.total_pause_time)
            
        def toggle_music(self):
            """切换音乐状态"""
            self.music_on = not self.music_on
            if self.music_on:
                renpy.music.play("audio/Keepsmiling.mp3", channel="music", loop=True)
            else:
                renpy.music.stop(channel="music")

# 定义小球的基本显示（不包含旋转）
transform ball_base(x, y, rot):
    xalign x yalign y
    rotate rot

# 定义轨迹点的显示
transform trail_dot(x, y, alpha):
    xalign x yalign y
    alpha alpha

# 定义速度按钮的样式
style speed_button_text:
    size 32
    color "#000000"
    hover_color "#4CAF50"
    outlines [(2, "#ffffff", 0, 0)]

style speed_button:
    background Frame("gui/button/choice_idle_background.png", Borders(5, 5, 5, 5))
    hover_background Frame("gui/button/choice_hover_background.png", Borders(5, 5, 5, 5))
    xpadding 30
    ypadding 15
    
screen meditation_screen():
    # 更新小球位置
    timer 0.016 repeat True action Function(meditation.update_position)
    
    # 添加背景
    add "bg meditation"
    
    # 显示时间
    frame:
        xalign 0.05 yalign 0.05
        padding (20, 10)
        text "冥想时间: [format_time(meditation.get_meditation_time())]"
    
    # 绘制轨迹
    for i, pos in enumerate(meditation.trail_positions):
        $ alpha = float(i) / len(meditation.trail_positions) * 0.3  # 透明度从0到0.3
        add "meditation_ball":
            at trail_dot(pos[0], pos[1], alpha)
    
    # 绘制主小球
    add "meditation_ball" at ball_base(meditation.current_pos[0], meditation.current_pos[1], meditation.rotation)
    
    # 速度控制按钮（居中）
    frame:
        xalign 0.5 yalign 0.95
        padding (20, 10)
        background None
        vbox:
            spacing 5
            text "速度" xalign 0.5 size 24 color "#000000"
            textbutton "[meditation.speed]x" action Function(meditation.toggle_speed) style "speed_button"
    
    # 控制按钮（右侧）
    frame:
        xalign 0.95 yalign 0.8  # 调整位置，避免与结束按钮重叠
        padding (20, 10)
        vbox:
            spacing 10
            if meditation.is_paused:
                textbutton "继续冥想" action [
                    SetField(meditation, "is_paused", False),
                    SetField(meditation, "total_pause_time", meditation.total_pause_time + (time.time() - meditation.pause_start))
                ]
            else:
                textbutton "暂停冥想" action [
                    SetField(meditation, "is_paused", True),
                    SetField(meditation, "pause_start", time.time())
                ]
    
    # 音乐控制按钮
    frame:
        xalign 0.95 yalign 0.05
        padding (10, 10)
        background None
        imagebutton:
            idle ("note_on" if meditation.music_on else "note_off")
            action Function(meditation.toggle_music)
            at transform:
                zoom 0.5
    
    # 结束冥想按钮
    frame:
        xalign 0.95 yalign 0.95
        padding (20, 10)
        textbutton "结束冥想" action [
            Hide("meditation_screen"),
            Jump("meditation_reward")
        ] 