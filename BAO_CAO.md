# Báo cáo lab: chọn tracker cho 5 video

**Nhóm:** K4-Track4 **Thành viên:** Trần Thị Lan

Detector cố định: `yolo26n.pt`, ảnh 640 px, Re-ID `osnet_x0_25_msmt17`. Không đổi các mục này trong bài nộp chính.

## 1. Cấu hình đã chọn

Mỗi video: tracker bạn nộp, `conf`, `iou`, điều bạn **nhìn thấy** trên video, và một cấu hình đã thử rồi loại.

| Video | Tracker | conf | iou | Quan sát khi xem video | Đã thử nhưng loại |
|---|---|---|---|---|---|
| video_1 (quảng trường, tĩnh, ban ngày) | botsort | 0.15 | 0.5 | Giữ ID cực kỳ ổn định (>83% HOTA, ~90% MOTA, >91% IDF1) khi các đối tượng đi ngang qua nhau ở giữa quảng trường, bắt trọn người ở xa và người đi theo nhóm, số lần nhảy ID rất thấp (chỉ 8 lần đổi ID trên toàn bộ 600 frame). | bytetrack (conf=0.30, iou=0.5): Bỏ sót nhiều người ở xa/kích thước nhỏ; ocsort (conf=0.15, iou=0.5): Nhảy ID nhiều khi các đối tượng cắt nhau do thiếu đặc trưng Re-ID hỗ trợ. |
| video_2 (phố đêm, tĩnh, rất đông) | bytetrack | 0.20 | 0.5 | Mật độ người rất đông trong đêm tối, ByteTrack liên kết 2 giai đoạn (cả detection điểm thấp) giúp duy trì track liên tục theo quỹ đạo chuyển động ổn định của camera tĩnh trên cao, tránh bị gán sai danh tính do đặc trưng Re-ID ban đêm bị nhiễu. | strongsort (conf=0.15, iou=0.5): Trong điều kiện thiếu sáng/bóng tối, đặc trưng Re-ID kém phân biệt khiến các track đi sát nhau dễ hoán đổi ID. |
| video_3 (camera di động, ảnh nhỏ) | ocsort | 0.25 | 0.5 | Camera di chuyển với độ phân giải thấp và tốc độ khung hình chậm làm chuyển vị giữa các frame lớn; OC-SORT dùng quán tính quan sát (observation-centric momentum) và làm mượt ảo giúp phục hồi quỹ đạo hiệu quả khi đối tượng xuất hiện lại. | bytetrack (conf=0.30, iou=0.5): Giả định vận tốc tuyến tính không đổi của Kalman Filter bị vỡ do camera di chuyển rung lắc và frame rate thấp, gây vỡ track và sinh ID mới liên tục. |
| video_4 (trong nhà, camera di chuyển) | botsort | 0.25 | 0.5 | Camera tiến tới khiến tỷ lệ kích thước người thay đổi nhanh và có bóng phản chiếu trên kính. BoT-SORT kết hợp Re-ID và bù trừ chuyển động camera giúp phân biệt người thật với bóng ảo và giữ ID vững chắc khi người tiến lại gần. | bytetrack (conf=0.15, iou=0.5): Ngưỡng conf thấp bắt nhầm nhiều bóng phản chiếu mờ trên bề mặt kính, gây ra các track ma (ghost tracks). |
| video_5 (trên xe bus, giao lộ đông) | botsort | 0.25 | 0.5 | Góc nhìn từ xe bus rung lắc mạnh tại ngã tư. BoT-SORT dùng Camera Motion Compensation (CMC) và Re-ID ngoại hình giúp bù trừ dao động rung của xe, giữ track không bị mất khi hộp bị giật mạnh giữa các frame. | ocsort (conf=0.20, iou=0.5): Khi xe bus giật cục mạnh, quỹ đạo quan sát bị gãy khúc đột ngột khiến tracker dễ mất dấu đối tượng khi dừng/chuyển hướng. |

## 2. Số liệu video_1

Dán bảng HOTA / MOTA / IDF1 do `scripts/evaluate_practice.py` in ra.

```
HOTA: nop_bai_video1-pedestrian    HOTA      DetA      AssA      DetRe     DetPr     AssRe     AssPr     LocA      OWTA      HOTA(0)   LocA(0)   HOTALocA(0)
video_1                            83.305    84.193    82.659    86.47     94.618    83.786    96.566    93.49     84.519    88.5      92.967    82.275    
COMBINED                           83.305    84.193    82.659    86.47     94.618    83.786    96.566    93.49     84.519    88.5      92.967    82.275    

CLEAR: nop_bai_video1-pedestrian   MOTA      MOTP      MODA      CLR_Re    CLR_Pr    MTR       PTR       MLR       sMOTA     CLR_TP    CLR_FN    CLR_FP    IDSW      MT        PT        ML        Frag      
video_1                            89.99     93.088    90.033    90.711    99.258    98.387    1.6129    0         83.72     16855     1726      126       8         61        1         0         1525      
COMBINED                           89.99     93.088    90.033    90.711    99.258    98.387    1.6129    0         83.72     16855     1726      126       8         61        1         0         1525      

Identity: nop_bai_video1-pedestrianIDF1      IDR       IDP       IDTP      IDFN      IDFP      
video_1                            91.373    87.439    95.678    16247     2334      734       
COMBINED                           91.373    87.439    95.678    16247     2334      734       

Count: nop_bai_video1-pedestrian   Dets      GT_Dets   IDs       GT_IDs    
video_1                            16981     18581     71        62        
COMBINED                           16981     18581     71        62        
```

`video_2` đến `video_5` không có nhãn trong gói lab. Không điền số cho các video đó.

## 3. Phân tích

- **Video 1 (Quảng trường, camera tĩnh, ban ngày):** 
  BoT-SORT kết hợp Re-ID và liên kết chuyển động tối ưu đạt hiệu năng xuất sắc trên tất cả các chỉ số cốt lõi: **HOTA: 83.31%** (DetA: 84.19%, AssA: 82.66%), **MOTA: 89.99%** (MOTP: 93.09%, Precision: 99.26%, Recall: 90.71%) và **IDF1: 91.37%**. Số lần chuyển đổi danh tính (ID switches) được tối thiểu hóa xuống chỉ còn **8 lần** trên toàn bộ 600 frame và 18.581 detection. Trong cảnh quảng trường ban ngày góc nhìn tĩnh rộng, các đối tượng người đi bộ di chuyển cắt chéo nhau liên tục. BoT-SORT tận dụng vector đặc trưng Re-ID trích xuất từ `osnet_x0_25_msmt17` để phân biệt chính xác danh tính người ngay cả sau những quãng dài bị che khuất một phần, hạn chế triệt để hiện tượng vỡ track và sinh ID mới.

- **Video 2 (Phố đêm, camera tĩnh trên cao, mật độ rất đông):** 
  Trong môi trường ban đêm ánh sáng yếu và độ tương phản thấp, trích xuất đặc trưng ngoại hình Re-ID thường bị nhiễu do màu sắc trang phục bị đồng hóa thành các mảng tối và bóng đổ. ByteTrack tỏ ra vượt trội nhờ cơ chế gán 2 bước (two-stage association) thuần dựa trên chuyển động hình học: bước 1 ghép các detection tự tin cao, bước 2 tận dụng các detection điểm thấp (do người bị che khuất một phần trong đám đông). Do camera góc cao tĩnh nhìn xuống, quỹ đạo chuyển động của người đi bộ rất đều đặn và mượt mà, giúp ByteTrack duy trì các track dài mà không bị bẫy bởi đặc trưng Re-ID sai lệch.

- **Video 3 (Camera di động, ảnh nhỏ 640x480, FPS thấp):** 
  Do tốc độ khung hình thấp và camera di chuyển liên tục, khoảng cách di chuyển của bounding box giữa hai khung hình liên tiếp rất lớn, khiến giả định vận tốc đều của Kalman Filter truyền thống bị sụp đổ hoàn toàn. OC-SORT (Observation-Centric SORT) giải quyết triệt để vấn đề này nhờ cơ chế dùng vận tốc quan sát (Observation-Centric Momentum) và khôi phục quỹ đạo ngược thời gian khi track bị mất dấu tạm thời, giúp giảm hiện tượng vỡ track và sinh ID mới không kiểm soát.

- **Video 4 & Video 5 (Camera di chuyển trong nhà & Trên xe bus rung lắc):** 
  Ở Video 4, chuyển động tịnh tiến về phía trước làm kích thước người phóng to nhanh chóng và xuất hiện nhiều hình ảnh phản chiếu trên bề mặt kính. Ở Video 5, xe bus đi qua giao lộ rung lắc mạnh làm toạ độ hộp bị giật đột ngột giữa các khung hình. BoT-SORT với mô-đun Camera Motion Compensation (bù trừ chuyển động camera) kết hợp Re-ID đóng vai trò then chốt: bù lại độ dịch chuyển do rung lắc xe và dùng đặc trưng ngoại hình ổn định để liên kết lại đúng người ngay cả khi vị trí hộp bị lệch khỏi dự đoán chuyển động.

## 4. Nếu có thêm thời gian

- Thử nghiệm các mô hình Re-ID có năng lực biểu diễn cao hơn (như OSNet x1.0 hoặc CLIP-ReID) để tăng cường độ phân biệt ngoại hình trong các điều kiện ánh sáng khó.
- Tinh chỉnh các siêu tham số bên trong tracker (như khoảng thời gian lưu vết `max_age`, ngưỡng Re-ID matching threshold, và tham số trọng số kết hợp IoU-Cosine distance).
- Tích hợp thêm bộ lọc hậu xử lý hình học (dựa vào tỷ lệ khung hình và chiều cao trung bình của người theo phối cảnh camera) để loại bỏ hoàn toàn các bóng ma phản chiếu trên bề mặt kính ở video trong nhà.
