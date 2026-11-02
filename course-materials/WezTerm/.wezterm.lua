-- ~ (your home directory)

local wezterm = require "wezterm"
local omarchy = require "omarchy"

local config = {}

if wezterm.config_builder then
    config = wezterm.config_builder()
end

-- PERFORMANCE
-- config.front_end = "WebGpu" -- for emulated GPU on VM
-- config.webgpu_power_preference = "LowPower"
config.front_end = "OpenGL" -- if your GPU supports it
-- config.front_end = "Software"
-- config.animation_fps = 60
-- config.max_fps = 60
-- config.allow_win32_input_mode = false

-- Default shell = Git Bash
config.default_prog = {
    "C:/Program Files/Git/bin/bash.exe", "--login", "-i"
}

config.set_environment_variables = {
    SHELL = "bash",
    TERM = "xterm-256color",
}

-- shift+enter
config.keys = {
    {
        key = "Enter",
        mods = "SHIFT",
        action = wezterm.action.SendString("\x0a"),
    },
}

config.launch_menu = {
    {
        label = "Git Bash",
        args  = { "C:/Program Files/Git/bin/bash.exe", "--login", "-i" },
    },
    -- {
    --   label = "PowerShell 7 (pwsh)",
    --   args  = { "C:/Program Files/PowerShell/7/pwsh.exe", "-NoLogo" },
    -- },
    {
        label = "Windows PowerShell",
        args  = { "C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe", "-NoLogo" },
    },
    { label = "WSL (Ubuntu)", domain = { DomainName = "WSL:Ubuntu" } },
}

-- COLOR THEME
config.colors = omarchy.colors

-- FONT
config.font = wezterm.font_with_fallback({
    "JetBrainsMono Nerd Font",
    "Symbols Nerd Font Mono",
    "Noto Color Emoji",
})
config.font_size = 12

-- WINDOW LOOK — Ghostty style
config.window_padding = { left = 8, right = 14, top = 8, bottom = 8 }
config.window_decorations = "INTEGRATED_BUTTONS"
config.use_fancy_tab_bar = true
config.hide_tab_bar_if_only_one_tab = false
config.tab_bar_at_bottom = false
config.adjust_window_size_when_changing_font_size = true
config.enable_scroll_bar = true

-- CURSOR
config.default_cursor_style = "SteadyBlock"
config.cursor_blink_rate = 0

-- COPY/PASTE (Ghostty-style)
-- config.keys = {
--   { key="c", mods="SUPER", action=wezterm.action.CopyTo("Clipboard") },
--   { key="v", mods="SUPER", action=wezterm.action.PasteFrom("Clipboard") },
-- }

return config
