# Kết quả chạy trực tiếp trên UTC

Đích: <https://vanphongdientu.utc.edu.vn/Login>. Kết quả tổng hợp từ **8 đợt chạy**, từ **08/10/2026 16:17:33 UTC+7** đến **08/10/2026 17:10:19 UTC+7**, bằng Selenium 4.50.0, pytest 9.1.1 và Chrome 154.0.8037.98 headless.

## Kết quả nghiệm thu

[Mở báo cáo HTML](../reports/utc-live/report.html) · [JSON tổng hợp và nguồn từng dòng](../reports/utc-live/report.json).

| Trạng thái mới nhất | Số lượt |
| --- | --- |
| PASS | **23** |
| FAIL | **0** |
| SKIPPED | **0** |
| BLOCKED | **0** |

Có **22 ID TC01–TC22**; TC19 gồm hai biến thể thiếu Username/Password nên tổng 23 lượt. PASS nghĩa là luồng negative bị từ chối đúng oracle. Mỗi dòng lấy kết quả mới nhất của biến thể, ghi Run ID và thời điểm nguồn; đây không phải một lượt pytest duy nhất. Các đợt cục bộ không được tính vào kết quả UTC.

## Các điều kiện đã gỡ chặn

- TC05 dùng Username tồn tại do người dùng xác nhận và mật khẩu giả ngẫu nhiên. Dữ liệu tài khoản nằm riêng trong .env; báo cáo che giá trị đã cấu hình.
- TC07/TC08/TC12 đã được người dùng chấp thuận riêng trên production, gửi mỗi ca đúng một lần và PASS. TC12 xác nhận thực nhập đủ 256 ký tự. Các ca khác không gửi lại payload này.
- CAPTCHA xuất hiện ở lần sai thứ 3 trong các phiên khảo sát; từng ca CAPTCHA được chuẩn bị bằng tài khoản giả với giới hạn hữu hạn, dừng khi ô mã hiện. TC22 PASS với 3 lần sai và lần gửi thứ 4 thiếu mã.
- TC13/TC14/TC15/TC20 PASS với CAPTCHA đã hiển thị. Mã đúng cần thiết được người dùng nhập thủ công; bộ test không tự đọc ảnh.
- TC16 PASS sau khi xác nhận mã A/B khác nhau và gửi lại A sau refresh. Đã sửa chờ ảnh tải xong và thay đổi thực tế, tránh chụp ảnh cũ khi src vừa đổi.
- Người dùng xác nhận CAPTCHA không tự hết hạn. TC17 được cập nhật thành giữ nguyên mã 60 giây, sau đó gửi với thông tin sai và nhận lỗi tài khoản. Bằng chứng chỉ xác nhận khoảng quan sát 60 giây, không suy luận thực nghiệm về hiệu lực vô hạn.
- TC18 và cả hai biến thể TC19 PASS với mã thủ công đúng phiên.
- Người dùng xác nhận đăng nhập sai cấp CAPTCHA mới. TC21 PASS: A được chấp nhận ở lần đầu, phản hồi cấp B với đáp án khác, gửi lại A nhận lỗi CAPTCHA. Đã sửa lỗi tham chiếu DOM cũ và chờ thuộc tính field ổn định trước thao tác.

Các lượt bị chặn, lỗi đồng bộ và phiên chờ mã hết thời gian trước khi sửa vẫn giữ trong file nguồn bên dưới. Chỉ kết quả mới nhất của từng biến thể được dùng cho bảng nghiệm thu.

## Locator và oracle

Selector dùng thuộc tính name/type trong form, kiểm tra đúng một phần tử cùng placeholder trước khi thao tác:

```text
Form:     form[action='/Login'][method='post']
Username: form[action='/Login'][method='post'] input[name='username'][type='text']
Password: form[action='/Login'][method='post'] input[name='userpwd'][type='password']
CAPTCHA:  form[action='/Login'][method='post'] input[name='captcha'][type='text']
Submit:   form[action='/Login'][method='post'] > input.submit_login[type='submit']
Error:    form[action='/Login'][method='post'] > div.error
Image:    form[action='/Login'][method='post'] img#captcha
Refresh:  form[action='/Login'][method='post'] a[onclick*="getElementById('captcha')"]
```

Thông báo đã xác minh: `Bạn chưa nhập tên đăng nhập`, `Bạn chưa nhập mật khẩu`, `Tài khoản hoặc mật khẩu không đúng.`, `Mã bảo mật không đúng`. Trang mới có Username/Password ở vị trí 1/2; div.error làm chúng chuyển sang 2/3. Selector theo thuộc tính hoạt động xuyên các bố cục có/không CAPTCHA.

## Chạy lại

[README.md](../README.md) có lệnh chọn từng nhóm ca, nhận mã thủ công và kiểm tra activation/replay. Lệnh mặc định không mở payload production và có thể BLOCKED nếu chưa nhận mã hoặc chưa bật ca có điều kiện; điều này không thay đổi kết quả đã ghi của lần nghiệm thu. Mỗi lần chạy mới cần đáp án của challenge mới.

```powershell
# Ví dụ chạy ca thiếu mã, không cần người nhập đáp án:
.\.venv\Scripts\python.exe tools/run_utc.py --cases TC13 TC15 TC20 --prepare-captcha --html reports/utc-live/captcha-empty.html
```

## Bằng chứng và kiểm tra báo cáo

- [HTML độc lập với ảnh nhúng](../reports/utc-live/report.html).
- [JSON tổng hợp](../reports/utc-live/report.json).
- [Kiểm tra giao diện HTML](../reports/utc-live/html-verification.json).
- [Ảnh xem trước báo cáo](../reports/utc-live/report-preview.png).
- [JUnit XML đợt cuối — riêng TC21](../reports/utc-live/junit.xml). Báo cáo đủ 23 lượt là HTML/JSON tổng hợp.

Nguồn theo thứ tự kết thúc:

- [20261008T091733-68602f](../reports/utc-live/20261008T091733-68602f-results.json): {"PASS": 8, "BLOCKED": 12, "SKIPPED": 3}.
- [20261008T093142-750238](../reports/utc-live/20261008T093142-750238-results.json): {"PASS": 4}.
- [20261008T093854-1ad580](../reports/utc-live/20261008T093854-1ad580-results.json): {"PASS": 1}.
- [20261008T093629-df29e5](../reports/utc-live/20261008T093629-df29e5-results.json): {"PASS": 3, "BLOCKED": 1}.
- [20261008T094855-f88b52](../reports/utc-live/20261008T094855-f88b52-results.json): {"PASS": 5, "BLOCKED": 1}.
- [20261008T100022-dbd57f](../reports/utc-live/20261008T100022-dbd57f-results.json): {"PASS": 1, "FAIL": 1}.
- [20261008T100525-cc4e06](../reports/utc-live/20261008T100525-cc4e06-results.json): {"FAIL": 1}.
- [20261008T100716-9ec8e9](../reports/utc-live/20261008T100716-9ec8e9-results.json): {"PASS": 1}.

HTML được kiểm tra lại trên Chrome về 23 dòng, số lượng trạng thái, tìm kiếm/lọc, ảnh nhúng và lỗi trình duyệt. Báo cáo/screenshot nằm trong reports/ và bị Git ignore. Kiểm tra cục bộ riêng xác minh chờ ảnh tải trễ, placeholder ổn định, bỏ qua DOM cũ tạm thời và vẫn từ chối thông báo sai oracle.
