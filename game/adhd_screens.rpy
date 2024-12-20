init python:
    import json
    import random

    class ADHDState:
        current_line = 0
        show_next_button = False
        ad_showing = False
        ad_time = persistent.ad_duration
        used_ads = set()
        current_ad = None
        ad_duration = persistent.ad_duration if hasattr(persistent, "ad_duration") else 10
        ad_type = "时政题库"  # 默认广告类型

        def __init__(self, task_type=None):
            # 读取对应任务的文件内容
            if task_type == "writing":
                try:
                    with open(renpy.loader.transfn("data/task/writing.json"), "r", encoding='utf-8') as f:
                        self.content = json.load(f)
                except:
                    self.content = ["示例写作内容"]
            elif task_type == "exercise":
                try:
                    with open(renpy.loader.transfn("data/task/exercise.json"), "r", encoding='utf-8') as f:
                        self.content = json.load(f)
                except:
                    self.content = ["锻炼示例内容1", "锻炼示例内容2"]
            elif task_type == "expression":
                try:
                    with open(renpy.loader.transfn("data/task/expression.json"), "r", encoding='utf-8') as f:
                        self.content = json.load(f)
                except:
                    self.content = ["表情示例内容1", "表情示例内容2"]
            else:
                self.content = ["示例内容1", "示例内容2"]

        def load_ads(self, ad_type):
            """根据类型加载预定义的广告内容"""
            if ad_type == "时政题库":
                self.ads = [
                    "乡村振兴，既要塑形，也要铸魂",
                    "大盘取厚势，落子开新局",
                    "千川汇海阔，风好正扬帆",
                    "沧海横流显砥柱，万山磅礴看主峰",
                    "天地与我并生，而万物与我为一，人与自然是生命共同体",
                    "就业，一头连着经济大势，一头连着千家万户",
                    "年轻干部把扣子扣严扣正、把基础扎稳扎实、把规矩牢记在心，人生之路才能走得更稳更远"
                ]
            elif ad_type == "专业题库":
                self.ads = [
                    "上下同欲者胜，左右齐一者强",
                    "志不易者成，事不避难者进",
                    "习近平总书记指出，抓创新就是抓发展，谋创新就是谋未来",
                    "人才兴则民族兴，人才强则国家强",
                    "习近平总书记指出，建设生态文明，关系人民福祉，关乎民族未来",
                    "文化如水，浸润无声，连着一个民族的过去、现在和未来"
                ]
            elif ad_type == "公基题库":
                self.ads = [
                    "心中有信仰，脚下有力量",
                    "习近平总书记强调，增进民生福祉是发展的根本目的",
                    "为官避事平生耻，重任千钧惟担当",
                    "空谈误国，实干兴邦",
                    "学者非必为仕，而仕者必为学"
                ]
            else:
                self.ads = ["默认广告内容"]
            
            self.used_ads.clear()  # 清空已使用广告记录

        def get_random_ad(self):
            """获取一条随机广告"""
            if not hasattr(self, 'ads') or not self.ads:
                self.load_ads(self.ad_type)
            if len(self.used_ads) >= len(self.ads):
                self.used_ads.clear()  # 所有广告都用过了，清空已用列表
                return random.choice(self.ads)  # 重新开始随机
            available_ads = [ad for ad in self.ads if ad not in self.used_ads]
            ad = random.choice(available_ads)
            self.used_ads.add(ad)
            return ad

        def next_line(self):
            """移动到下一行，并更新广告时长"""
            if self.current_line < len(self.content) - 1:
                self.current_line += 1
                self.ad_time = persistent.ad_duration  # 使用最新的广告时长
                return True
            return False

        def get_current_content(self):
            """获取当前行内容"""
            return self.content[self.current_line]

        def reset(self):
            """重置到第一行"""
            self.current_line = 0

# ADHD 界面
screen adhd_interface():
    # 广告上框
    frame:
        xalign 0.0
        yalign 1.0
        xpadding 20
        ypadding 10
        vbox:
            text "广告" size 24
            textbutton "时政题库" action [SetVariable("current_ad", "时政题库"), SetVariable("ADHDState.ad_type", "时政题库")]
            textbutton "专业题库" action [SetVariable("current_ad", "专业题库"), SetVariable("ADHDState.ad_type", "专业题库")]
            textbutton "公基题库" action [SetVariable("current_ad", "公基题库"), SetVariable("ADHDState.ad_type", "公基题库")]

    # 任务下拉框
    frame:
        xalign 0.0
        yalign 0.0
        xpadding 20
        ypadding 10
        vbox:
            text "任务" size 24
            if current_task != "抄写文案":
                textbutton "抄写文案" action Jump("adhd_writing")
            else:
                textbutton "抄写文案" action NullAction() text_color "#888888"

            if current_task != "锻炼身体":
                textbutton "锻炼身体" action Jump("adhd_exercise")
            else:
                textbutton "锻炼身体" action NullAction() text_color "#888888"

            if current_task != "表情管理":
                textbutton "表情管理" action Jump("adhd_expression")
            else:
                textbutton "表情管理" action NullAction() text_color "#888888"

# 设置按钮
screen adhd_settings_button():
    frame:
        xalign 1.0
        yalign 0.0
        padding (20, 10)
        textbutton "设置" action Show("adhd_settings")

# 设置界面
screen adhd_settings():
    modal True
    frame:
        xalign 0.5
        yalign 0.5
        xsize 300  # 设置固定宽度
        padding (20, 20)  # 减小内边距
        background "#ffffff"
        
        # 关闭按钮
        frame:
            xalign 1.0
            yalign 0.0
            xoffset 10  # 调整位置
            yoffset -10
            background None
            textbutton "×" action Hide("adhd_settings") style "close_button"
        
        vbox:
            spacing 10  # 减小间距
            text "广告时长设置" size 24 xalign 0.5  # 减小标题大小

            # 预设时长选项
            hbox:
                spacing 10  # 减小按钮间距
                xalign 0.5
                for duration in [10, 20, 30]:
                    if persistent.ad_duration == duration:
                        textbutton "[duration]秒":
                            action [
                                SetVariable("persistent.ad_duration", duration),
                                Hide("adhd_settings")
                            ]
                            style "selected_duration_button"
                    else:
                        textbutton "[duration]秒":
                            action [
                                SetVariable("persistent.ad_duration", duration),
                                Hide("adhd_settings")
                            ]
                            style "duration_button"

            # 回到主页按钮
            textbutton "回到主页" action [
                Hide("adhd_settings"),
                Hide("adhd_interface"),
                Hide("adhd_settings_button"),
                Hide("adhd_writing_screen"),
                Hide("message"),
                Jump("start")
            ] style "duration_button" xalign 0.5

# 添加广告时长快捷按钮
screen ad_duration_button():
    frame:
        xalign 0.5
        yalign 0.0
        padding (10, 5)
        background "#dddddd"
        
        textbutton "[persistent.ad_duration]秒":
            action [
                SetVariable("persistent.ad_duration", 
                    30 if persistent.ad_duration == 20 else 
                    10 if persistent.ad_duration == 30 else 20)
            ]
            style "quick_duration_button"

# 修改按钮样式
style duration_button:
    xpadding 15  # 减小按钮内边距
    ypadding 5
    size 20  # 减小字体大小
    background "#dddddd"
    hover_background "#bbbbbb"
    color "#000000"

style selected_duration_button:
    xpadding 15
    ypadding 5
    size 20
    background "#4169E1"
    hover_background "#4169E1"
    color "#000000"

style close_button:
    xpadding 5
    ypadding 2
    size 20  # 减小关闭按钮大小
    color "#000000"
    hover_color "#ff0000"

style quick_duration_button:
    xpadding 10
    ypadding 5
    size 20
    background None
    hover_background "#bbbbbb"
    color "#000000"

# ADHD 写作页面屏幕
screen adhd_writing_screen():
    modal True

    # 背景
    add "bg room"

    # 继承下拉框和设置按钮
    use adhd_interface
    use adhd_settings_button
    use ad_duration_button  # 添加广告时长快捷按钮

    # 内容显示区域（居中的文本框）
    frame:
        xalign 0.5
        yalign 0.5
        xsize 800
        ysize 200
        background "#ffffff"
        padding (20, 20)

        text adhd_state.get_current_content():
            xalign 0.5
            yalign 0.5
            size 30
            color "#000000"
            text_align 0.5

    # 下一条按钮
    if adhd_state.show_next_button:
        frame:
            xalign 0.5
            yalign 0.8
            padding (20, 10)
            background "#ffffff"
            textbutton "下一条" action [
                SetField(adhd_state, "ad_showing", True),
                SetField(adhd_state, "ad_time", persistent.ad_duration),
                SetField(adhd_state, "show_next_button", False)
            ] text_size 30

    # 广告遮罩层
    if adhd_state.ad_showing:
        # 全屏遮罩
        add "bg meditation" size (1920, 1080)

        # 广告内容显示框
        frame:
            xalign 0.5
            yalign 0.5
            xsize 800
            ysize 200
            background "#ffffff"
            padding (20, 20)

            text adhd_state.current_ad or "":
                xalign 0.5
                yalign 0.5
                size 30
                color "#000000"
                text_align 0.5

        # 广告倒计时
        frame:
            xalign 0.5
            yalign 0.9
            padding (20, 10)
            text "广告剩余时间: [adhd_state.ad_time]秒" size 30

        # 广告计时器
        timer 1.0 repeat True action [
            SetField(adhd_state, "ad_time", adhd_state.ad_time - 1),
            SetField(adhd_state, "current_ad", adhd_state.get_random_ad()),
            If(adhd_state.ad_time <= 0, [
                SetField(adhd_state, "ad_showing", False),
                Function(adhd_state.next_line),
                SetField(adhd_state, "show_next_button", False),
                SetField(adhd_state, "current_ad", None)
            ])
        ]

    # 5秒后显示下一条按钮的计时器
    if not adhd_state.show_next_button and not adhd_state.ad_showing:
        timer 5.0 action SetField(adhd_state, "show_next_button", True)
