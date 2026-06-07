import pygame
import sys
import os
import json
from collections import deque
os.chdir(os.path.dirname(os.path.abspath(__file__)))

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700

UI_HEIGHT = 100

screen = pygame.display.set_mode(
    (
        SCREEN_WIDTH,
        SCREEN_HEIGHT
    )
)

pygame.display.set_caption(
    "행소박물관 유물 따라 그리기"
)

clock = pygame.time.Clock()


WHITE = (255,255,255)
BLACK = (0,0,0)

GRAY = (220,220,220)
LIGHT_GRAY = (245,245,245)
DARK_GRAY = (60,60,60)

RED = (220,70,70)
GREEN = (70,180,90)
BLUE = (70,120,220)

BROWN = (150,80,30)
PURPLE = (180,50,200)
CYAN = (0,180,180)
ORANGE = (255,170,0)

font_small = pygame.font.SysFont(
    "malgungothic",
    15
)

font_main = pygame.font.SysFont(
    "malgungothic",
    20
)

font_title = pygame.font.SysFont(
    "malgungothic",
    40,
    bold=True
)

STATE_GALLERY = "GALLERY"
STATE_DRAWING = "DRAWING"
STATE_INFO = "INFO"
STATE_EXHIBITION = "EXHIBITION"

current_state = STATE_GALLERY


artifact_data = [

    (
        "주먹도끼",
        "주먹도끼.png",
        "구석기 시대",
        "사냥과 채집 생활에 사용된 대표적인 석기이다."
    ),

    (
        "분청사기 표주박 모양 병",
        "분청사기표주박모양병.png",
        "조선 전기",
        "표주박 모양을 본떠 제작한 분청사기이다."
    ),

    (
        "빗살무늬토기",
        "빗살무늬토기.png",
        "신석기 시대",
        "빗살무늬가 새겨진 대표적인 토기이다."
    ),

    (
        "봉황을 수놓은 베갯모",
        "봉황을수놓은베갯모.png",
        "조선 시대",
        "봉황 문양이 수놓아진 전통 자수품이다."
    ),

    (
        "간석기",
        "돌칼.png",
        "신석기 시대",
        "갈아서 만든 날을 지니고 있는 도구. 돌도끼, 돌 자귀, 반달 돌칼 등이 존재."
    ),

    (
        "용이 새겨진 자수용 판과 용보",
        "용이새겨진자수용판과용보.png",
        "조선 후기 시대",
        "자수를 놓기 위한 밑그림인 용무늬를 새겨 넣은 나무판. 주로 곤룡포의 가슴, 등, 양 어깨에 장식."
    ),

    (
        "청동거울",
        "청동거울.png",
        "청동기 시대",
        "청동기 시대와 철기 시대에 처음 등장하며, 제사를 진행하고 신분을 과시하는 용도로 사용했을 것으로 추정."
    ),

    (
        "세형동검",
        "세형동검.png",
        "후삼국 시대",
        "후기 청동기시대부터 철기 시대 초기까지 만들어진 청동검의 한 종류."
    ),

    (
        "나전필통",
        "나전필통.png",
        "조선 후기 시대",
        "붓 등 필기구를 꽂아 두기 위한 통."
    ),

    (
        "갑옷과 투구",
        "갑옷과투구.png",
        "삼국 시대",
        "얇은 철판을 옷이나 가죽으로 고정하여 만든 횡장판갑 형식의 갑옷과 측면 반타원형 형태로 4매의 가늘고 긴 철판을 상하로 연결하여 만든 투구."
    )
]


thumb_w = 160
thumb_h = 180

start_x = 40
start_y = 180

gap_x = 30
gap_y = 80

artifacts = []


for i, data in enumerate(
    artifact_data
):

    row = i // 5
    col = i % 5

    x = (
        start_x
        +
        col * (thumb_w + gap_x)
    )

    y = (
        start_y
        +
        row * (thumb_h + gap_y)
    )

    name,file,era,desc = data

    artifact = {

        "name":name,
        "file":file,
        "era":era,
        "description":desc,

        "rect":pygame.Rect(
            x,
            y,
            thumb_w,
            thumb_h
        )
    }

    try:

        raw = pygame.image.load(
            file
        ).convert_alpha()

        artifact["raw"] = raw

        artifact["thumb"] = pygame.transform.smoothscale(
            raw,
            (
                thumb_w,
                thumb_h
            )
        )

    except:

        artifact["raw"] = None
        artifact["thumb"] = None

    artifacts.append(
        artifact
    )


SAVE_FILE = "museum_save.json"

save_data = {

    "completed":[],
    "saved_artworks":[]
}

if os.path.exists(
    SAVE_FILE
):

    try:

        with open(
            SAVE_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            save_data = json.load(f)

    except:
        pass

def save_progress():

    with open(
        SAVE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            save_data,
            f,
            ensure_ascii=False,
            indent=4
        )


ARTWORK_FOLDER = "saved_artworks"

if not os.path.exists(
    ARTWORK_FOLDER
):
    os.makedirs(
        ARTWORK_FOLDER
    )


CANVAS_WIDTH = 2000
CANVAS_HEIGHT = 2000

canvas_surface = pygame.Surface(
    (
        CANVAS_WIDTH,
        CANVAS_HEIGHT
    ),
    pygame.SRCALPHA
)

canvas_surface.fill(
    (0,0,0,0)
)


zoom = 1.0

camera_x = 0
camera_y = 0

is_panning = False

pan_last_mouse = (0,0)


TOOL_BRUSH = "BRUSH"
TOOL_ERASER = "ERASER"
TOOL_FILL = "FILL"

current_tool = TOOL_BRUSH

brush_size = 3

current_color = BLACK

palette_colors = [

    BLACK,
    RED,
    BLUE,
    GREEN,

    ORANGE,
    BROWN,

    PURPLE,
    CYAN
]


undo_stack = []
redo_stack = []

MAX_HISTORY = 30


drawing = False

prev_canvas_pos = None

selected_artifact = None

show_grid = False


class Button:

    def __init__(
        self,
        x,
        y,
        w,
        h,
        text,
        color=DARK_GRAY,
        text_color=WHITE
    ):

        self.rect = pygame.Rect(
            x,
            y,
            w,
            h
        )

        self.text = text
        self.color = color
        self.text_color = text_color

    def draw(self):

        pygame.draw.rect(
            screen,
            self.color,
            self.rect,
            border_radius=8
        )

        pygame.draw.rect(
            screen,
            BLACK,
            self.rect,
            2,
            border_radius=8
        )

        txt = font_main.render(
            self.text,
            True,
            self.text_color
        )

        screen.blit(
            txt,
            (
                self.rect.centerx
                - txt.get_width()//2,

                self.rect.centery
                - txt.get_height()//2
            )
        )

    def clicked(self,pos):

        return self.rect.collidepoint(
            pos
        )


btn_back = Button(
    20,
    20,
    120,
    40,
    "목록으로"
)

btn_save = Button(
    160,
    20,
    120,
    40,
    "이미지 저장"
)

btn_info = Button(
    300,
    20,
    120,
    40,
    "유물 설명"
)

btn_exhibition = Button(
    440,
    20,
    120,
    40,
    "전시관"
)


def draw_collection_progress():

    total = len(
        artifacts
    )

    completed = len(
        save_data["completed"]
    )

    ratio = completed / total

    pygame.draw.rect(
        screen,
        GRAY,
        (
            20,
            SCREEN_HEIGHT-40,
            300,
            20
        )
    )

    pygame.draw.rect(
        screen,
        GREEN,
        (
            20,
            SCREEN_HEIGHT-40,
            int(300*ratio),
            20
        )
    )

    txt = font_small.render(
        f"수집률 : {completed}/{total}",
        True,
        BLACK
    )

    screen.blit(
        txt,
        (
            330,
            SCREEN_HEIGHT-42
        )
    )

def draw_gallery():

    screen.fill(
        WHITE
    )

    title = font_title.render(
        "계명대학교 행소박물관",
        True,
        DARK_GRAY
    )

    screen.blit(
        title,
        (
            SCREEN_WIDTH//2
            -
            title.get_width()//2,
            50
        )
    )

    subtitle = font_main.render(
        "따라 그리고 싶은 유물을 선택하세요",
        True,
        BLACK
    )

    screen.blit(
        subtitle,
        (
            SCREEN_WIDTH//2
            -
            subtitle.get_width()//2,
            120
        )
    )

    for artifact in artifacts:

        pygame.draw.rect(
            screen,
            LIGHT_GRAY,
            artifact["rect"]
        )

        pygame.draw.rect(
            screen,
            DARK_GRAY,
            artifact["rect"],
            3
        )

        if artifact["thumb"]:

            screen.blit(
                artifact["thumb"],
                artifact["rect"].topleft
            )

        txt = font_small.render(
            artifact["name"],
            True,
            BLACK
        )

        screen.blit(
            txt,
            (
                artifact["rect"].centerx
                -
                txt.get_width()//2,

                artifact["rect"].bottom+10
            )
        )

        if (
            artifact["name"]
            in
            save_data["completed"]
        ):

            done = font_small.render(
                "완료",
                True,
                GREEN
            )

            screen.blit(
                done,
                (
                    artifact["rect"].right
                    -
                    done.get_width()
                    -
                    5,

                    artifact["rect"].top
                    +
                    5
                )
            )

    draw_collection_progress()



def draw_info_screen():

    screen.fill(
        WHITE
    )

    btn_back.draw()

    if not selected_artifact:
        return

    title = font_title.render(
        selected_artifact["name"],
        True,
        BLACK
    )

    screen.blit(
        title,
        (
            40,
            120
        )
    )

    era = font_main.render(
        f"시대 : {selected_artifact['era']}",
        True,
        BLUE
    )

    screen.blit(
        era,
        (
            40,
            210
        )
    )

    desc_title = font_main.render(
        "설명",
        True,
        DARK_GRAY
    )

    screen.blit(
        desc_title,
        (
            40,
            280
        )
    )

    description = selected_artifact[
        "description"
    ]

    lines = []

    current = ""

    for word in description.split():

        test = current + word + " "

        if (
            font_main.size(test)[0]
            > 800
        ):

            lines.append(
                current
            )

            current = word + " "

        else:

            current = test

    lines.append(
        current
    )

    y = 340

    for line in lines:

        txt = font_main.render(
            line,
            True,
            BLACK
        )

        screen.blit(
            txt,
            (
                40,
                y
            )
        )

        y += 40


def draw_exhibition():

    screen.fill(
        (
            240,
            235,
            220
        )
    )

    btn_back.draw()

    title = font_title.render(
        "나만의 전시관",
        True,
        DARK_GRAY
    )

    screen.blit(
        title,
        (
            SCREEN_WIDTH//2
            -
            title.get_width()//2,
            30
        )
    )

    x = 40
    y = 120

    count = 0

    for item in save_data[
        "saved_artworks"
    ]:

        frame = pygame.Rect(
            x,
            y,
            180,
            220
        )

        pygame.draw.rect(
            screen,
            (
                130,
                90,
                50
            ),
            frame
        )

        pygame.draw.rect(
            screen,
            WHITE,
            (
                x+10,
                y+10,
                160,
                160
            )
        )

        try:

            img = pygame.image.load(
                item["file"]
            ).convert()

            img = pygame.transform.smoothscale(
                img,
                (
                    160,
                    160
                )
            )

            screen.blit(
                img,
                (
                    x+10,
                    y+10
                )
            )

        except:
            pass

        txt = font_small.render(
            item["name"],
            True,
            BLACK
        )

        screen.blit(
            txt,
            (
                x+10,
                y+185
            )
        )

        x += 210

        count += 1

        if count % 4 == 0:

            x = 40
            y += 250


def draw_status_bar():

    pygame.draw.rect(
        screen,
        GRAY,
        (
            0,
            0,
            SCREEN_WIDTH,
            UI_HEIGHT
        )
    )

    btn_back.draw()
    btn_save.draw()
    btn_info.draw()
    btn_exhibition.draw()

    txt = font_small.render(
        f"도구 : {current_tool}",
        True,
        BLACK
    )

    screen.blit(
        txt,
        (
            600,
            15
        )
    )

    txt2 = font_small.render(
        f"굵기 : {brush_size}",
        True,
        BLACK
    )

    screen.blit(
        txt2,
        (
            600,
            35
        )
    )

    txt3 = font_small.render(
        f"확대 : {int(zoom*100)}%",
        True,
        BLACK
    )

    screen.blit(
        txt3,
        (
            600,
            55
        )
    )


def draw_shortcuts():

    lines = [

        "Z : 실행취소",
        "Y : 다시실행",

        "B : 브러시",
        "E : 지우개",

        "F : 페인트",

        "G : 격자",

        "↑ ↓ : 굵기",

        "휠 : 확대/축소",

        "가운데버튼 : 이동"
    ]

    y = 100

    for line in lines:

        txt = font_small.render(
            line,
            True,
            BLACK
        )

        screen.blit(
            txt,
            (
                810,
                y
            )
        )

        y += 22


def push_undo():

    undo_stack.append(
        canvas_surface.copy()
    )

    if len(undo_stack) > MAX_HISTORY:

        undo_stack.pop(0)



def undo():

    if not undo_stack:
        return

    redo_stack.append(
        canvas_surface.copy()
    )

    old = undo_stack.pop()

    canvas_surface.fill(
        (0,0,0,0)
    )

    canvas_surface.blit(
        old,
        (0,0)
    )


def redo():

    if not redo_stack:
        return

    undo_stack.append(
        canvas_surface.copy()
    )

    old = redo_stack.pop()

    canvas_surface.fill(
        (0,0,0,0)
    )

    canvas_surface.blit(
        old,
        (0,0)
    )

def screen_to_canvas(pos):

    mx,my = pos

    cx = int(
        (mx - camera_x)
        / zoom
    )

    cy = int(
        (my - camera_y)
        / zoom
    )

    return cx,cy


def canvas_to_screen(pos):

    x,y = pos

    sx = int(
        x * zoom
        + camera_x
    )

    sy = int(
        y * zoom
        + camera_y
    )

    return sx,sy


def get_draw_size():

    if current_tool == TOOL_BRUSH:
        return brush_size

    return brush_size


def draw_line(start,end):

    if current_tool == TOOL_ERASER:

        pygame.draw.line(
            canvas_surface,
            (0,0,0,0),
            start,
            end,
            brush_size * 2
        )

    else:

        pygame.draw.line(
            canvas_surface,
            current_color,
            start,
            end,
            get_draw_size()
        )


def flood_fill(
    surface,
    x,
    y,
    fill_color
):

    width = surface.get_width()
    height = surface.get_height()

    if (
        x < 0
        or y < 0
        or x >= width
        or y >= height
    ):
        return

    target = surface.get_at(
        (x,y)
    )

    replacement = (
        fill_color[0],
        fill_color[1],
        fill_color[2],
        255
    )

    if target == replacement:
        return

    queue = deque()

    queue.append(
        (x,y)
    )

    while queue:

        px,py = queue.popleft()

        if (
            px < 0
            or py < 0
            or px >= width
            or py >= height
        ):
            continue

        if (
            surface.get_at(
                (px,py)
            )
            != target
        ):
            continue

        surface.set_at(
            (px,py),
            replacement
        )

        queue.append(
            (px+1,py)
        )

        queue.append(
            (px-1,py)
        )

        queue.append(
            (px,py+1)
        )

        queue.append(
            (px,py-1)
        )


def use_fill_tool(pos):

    cx,cy = screen_to_canvas(
        pos
    )

    if (
        cx < 0
        or cy < 0
        or cx >= CANVAS_WIDTH
        or cy >= CANVAS_HEIGHT
    ):
        return

    push_undo()

    flood_fill(
        canvas_surface,
        cx,
        cy,
        current_color
    )


def zoom_at_point(
    mouse_pos,
    zoom_factor
):

    global zoom
    global camera_x
    global camera_y

    mx,my = mouse_pos

    before_x = (
        mx - camera_x
    ) / zoom

    before_y = (
        my - camera_y
    ) / zoom

    zoom *= zoom_factor

    zoom = max(
        0.25,
        min(
            zoom,
            8.0
        )
    )

    camera_x = mx - before_x * zoom
    camera_y = my - before_y * zoom


def start_pan(pos):

    global is_panning
    global pan_last_mouse

    is_panning = True

    pan_last_mouse = pos

def update_pan(pos):

    global camera_x
    global camera_y
    global pan_last_mouse

    if not is_panning:
        return

    dx = pos[0] - pan_last_mouse[0]
    dy = pos[1] - pan_last_mouse[1]

    camera_x += dx
    camera_y += dy

    pan_last_mouse = pos

def stop_pan():

    global is_panning

    is_panning = False


def draw_grid():

    if not show_grid:
        return

    spacing = int(
        50 * zoom
    )

    if spacing < 8:
        return

    x = camera_x % spacing

    while x < SCREEN_WIDTH:

        pygame.draw.line(
            screen,
            (220,220,220),
            (x,0),
            (x,SCREEN_HEIGHT)
        )

        x += spacing

    y = camera_y % spacing

    while y < SCREEN_HEIGHT:

        pygame.draw.line(
            screen,
            (220,220,220),
            (0,y),
            (SCREEN_WIDTH,y)
        )

        y += spacing


def draw_canvas():

    scaled_w = int(
        CANVAS_WIDTH
        * zoom
    )

    scaled_h = int(
        CANVAS_HEIGHT
        * zoom
    )

    scaled_canvas = pygame.transform.smoothscale(
        canvas_surface,
        (
            scaled_w,
            scaled_h
        )
    )

    screen.blit(
        scaled_canvas,
        (
            camera_x,
            camera_y
        )
    )


def draw_reference_image():

    if not selected_artifact:
        return

    if not selected_artifact["raw"]:
        return

    raw = selected_artifact["raw"]

    visible_height = (
        SCREEN_HEIGHT
        - UI_HEIGHT
    )

    ratio = (
        visible_height
        / raw.get_height()
    )

    base_w = int(
        raw.get_width()
        * ratio
    )

    base_h = int(
        raw.get_height()
        * ratio
    )

    scaled_w = int(
        base_w * zoom
    )

    scaled_h = int(
        base_h * zoom
    )

    img = pygame.transform.smoothscale(
        raw,
        (
            scaled_w,
            scaled_h
        )
    )

    img.set_alpha(120)

    screen.blit(
        img,
        (
            camera_x,
            camera_y + UI_HEIGHT
        )
    )


def draw_palette():

    start_x = 700

    for i,color in enumerate(
        palette_colors
    ):

        rect = pygame.Rect(
            start_x + i*35,
            20,
            30,
            30
        )

        pygame.draw.rect(
            screen,
            color,
            rect
        )

        pygame.draw.rect(
            screen,
            BLACK,
            rect,
            1
        )
        
def palette_click(pos):

    start_x = 700

    for i, color in enumerate(palette_colors):

        rect = pygame.Rect(
            start_x + i * 35,
            20,
            30,
            30
        )

        if rect.collidepoint(pos):

            return color

    return None


def draw_drawing_screen():

    screen.fill(
        WHITE
    )

    draw_reference_image()

    draw_canvas()

    draw_grid()

    draw_status_bar()

    draw_shortcuts()

    draw_palette()


def save_current_artwork():

    if not selected_artifact:
        return

    filename = (
        selected_artifact["name"]
        .replace(" ","_")
        + ".png"
    )

    filepath = os.path.join(
        ARTWORK_FOLDER,
        filename
    )

    save_surface = pygame.Surface(
        (
            CANVAS_WIDTH,
            CANVAS_HEIGHT
        ),
        pygame.SRCALPHA
    )

    save_surface.blit(
        canvas_surface,
        (0,0)
    )

    pygame.image.save(
        save_surface,
        filepath
    )

    if (
        selected_artifact["name"]
        not in save_data["completed"]
    ):

        save_data["completed"].append(
            selected_artifact["name"]
        )

    exists = False

    for item in save_data[
        "saved_artworks"
    ]:

        if (
            item["name"]
            ==
            selected_artifact["name"]
        ):

            exists = True

    if not exists:

        save_data[
            "saved_artworks"
        ].append(

            {
                "name":
                selected_artifact["name"],

                "file":
                filepath
            }
        )

    save_progress()


def open_artifact(artifact):

    global selected_artifact
    global current_state
    global zoom
    global camera_x
    global camera_y

    selected_artifact = artifact

    canvas_surface.fill(
        (0,0,0,0)
    )

    undo_stack.clear()
    redo_stack.clear()

    zoom = 1.0

    camera_x = 0
    camera_y = 0

    current_state = STATE_DRAWING


running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False


        if current_state == STATE_GALLERY:

            if event.type == pygame.MOUSEBUTTONDOWN:

                for artifact in artifacts:

                    if artifact["rect"].collidepoint(
                        event.pos
                    ):

                        open_artifact(
                            artifact
                        )


        elif current_state == STATE_INFO:

            if event.type == pygame.MOUSEBUTTONDOWN:

                if btn_back.clicked(
                    event.pos
                ):

                    current_state = (
                        STATE_GALLERY
                    )


        elif current_state == STATE_EXHIBITION:

            if event.type == pygame.MOUSEBUTTONDOWN:

                if btn_back.clicked(
                    event.pos
                ):

                    current_state = (
                        STATE_GALLERY
                    )


        elif current_state == STATE_DRAWING:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_b:

                    current_tool = TOOL_BRUSH

                elif event.key == pygame.K_e:

                    current_tool = TOOL_ERASER

                elif event.key == pygame.K_f:

                    current_tool = TOOL_FILL

                elif event.key == pygame.K_g:

                    show_grid = (
                        not show_grid
                    )

                elif event.key == pygame.K_z:

                    undo()

                elif event.key == pygame.K_y:

                    redo()

                elif event.key == pygame.K_UP:

                    brush_size += 1

                elif event.key == pygame.K_DOWN:

                    brush_size = max(
                        1,
                        brush_size - 1
                    )


                elif event.key == pygame.K_1:

                    current_color = BLACK

                elif event.key == pygame.K_2:

                    current_color = RED

                elif event.key == pygame.K_3:

                    current_color = BLUE

                elif event.key == pygame.K_4:

                    current_color = GREEN


            if event.type == pygame.MOUSEWHEEL:

                if event.y > 0:

                    zoom_at_point(
                        pygame.mouse.get_pos(),
                        1.1
                    )

                else:

                    zoom_at_point(
                        pygame.mouse.get_pos(),
                        0.9
                    )


            if event.type == pygame.MOUSEBUTTONDOWN:


                if event.button == 2:

                    start_pan(
                        event.pos
                    )


                elif event.button == 1:
                    new_color = palette_click(event.pos)

                    if new_color:
                        
                        current_color = new_color

                    if btn_back.clicked(
                        event.pos
                    ):

                        current_state = (
                            STATE_GALLERY
                        )

                    elif btn_save.clicked(
                        event.pos
                    ):

                        save_current_artwork()

                    elif btn_info.clicked(
                        event.pos
                    ):

                        current_state = (
                            STATE_INFO
                        )

                    elif btn_exhibition.clicked(
                        event.pos
                    ):

                        current_state = (
                            STATE_EXHIBITION
                        )

                    else:

                        if (
                            current_tool
                            ==
                            TOOL_FILL
                        ):

                            use_fill_tool(
                                event.pos
                            )

                        else:

                            push_undo()

                            drawing = True

                            prev_canvas_pos = (
                                screen_to_canvas(
                                    event.pos
                                )
                            )


            if event.type == pygame.MOUSEBUTTONUP:

                if event.button == 1:

                    drawing = False

                    prev_canvas_pos = None

                elif event.button == 2:

                    stop_pan()


            if event.type == pygame.MOUSEMOTION:

                if is_panning:

                    update_pan(
                        event.pos
                    )


    if (
        current_state
        ==
        STATE_DRAWING
        and drawing
    ):

        current_canvas_pos = (
            screen_to_canvas(
                pygame.mouse.get_pos()
            )
        )

        if prev_canvas_pos:

            draw_line(
                prev_canvas_pos,
                current_canvas_pos
            )

        prev_canvas_pos = (
            current_canvas_pos
        )


    if current_state == STATE_GALLERY:

        draw_gallery()

    elif current_state == STATE_DRAWING:

        draw_drawing_screen()

    elif current_state == STATE_INFO:

        draw_info_screen()

    elif current_state == STATE_EXHIBITION:

        draw_exhibition()

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()