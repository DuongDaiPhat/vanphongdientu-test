# Báo cáo triển khai và kiểm chứng

Ngày: **08/10/2026**, múi giờ người dùng Asia/Bangkok. Timestamp của các báo cáo máy đọc dùng UTC.

## Kết quả triển khai

- Đã đánh lại ID liên tiếp **TC01–TC22**, đồng bộ bảng yêu cầu, plan, tên test và tham chiếu.
- Đã xây dựng Python Selenium theo cấu trúc `src/test/python/e2e/base`, `pages`, `tests`; có cấu hình, browser fixture, explicit wait, Page Objects và báo cáo JSON/Markdown/JUnit.
- Đã thêm mã thực thi cho cả 22 testcase; TC19 có hai biến thể nên pytest thu thập **23 lượt**.
- Đã dùng hai bộ locator đúng theo cập nhật của người dùng: không CAPTCHA là (2, 3); có CAPTCHA là (6, 7), ô CAPTCHA ở vị trí 5. Chọn lại theo DOM hiện tại trước khi nhập/submit.
- Có **22 commit testcase riêng** bằng tiếng Anh, từ `test(login): add TC01 ...` đến `test(captcha): add TC22 ...`. Nhánh: `codex/login-negative-tests`; commit tài liệu/hạ tầng và sửa fixture tách riêng.
- Có hướng dẫn cài đặt/chạy trong [README](../README.md), công cụ kiểm tra DOM chỉ đọc và môi trường tham chiếu cục bộ. `docs/` được Git theo dõi.

## Môi trường đã dùng

Windows, Python **3.14.0**, Selenium **4.50.0**, pytest **9.1.1**, Chrome **154.0.8037.98**, chế độ headless. `pip check` không phát hiện dependency hỏng. Cài đặt nằm trong `.venv`, không thay dependency Python toàn hệ thống.

## Kết quả kiểm tra

| Lần kiểm tra | Kết quả | Ý nghĩa |
| --- | --- | --- |
| Thu thập / truy vết | 22 ID, 22 hàm test, 23 lượt; 22 commit testcase | Bảng, mã và lịch sử khớp nhau. |
| Từng testcase trên form tham chiếu | Tất cả đạt trước khi commit | Mỗi ID đã được thực thi, không phải hàm skip cố định. |
| Bộ đầy đủ trên form tham chiếu | **23 PASS** | Selenium thao tác browser thật với DOM và validation thử nghiệm. |
| Cố ý bỏ kiểm tra CAPTCHA | **1 FAIL như mong đợi** ở TC13 | Assertion phát hiện lỗi bảo vệ, không PASS chỉ vì tài khoản sai. |
| Cố ý hiển thị nội dung đã xác thực | **1 FAIL như mong đợi** ở TC04 | Assertion phát hiện trạng thái xác thực trái yêu cầu. |
| Cố ý trả lỗi không đúng loại | **1 FAIL như mong đợi** ở TC04 | Không chấp nhận thông báo bất kỳ làm bằng chứng từ chối. |
| Reset khi CAPTCHA đã hiện trước reset | **1 PASS** ở TC22 | Fixture cho phép thiết lập lại tiền điều kiện; sau reset xác minh ngưỡng và giới hạn số submit. |
| Kiểm tra locator trên UTC, chỉ đọc | **2 FAIL locator**, CAPTCHA **SKIPPED** | Phiên mới không CAPTCHA; cả Username (2) và Password (3) khớp 0 phần tử. |
| Kiểm tra điều kiện toàn bộ suite với cấu hình UTC mặc định | **23 BLOCKED** | Chưa có oracle, dữ liệu hoặc điều kiện môi trường; chưa submit đăng nhập. |

**23 PASS cục bộ chỉ xác minh mã automation. Chưa có testcase được xác minh PASS trên UTC.** Lượt mặc định trả exit code 0 của pytest do không có test FAIL, nhưng báo cáo chi tiết ghi 23 BLOCKED; đây không phải kết luận hệ thống UTC đạt yêu cầu.

Form tham chiếu chỉ mở trên `127.0.0.1`, có hai bố cục DOM, mã tổng hợp, refresh, hết hạn, chống replay và ngưỡng kích hoạt. Kết quả không được dùng để suy diễn hành vi thực tế của UTC hoặc độ an toàn toàn hệ thống.

## Bằng chứng tại workspace

Các file trong `reports/` bị Git ignore; có thể tái tạo bằng lệnh trong README:

- [Kết quả bộ cục bộ](../reports/20261008T090215-849d95-results.json), [JUnit cục bộ](../reports/reference.xml).
- [Điều kiện chạy UTC](../reports/20261008T090357-3e2ef6-results.json), [JUnit UTC preflight](../reports/utc-preflight.xml).
- [Phát hiện bỏ CAPTCHA](../reports/20261008T090359-2a7493-results.json).
- [Phát hiện vượt xác thực](../reports/20261008T090416-188f30-results.json).
- [Phát hiện sai thông báo](../reports/20261008T090424-0807f7-results.json).
- [TC22 với CAPTCHA trước reset](../reports/20261008T090427-0714c6-results.json).
- [Kết quả kiểm tra locator UTC](../reports/locator-probe.json), [Ảnh trang UTC](../reports/locator-probe.png).

## Phần còn cần để xác minh trên UTC

1. Đối chiếu DOM trong **phiên mới** với hai bộ CSS đã chỉ định. Hiện bộ không CAPTCHA không khớp; không tự thay bằng selector khác hoặc tạo một lần submit ngầm để đổi bố cục.
2. Sau khi locator đúng, khảo sát và cấu hình selector vùng lỗi cùng thông báo/regex validation, xác thực, CAPTCHA. Không lấy lỗi tiếng Anh của form tham chiếu làm oracle UTC.
3. TC05 cần Username thực sự tồn tại và mật khẩu được xác nhận sai. Ca cần mã CAPTCHA đúng phải có người hỗ trợ hoặc cơ chế test chính thức.
4. Xác nhận ảnh/challenge, refresh, TTL, chính sách mã dùng một lần và ngưỡng N. TC22 cần cơ chế reset trên môi trường thử nghiệm cùng giới hạn số submit.
5. Chỉ mở nhóm `test_env_only` trên hostname thử nghiệm đã cấu hình, sau đó chạy từng nhóm đủ điều kiện và cập nhật kết quả. Không chạy payload bảo mật hoặc cố ép ngưỡng CAPTCHA trên UTC production.

Mốc xây dựng dự án kiểm thử đã hoàn tất; mốc xác minh đủ 22 testcase trên UTC còn bị chặn bởi các điều kiện trên.
