from enum import Enum

# マップの情報はテキストファイルを読み取って配列に変換する
# 配列内にはマスの情報を格納している
# マスの情報はクラスを使用すること
# ユーザーからの入力を受けて移動を行う（どんな入力を受け付けるかは自由）
# リセット機能を付けること

class DirectionType(Enum):
    RIGHT = "d"
    LEFT = "a"
    UP = "w"
    DOWN = "s"
    RESET = "r"

    def get_direction_type(ch):
        for direction_type in DirectionType:
            if direction_type.value[0] == ch:
                return direction_type
        return None


# マスのタイプ管理
class MassType(Enum):
    SPACE = ("0", "　")
    BOX = ("1", "箱")
    WALL = ("2", "壁")
    USER = ("3", "人")
    GOAL = ("4", "ゴ")

    # タプル内の番号からMassTypeを取得
    def get_mass_type(ch):
        for mass_type in MassType:
            if mass_type.value[0] == ch:
                return mass_type
            
# マス情報の管理クラス
class MassInfo():
    # マスのタイプとゴール有無を設定
    def __init__(self, mass_type):
        self.mass_type = mass_type
        if mass_type == MassType.GOAL:
            self.goal = True
        else:
            self.goal = False
    
    # 表示文字列を取得
    def get_disp(self):
        return self.mass_type.value[1]

# マップ情報を出力
def disp_map(souko_map):
    for row in souko_map:
        row_str = ""
        for mass in row:
            row_str = row_str + mass.get_disp()
        print(row_str)

# マップ情報を生成
def create_map_info():
    # テキストファイルからマップ情報を取得
    f = None
    try:
        file_name = 'map1.txt'
        print(file_name + "からマップ情報をロード")
        f = open(file_name)
        map_str = f.read()  # ファイル終端まで全て読んだデータを返す
    except Exception as e:
        # 例外が発生した場合の処理は全て上位のexceptに任せる（そのためにraiseでeを投げている）
        print("マップ情報の読み込みに失敗しました。")
        raise e
    finally:
        # ファイルを開いてた場合のみ閉じ処理を行う
        if f is not None:
            f.close()

    # マップ情報を形成(２次元配列でマップ情報を生成する)
    lines = map_str.split('\n') # 改行で区切る(改行文字そのものは戻り値のデータには含まれない)
    souko_map = []
    row = 0
    for line in lines:
        souko_map.append([])
        for ch in line:
            souko_map[row].append(MassInfo(MassType.get_mass_type(ch)))
        row = row + 1
    
    # マップ情報を返却
    return souko_map

# ユーザーの入力を取得
def user_input():
    direction = None
    directions = [DirectionType.UP, DirectionType.DOWN, DirectionType.LEFT, DirectionType.RIGHT, DirectionType.RESET]
    while True:
        # 進行方向を入力してもらい、DirectionTypeに変換してから入力内容が合っているか確認
        print("進行方向を入力してください。")
        print("a: 左, w:上, d:右, s:下, r:リセット")
        user_input_direction = input("進行方向：")
        direction = DirectionType.get_direction_type(user_input_direction)
        if directions.count(direction) == 0:
            print("入力内容が間違っています。　入力した進行方向：" + user_input_direction)
        else:
            break
    return direction

# 移動方向の取得
def get_move_index(direction):
    move_row_index = 0
    move_col_index = 0

    if direction == DirectionType.LEFT:
        # 左
        move_col_index = -1
    elif direction == DirectionType.UP:
        # 上
        move_row_index = -1
    elif direction == DirectionType.RIGHT:
        # 右
        move_col_index = 1
    elif direction == DirectionType.DOWN:
        # 下
        move_row_index = 1
    return {"row": move_row_index, "col":move_col_index}

# 移動可能か判定
def is_move(souko_map, direction):
    # 移動量を計算
    move_index = get_move_index(direction)

    # ユーザーの現在地を取得
    place = get_user_place(souko_map)

    # 移動先の情報を取得
    mass = souko_map[place["row"] + move_index["row"]][place["col"] + move_index["col"]]
    if mass.mass_type == MassType.WALL:
        # 壁には移動不可
        return False
    elif mass.mass_type == MassType.SPACE or mass.mass_type == MassType.GOAL:
        # 空白とゴールには移動可能
        return True
    elif  mass.mass_type == MassType.BOX:
        # 移動先が箱の場合、箱の先が空白もしくはゴールか確認する
        mass2 = souko_map[place["row"] + (move_index["row"] * 2)][place["col"] + (move_index["col"] * 2)]
        if mass2.mass_type == MassType.SPACE or mass2.mass_type == MassType.GOAL:
            # 箱の先に障害物が無いので移動可能
            return True
        else:
            # 箱の先に何か障害物があるので移動不可
            return False

# ユーザーの現在の場所を取得
def get_user_place(souko_map):
    row_index = 0
    col_index = 0
    for row in souko_map:
        for mass in row:
            if mass.mass_type == MassType.USER:
                # 人を発見、massの座標を取得
                row_index = souko_map.index(row)
                col_index = row.index(mass)

    # print("現在地： 行番号：" +  str(row_index) + ", 列番号：" + str(col_index))
    return {"row": row_index, "col": col_index}

# 移動処理
def move(souko_map, direction):
    # 移動可能か判定
    move_judge = is_move(souko_map, direction)

    if move_judge == False:
        print("移動できません")
        return souko_map

    # ユーザーの座標を取得
    place = get_user_place(souko_map)
    # 移動量を取得
    move_index = get_move_index(direction)
    # ユーザーの座標からsouko_map内のマスを取得
    now = souko_map[place["row"]][place["col"]]
    
    # 移動先の情報を取得
    mass = souko_map[place["row"] + move_index["row"]][place["col"] + move_index["col"]]
    if mass.mass_type == MassType.SPACE or mass.mass_type == MassType.GOAL:
        # 移動先マス
        mass.mass_type = MassType.USER
        # 移動元マス
        if now.goal == True:
            now.mass_type = MassType.GOAL
        else:
            now.mass_type = MassType.SPACE

    elif mass.mass_type == MassType.BOX:
        # 箱の先マス
        souko_map[place["row"] + (move_index["row"] * 2)][place["col"] + (move_index["col"] * 2)].mass_type = MassType.BOX
        # 箱マス
        mass.mass_type = MassType.USER
        # 移動元マス
        if now.goal == True:
            now.mass_type = MassType.GOAL
        else:
            now.mass_type = MassType.SPACE

    # 移動の結果を詰めた倉庫マップを返却
    return souko_map

# 全てのゴール上に箱が存在しているか確認
def is_goal(souko_map):
    goal_count = 0
    box_on_goal_count = 0
    for row in souko_map:
        for mass in row:
            if mass.goal == True:
                goal_count = goal_count + 1
                if mass.mass_type == MassType.BOX:
                    box_on_goal_count = box_on_goal_count + 1
    
    if goal_count == box_on_goal_count:
        return True
    else:
        return False

# ゲーム処理
def game():
    # マップ情報を読み込み
    souko_map = create_map_info()

    while True:
        # マップを表示
        disp_map(souko_map)

        # ユーザーの入力
        direction = user_input()
        if direction == "r":
            print("マップ情報をリセットします。")
            souko_map = create_map_info()

        # 移動
        souko_map = move(souko_map, direction)

        # ゴール判定
        if is_goal(souko_map):
            disp_map(souko_map)
            print("ゲームクリア！！！！")
            break

# ゲーム開始
try:
    game()
except:
    print("ゲームを中断します。")