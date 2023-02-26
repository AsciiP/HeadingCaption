# HeadingCaption

Advanced SubStation Alpha(.ass)字幕文件生成Premiere XML序列。样式可自定义。

# 使用说明

1. 使用Aegisub ([Aegisub - Aegisub Advanced Subtitle Editor](https://aegisub.org/)) 或其他软件制作字幕文件。每条字幕需要指定说话人。
2. 根据说话人，在styles文件夹内创建样式配置文件，文件夹名对应一个说话人。
3. 把字幕文件拖放至程序。片刻后在out文件夹内就可以看到生成好的XML文件和附带的png序列。

# 样式文件参考

```yaml
name: A # 名称，仅做标识用，保持和文件夹一致即可。
bg_margin: 20 # 背景外边缘，也就是包裹文本的厚度。
bg_radius: 20 # 背景圆角矩形半径。
bg_color: orange # 背景颜色。
font_name: Heavy.ttf # 字体名称，在fonts文件夹中的名称。
font_size: 100 # 字体大小。
font_color: white # 字体颜色。
x: 960 # 锚点X坐标。
y: 1050 # 锚点Y坐标。
anchor: md # 文本锚点。可接受：(l, m, r) + (a, m, s, d)。参考：https://v1.mk/PgLAJg3 (Pillow documention)
stroke_width: 5 # 描边粗细。
stroke_color: black # 描边颜色。
logo: no # 人物Logo。有则填该文件夹中的文件名，无则填no。
logo_spacing: 10 # Logo与文本的间距。
```
