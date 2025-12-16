"""アプリアイコン生成スクリプト"""

from PIL import Image, ImageDraw, ImageFont
import math


def create_icon():
    """Python AutoUpdate用のアイコンを作成"""
    sizes = [256, 128, 64, 48, 32, 16]
    images = []

    for size in sizes:
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 背景円（ダークブルー）
        padding = size // 16
        draw.ellipse(
            [padding, padding, size - padding, size - padding],
            fill='#1E293B'
        )

        # 中心点
        cx, cy = size // 2, size // 2
        radius = size // 2 - padding * 2

        # 更新矢印を描画（円形の矢印）
        arrow_width = max(2, size // 16)

        # 上部の円弧矢印
        arc_radius = radius * 0.55
        arc_start = -60
        arc_end = 150

        # 円弧を描画
        arc_bbox = [
            cx - arc_radius, cy - arc_radius,
            cx + arc_radius, cy + arc_radius
        ]
        draw.arc(arc_bbox, arc_start, arc_end, fill='#38BDF8', width=arrow_width)

        # 矢印の先端（三角形）
        arrow_size = max(4, size // 10)
        # 円弧の終点に矢印を配置
        end_angle = math.radians(arc_end)
        arrow_x = cx + arc_radius * math.cos(end_angle)
        arrow_y = cy + arc_radius * math.sin(end_angle)

        # 矢印の三角形を描画
        triangle_points = [
            (arrow_x + arrow_size * 0.8, arrow_y - arrow_size * 0.3),
            (arrow_x - arrow_size * 0.3, arrow_y - arrow_size * 0.8),
            (arrow_x - arrow_size * 0.3, arrow_y + arrow_size * 0.5),
        ]
        draw.polygon(triangle_points, fill='#38BDF8')

        # 下部の円弧矢印（反対方向）
        arc_start2 = 120
        arc_end2 = 330

        draw.arc(arc_bbox, arc_start2, arc_end2, fill='#7DD3FC', width=arrow_width)

        # 下の矢印の先端
        end_angle2 = math.radians(arc_end2)
        arrow_x2 = cx + arc_radius * math.cos(end_angle2)
        arrow_y2 = cy + arc_radius * math.sin(end_angle2)

        triangle_points2 = [
            (arrow_x2 - arrow_size * 0.8, arrow_y2 + arrow_size * 0.3),
            (arrow_x2 + arrow_size * 0.3, arrow_y2 + arrow_size * 0.8),
            (arrow_x2 + arrow_size * 0.3, arrow_y2 - arrow_size * 0.5),
        ]
        draw.polygon(triangle_points2, fill='#7DD3FC')

        # 中央にPythonの "Py" テキスト（大きいサイズのみ）
        if size >= 48:
            try:
                font_size = size // 4
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()

            text = "Py"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = cx - text_width // 2
            text_y = cy - text_height // 2
            draw.text((text_x, text_y), text, fill='#E0F2FE', font=font)

        images.append(img)

    # ICOファイルとして保存
    images[0].save(
        'Python_AutoUpdate/icon.ico',
        format='ICO',
        sizes=[(s, s) for s in sizes],
        append_images=images[1:]
    )
    print("アイコンを作成しました: Python_AutoUpdate/icon.ico")

    # PNGも保存（256x256）
    images[0].save('Python_AutoUpdate/icon.png', format='PNG')
    print("PNGも保存しました: Python_AutoUpdate/icon.png")


if __name__ == "__main__":
    create_icon()
