"""
GUI样式和主题配置
"""

import customtkinter as ctk

# 设置外观模式和颜色主题
ctk.set_appearance_mode("dark")  # 可选: "light", "dark", "system"
ctk.set_default_color_theme("blue")  # 可选: "blue", "green", "dark-blue"

# 颜色配置
COLORS = {
    'primary': '#1f538d',
    'secondary': '#14375e',
    'success': '#2d5a27',
    'warning': '#8b5a00',
    'danger': '#8b2635',
    'info': '#0c5460',
    'light': '#f8f9fa',
    'dark': '#212529',
    'background': '#212121',
    'surface': '#2b2b2b',
    'text_primary': '#ffffff',
    'text_secondary': '#b0b0b0'
}

# 字体配置
FONTS = {
    'title': ('Microsoft YaHei UI', 18, 'bold'),
    'subtitle': ('Microsoft YaHei UI', 14, 'bold'),
    'body': ('Microsoft YaHei UI', 12),
    'small': ('Microsoft YaHei UI', 10),
    'code': ('Consolas', 11)
}

# 尺寸配置
SIZES = {
    'window_width': 1000,
    'window_height': 650,
    'button_height': 32,
    'input_height': 32,
    'padding': 15,
    'small_padding': 8
}

# 按钮样式配置
BUTTON_STYLES = {
    'primary': {
        'fg_color': COLORS['primary'],
        'hover_color': COLORS['secondary'],
        'height': SIZES['button_height'],
        'font': FONTS['body'],
        'corner_radius': 8
    },
    'success': {
        'fg_color': COLORS['success'],
        'hover_color': '#1e3f1a',
        'height': SIZES['button_height'],
        'font': FONTS['body'],
        'corner_radius': 8
    },
    'warning': {
        'fg_color': COLORS['warning'],
        'hover_color': '#6b4400',
        'height': SIZES['button_height'],
        'font': FONTS['body'],
        'corner_radius': 8
    },
    'danger': {
        'fg_color': COLORS['danger'],
        'hover_color': '#6b1d28',
        'height': SIZES['button_height'],
        'font': FONTS['body'],
        'corner_radius': 8
    }
}
