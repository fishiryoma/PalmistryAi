tw_map = {
    "士兵": "pawn",
    "騎士": "knight",
    "主教": "bishop",
    "城堡": "rook",
    "皇后": "queen",
    "國王": "king"
}
jp_map = {
    "士兵": "pawn",
    "騎士": "knight",
    "主教": "bishop",
    "城堡": "rook",
    "皇后": "queen",
    "國王": "king"
}


def role_name(lan, character):
    maps = {
        "tw": tw_map,
        "jp": jp_map
    }
    return maps.get(lan, {}).get(character, 'back')