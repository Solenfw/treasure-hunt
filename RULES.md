# 🏴‍☠️ GAME DESIGN DOCUMENT: Treasure Hunt (Truy Tìm Kho Báu)

## 1. Overview (Tổng quan)
- **Game name:** Treasure Hunt (Truy Tìm Kho Báu)
- **Genre:** Puzzle, Competitive Racing, Strategy.
- **Introduction:** Treasure Hunt là một trò chơi phiêu lưu - giải đố mang tính cạnh tranh cao. Điểm đặc biệt của game là người chơi không đối đầu trực tiếp trên cùng một bản đồ, mà sẽ chạy đua trên hai bản đồ riêng biệt nhưng đối xứng và có độ khó tương đương nhau. Nhiệm vụ của người chơi là vận dụng tư duy logic để giải mã chuỗi các "Gợi ý" (Hints) ẩn dưới lòng đất nhằm tìm ra Kho báu cuối cùng. Song song đó, người chơi phải cẩn thận tránh né các quả Bom chết người và khéo léo sử dụng các Kỹ năng đặc biệt (Skills) để quấy rối tiến độ của đối thủ. Ai chạm tay vào Kho báu trước sẽ là người chiến thắng.

## 2. Rules (Luật chơi cốt lõi)

### Cơ chế gameplay chung:
- **Thời gian:** Mỗi ván đấu diễn ra tối đa 2 phút.
- **Sinh mạng (Hearts):** Mỗi người chơi bắt đầu với 2 Trái tim. Nếu số tim về 0, người chơi lập tức thua cuộc (Game Over).

### Chuỗi gợi ý (The Hint Chain):
Trên bản đồ 20x20, tất cả mọi thứ đều bị chôn vùi (ẩn đi), ngoại trừ Gợi ý số 1.
1. Khi người chơi đến và giải mã Gợi ý 1, nó sẽ cung cấp manh mối (tọa độ, phương hướng, hoặc câu đố logic) để tìm Gợi ý 2.
2. Gợi ý 2 sẽ dẫn đến Gợi ý 3, và cứ thế cho đến khi chỉ ra vị trí của Kho báu.
*(Lưu ý: Cơ chế game sẽ điều phối để người chơi chỉ tìm được kho báu theo trình tự, không có chuyện “đào bừa” hoặc “ăn may”)*

### Cơ chế Đào bới (Digging) & Rủi ro:
Dựa vào manh mối, người chơi di chuyển đến ô tình nghi và thực hiện lệnh "Đào":
- **Đào trúng Gợi ý/Kho báu:** Mở khóa mục tiêu tiếp theo.
- **Đào trúng Đất trống (Sai vị trí):** Không mất máu, nhưng nhân vật bị choáng/mất thời gian đào đất khoảng 2-3 giây (Hình phạt thời gian).
- **Đào trúng Bom:** Mất 1 Trái tim (-1 Heart) và bị choáng. Bom được đặt ẩn xung quanh các khu vực Gợi ý/Kho báu để trừng phạt suy luận sai.

### Điều kiện Thắng/Thua:
- **Thắng:** Tìm thấy Kho báu đầu tiên, hoặc đối thủ đạp trúng Bom mất hết tim.
- **Hòa:** Nếu hết 2 phút chưa ai tìm ra Kho báu.

### Các chế độ chơi (Game Modes):
1. **Player vs Player (PvP):** Hai người chơi thi đấu song song. Có thể nhặt "Vật phẩm kỹ năng" tác động chéo (Cross-map Sabotage) như: đóng băng 3 giây, làm mù bản đồ, thêm gợi ý. Có thanh Tiến trình (Progress Bar) báo hiệu tiến độ đối thủ.
2. **Player vs Computer (PvE):** Đấu với AI (Easy, Normal, Hard). AI mô phỏng việc giải đố và di chuyển theo tốc độ lập trình sẵn.
3. **Computer vs Computer (EvE - Spectator):** 2 Bot tự động thi đấu. Người chơi làm trọng tài, xem logic giải đố, có thể tua nhanh/chậm.

## 3. Controls & Interface (Điều khiển & Giao diện)

### Hệ thống điều khiển:
- `W / A / S / D`: Di chuyển nhân vật từng ô (Grid 20x20).
- `Space`: Tương tác / Đào bới tại ô đang đứng.
- `E`: Kích hoạt Vật phẩm kỹ năng (Sabotage Skill).

### Giao diện người dùng (UI / HUD):
- **Bản đồ 20x20:** Bề mặt ô đất (kết hợp Fog of War cho vùng chưa qua).
- **HUD Cá nhân:**
  - *Góc trên cùng:* Đồng hồ đếm ngược (2:00), Sinh mạng (2 Hearts).
  - *Clue UI:* Nội dung Gợi ý gần nhất (VD: *"Gợi ý tiếp theo cách đây 4 bước về hướng Bắc"*).
  - *Tension UI:* Thanh Tiến trình trạng thái đối thủ (VD: *"Đối thủ đã tìm thấy Gợi ý 2!"*).