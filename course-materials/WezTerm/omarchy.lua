-- ~/.config/wezterm

local M = {}

M.colors = {
    foreground = "#a9b1d6",
    background = "#1a1b26",

    cursor_bg = "#c0caf5",
    cursor_fg = "#1a1b26",
    cursor_border = "#c0caf5",

    selection_bg = "#7aa2f7",
    selection_fg = "#c0caf5",

    scrollbar_thumb = "#32344a",

    ansi = {
        "#32344a", -- 0 black
        "#f7768e", -- 1 red
        "#9ece6a", -- 2 green
        "#e0af68", -- 3 yellow
        "#7aa2f7", -- 4 blue
        "#ad8ee6", -- 5 magenta
        "#449dab", -- 6 cyan
        "#787c99", -- 7 white
    },

    brights = {
        "#444b6a", -- 8 bright black
        "#ff7a93", -- 9 bright red
        "#b9f27c", -- 10 bright green
        "#ff9e64", -- 11 bright yellow
        "#7da6ff", -- 12 bright blue
        "#bb9af7", -- 13 bright magenta
        "#0db9d7", -- 14 bright cyan
        "#acb0d0", -- 15 bright white (your missing value)
    },
}

return M
