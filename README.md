# Treasure Hunt

Treasure Hunt là game desktop local viết bằng **Python + Pygame**. Người chơi thi đấu trên lưới `20x20`, đào theo chuỗi gợi ý `Key 1 -> Key 2 -> Key 3 -> Treasure`, né bomb, dùng skill để phá nhịp đối thủ, và tận dụng địa hình có tường chắn.

Project hiện là **Pygame desktop game**, không phải web game.

## Tổng quan

Game hỗ trợ 3 chế độ:

- `PvP`: 2 người chơi local trên cùng máy
- `PvE`: 1 người chơi đấu AI
- `EvE`: 2 bot tự chơi để quan sát và test balance

Flow hiện tại của game:

`Start -> Mode Select -> Difficulty Select -> Match -> End`

Ngoài màn chơi chính, game còn có:

- `Settings`
- `Manual`
- chuyển ngôn ngữ `English / Tiếng Việt`
- nhạc nền và hiệu ứng âm thanh
- fullscreen

## Gameplay

### Luật cốt lõi

- Map là grid `20x20`
- `Tile size = 32px`
- Mỗi bên có layout tương đương để giữ tính công bằng
- Treasure bị khóa cho đến khi đã thu thập đủ `3 key`
- Key phải lấy đúng thứ tự:
  - `Key 1`
  - `Key 2`
  - `Key 3`
  - sau đó mới được đào `Treasure`
- Đào sai ô sẽ bị `cooldown / stun`
- Đào trúng bomb sẽ mất `1 HP`
- Hết HP là thua
- Hết thời gian là hòa
- Tường là vật cản, người chơi và bot đều không được đi xuyên qua

### Điều kiện thắng

Một bên thắng khi:

- đã lấy đủ `3 key`
- và đào được `Treasure`

Hoặc khi đối thủ:

- mất hết HP

## Skill System

Game hiện có 3 skill chính:

### Freeze

- Đóng băng đối thủ trong vài giây
- Trong thời gian hiệu lực, đối thủ không thể di chuyển hoặc hành động bình thường

### Blind

- Hạn chế thông tin của đối thủ trong thời gian ngắn
- Với người chơi: clue bị che
- Với bot: hành vi kém tối ưu hơn trong lúc effect còn hiệu lực

### Extra Hint

- Reveal thêm thông tin về mục tiêu hợp lệ tiếp theo

### Quy tắc chung của skill

- Mỗi skill có cooldown riêng
- Mỗi skill có duration riêng
- Skill phải có target hợp lệ theo từng loại

## Chế độ chơi

### PvP

2 người chơi local thi đấu trên cùng máy.

Phù hợp để:

- đấu trực tiếp người với người
- test control
- test skill đối kháng

### PvE

1 người chơi đấu AI.

Các mức độ khó:

- `Easy`: di chuyển chậm hơn, kém tối ưu hơn, sai nhiều hơn
- `Normal`: ổn định, vẫn có độ trễ và ngẫu nhiên vừa phải
- `Hard`: tối ưu hơn, ít sai hơn, dùng pathfinding tốt hơn

### EvE

2 bot tự chơi với nhau.

Phù hợp để:

- quan sát hành vi AI
- xem pacing trận đấu
- kiểm tra balance map và difficulty

## Điều khiển

### Phím chung

- `F11`: bật / tắt fullscreen
- `Alt + Enter`: bật / tắt fullscreen
- `ESC`: thoát fullscreen trước; nếu không ở fullscreen thì thoát màn hiện tại tùy ngữ cảnh

### Trong menu

- `Enter`: xác nhận
- `Space`: xác nhận ở một số màn
- `1 / 2 / 3`: chọn nhanh mode hoặc difficulty ở màn tương ứng
- Có thể bấm chuột trực tiếp vào button

### Trong trận

- `Tab`: pause / resume
- `F10`: mở settings
- `R`: restart ván hiện tại

### PvP

#### Player 1

- `W / A / S / D`: di chuyển
- `Space` hoặc `Left Ctrl`: đào
- `Q`: Freeze
- `E`: Blind
- `F`: Extra Hint

#### Player 2

- `Arrow Keys`: di chuyển
- `Enter`, `Numpad Enter`, hoặc `Right Ctrl`: đào
- `I`: Freeze
- `O`: Blind
- `P`: Extra Hint

### PvE

Người chơi:

- `W / A / S / D` hoặc `Arrow Keys`: di chuyển
- `Space`, `Enter`, `Left Ctrl`, hoặc `Numpad Enter`: đào
- `Q`: Freeze bot
- `E`: Blind bot
- `F`: Extra Hint

### EvE

Không có điều khiển di chuyển trực tiếp cho người chơi.

Các phím hữu ích:

- `Tab`: pause / resume
- `R`: restart
- `F10`: settings
- `F11`: fullscreen

## UI hiện có

Game đang có đầy đủ các màn sau:

- `Start`
- `Mode Select`
- `Difficulty Select`
- `Settings`
- `Manual`
- `Gameplay`
- `Pause`
- `Game Over`

### Settings

Hiện hỗ trợ các tùy chọn:

- `Music`
- `SFX`
- `Hints`
- `Language`
- `Manual`

### Manual

Manual mở từ `Settings`, dùng để hiển thị:

- mục tiêu game
- luật chơi
- điều khiển
- skill

### Ngôn ngữ

UI hiện hỗ trợ:

- `English`
- `Tiếng Việt`

## AI và map

### AI

Bot sử dụng pathfinding hợp lệ để tìm đường trong map có tường.

Hiện game đã có:

- A* pathfinding
- hành vi khác nhau theo difficulty
- dùng skill trong các mode có bot

### Map

Map có:

- chuỗi hint / key
- treasure bị khóa
- bomb
- tường ngẫu nhiên
- kiểm tra để đảm bảo vẫn còn đường đi hợp lệ

## Audio

### Nhạc nền

Game tự tìm nhạc nền theo các key sau:

- `assets/music/menu.ogg` hoặc `assets/music/menu.mp3`
- `assets/music/gameplay.ogg` hoặc `assets/music/gameplay.mp3`
- `assets/music/result.ogg` hoặc `assets/music/result.mp3`

### Sound effects

SFX được load từ `assets/sounds/`.

Nếu thiếu asset âm thanh, game vẫn phải chạy mà không crash.

## Cài đặt và chạy

### Yêu cầu

- Python `3.11` được khuyến nghị
- `pygame >= 2.1.0`

### Cài thư viện

```bash
pip install -r requirements.txt
```

### Chạy game

```bash
python main.py
```

## Kiểm tra

### Compile check

```bash
python -m compileall src
```

### Chạy test

```bash
python -m unittest discover -s tests
```

### Test hiện có

- `tests/test_gameplay_logic.py`
  - map rules
  - locked treasure
  - wall blocking
  - skill effects
  - input regressions
- `tests/test_runtime_smoke.py`
  - menu flow
  - start match theo mode
  - settings / language / manual
  - restart / end flow
  - gameplay runtime smoke

## Cấu trúc dự án

```text
treasure-hunt/
|-- assets/
|   |-- images/
|   |-- music/
|   `-- sounds/
|-- scripts/
|   `-- generate_placeholder_sfx.py
|-- src/
|   |-- __init__.py
|   |-- audio_manager.py
|   |-- bot_ai.py
|   |-- entities.py
|   |-- game.py
|   |-- game_mode.py
|   |-- game_state.py
|   |-- hint_system.py
|   |-- map.py
|   |-- player.py
|   |-- settings.py
|   |-- skills.py
|   |-- ui.py
|   |-- ui_manager.py
|   `-- utils.py
|-- tests/
|   |-- test_gameplay_logic.py
|   `-- test_runtime_smoke.py
|-- main.py
|-- settings.py
|-- README.md
|-- requirements.txt
|-- REFACTORING_SUMMARY.md
`-- RULES.md
```
### UI và audio

- `src/ui_manager.py`
  - menu
  - HUD
  - settings
  - manual
  - end screen
  - localization

- `src/audio_manager.py`
  - music routing
  - SFX playback
  - fail-safe audio handling

### Module phụ / legacy

- `src/entities.py`
- `src/hint_system.py`
- `src/ui.py`
- `src/utils.py`

## Ghi chú
- Project được tạo từ ngôn ngữ Python và PyGame
## License
MIT
