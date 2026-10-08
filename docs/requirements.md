# Yêu cầu kiểm thử chức năng đăng nhập

## 1. Mục tiêu và phạm vi

Tạo Selenium Project tự động kiểm thử đăng nhập thất bại tại <https://vanphongdientu.utc.edu.vn/Login>.

- Chưa có tài khoản/mật khẩu hợp lệ. Chỉ thực thi luồng đăng nhập bị từ chối hoặc dữ liệu bị validation chặn.
- “Testcase fail” được hiểu là **negative testcase**: bài test PASS khi ứng dụng từ chối đúng, không phải cố tình làm bài test thất bại.
- Phạm vi gồm ba trường Username, Password, CAPTCHA và thao tác submit form. CAPTCHA là ô nhập mã dạng text theo HTML người dùng cung cấp; chưa xác nhận ngưỡng kích hoạt, thời hạn và thông báo lỗi.
- Chỉ giữ negative testcase thuộc ba trường trên. ID được đánh lại liên tiếp TC01–TC22 theo thứ tự bảng; bảng hiện có 22 ca, gồm 10 ca CAPTCHA.
- Mỗi testcase được triển khai trong một commit riêng, dùng Conventional Commits bằng tiếng Anh, ví dụ `test(login): add TC01 empty credentials validation`.
- Không dò mật khẩu hoặc lặp request vô hạn để ép CAPTCHA xuất hiện. Ca payload bảo mật và kích hoạt CAPTCHA theo ngưỡng chỉ chạy trong môi trường thử nghiệm được cho phép.

## 2. Căn cứ, dữ liệu và oracle

Locator và HTML của ba trường dưới đây do người dùng cung cấp trong lần cập nhật ngày 08/10/2026. Chưa chạy Selenium để xác minh selector, submit hoặc thông báo lỗi thực tế.

### Quy ước dữ liệu

| Ký hiệu | Ý nghĩa |
| --- | --- |
| `U_BAD` | Tài khoản giả dành cho kiểm thử, ví dụ `qa_invalid_<run_id>`; xác nhận chưa được cấp phát khi có môi trường thử nghiệm. Không dùng tài khoản người thật. |
| `P_BAD` | Mật khẩu giả `InvalidPass_123!`, không phải thông tin xác thực thực. |
| `U_VALID` | Username được xác nhận tồn tại; hiện chưa có. |
| `C_WRONG` | Đáp án được xác nhận sai với challenge hiện tại, không chỉ một chuỗi đoán ngẫu nhiên. |
| `C_VALID` | Mã CAPTCHA hợp lệ lấy thủ công hoặc qua cơ chế test chính thức trong môi trường được phép; không bypass CAPTCHA. |

Mỗi ca bắt đầu bằng phiên trình duyệt mới, mở `/Login`, chờ form sẵn sàng và kiểm tra tiền điều kiện CAPTCHA. Không dùng trạng thái của ca trước để tạo tiền điều kiện ngầm cho ca sau.

### Oracle kiểm thử

- **O1 — Từ chối xác thực:** có lỗi/validation tương ứng; form đăng nhập vẫn hiển thị hoặc quay lại trang đăng nhập; không xuất hiện dấu hiệu đã xác thực được xác minh khi khảo sát. Không kết luận chỉ từ URL hoặc HTTP 200.
- **O2 — Validation:** có lỗi trình duyệt hoặc ứng dụng cho trường bắt buộc thiếu. Không mặc định ứng dụng phải chặn request phía client; không yêu cầu nguyên văn câu lỗi chưa được xác minh.
- **O3 — CAPTCHA:** có tín hiệu challenge chưa hoàn tất hoặc lỗi CAPTCHA tương ứng; vẫn chưa xác thực. “Sai tài khoản” đơn thuần không chứng minh CAPTCHA hoạt động.
- Chốt locator, nội dung lỗi và dấu hiệu xác thực trước khi triển khai assertion. Thiếu oracle thì BLOCKED, không nới assertion chỉ để PASS.
- CAPTCHA không xuất hiện: ca yêu cầu CAPTCHA là SKIPPED vì không áp dụng trong phiên. CAPTCHA có nhưng thiếu dữ liệu/đặc tả/cơ chế thử: BLOCKED. Nếu pytest biểu diễn cả hai bằng skip, báo cáo phải giữ riêng phân loại và lý do.
- PASS/FAIL chỉ ghi sau thực thi. Trạng thái trong bảng là trạng thái lập kế hoạch.

## 3. Locator do người dùng cung cấp

Dùng nguyên CSS selector dưới đây với Selenium `By.CSS_SELECTOR`. HTML ghi nhận đúng theo dữ liệu người dùng cung cấp, chưa phải kết quả chạy kiểm chứng.

| Trạng thái | Trường | CSS selector | Element |
| --- | --- | --- | --- |
| Không có CAPTCHA | Username | `body > div > div.main > div.right > div.form > form > input[type=text]:nth-child(2)` | `<input placeholder="Tên đăng nhập" type="text" name="username">` |
| Không có CAPTCHA | Password | `body > div > div.main > div.right > div.form > form > input[type=password]:nth-child(3)` | `<input placeholder="Mật khẩu" type="password" name="userpwd">` |
| Có CAPTCHA | Username | `body > div > div.main > div.right > div.form > form > input[type=text]:nth-child(6)` | `<input placeholder="Tên đăng nhập" type="text" name="username">` |
| Có CAPTCHA | Password | `body > div > div.main > div.right > div.form > form > input[type=password]:nth-child(7)` | `<input placeholder="Mật khẩu" type="password" name="userpwd">` |
| Có CAPTCHA | CAPTCHA | `body > div > div.main > div.right > div.form > form > input[type=text]:nth-child(5)` | `<input placeholder="Mã bảo mật" type="text" name="captcha">` |

Khi triển khai, kiểm tra mỗi selector khớp duy nhất một phần tử và đúng `name`, `type`, `placeholder` mong đợi trước khi nhập. `nth-child` tính vị trí trong toàn bộ phần tử con; cần kiểm tra ở cả trạng thái CAPTCHA hiện và ẩn. Chọn cặp (2, 3) khi CAPTCHA không hiển thị và (6, 7) khi CAPTCHA hiển thị; chọn lại sau mỗi phản hồi submit/refresh. Nếu selector theo trạng thái không khớp, báo lỗi locator, không nhập vào ô khác hoặc tự dùng selector ngoài hai bộ đã cung cấp.

Locator hỗ trợ thao tác submit và quan sát kết quả:

| Thành phần | Locator / trạng thái | Ghi chú |
| --- | --- | --- |
| Submit | `input.submit_login[type='submit']` | Từ tài liệu trước, chưa xác minh; chỉ dùng để submit ba trường trong phạm vi. |
| Lỗi validation/xác thực/CAPTCHA | Chưa xác định | Khảo sát trước khi viết assertion. |
| Ảnh/challenge CAPTCHA và refresh | Chưa xác định | Chỉ áp dụng ca refresh/vòng đời khi chức năng thực tế có hỗ trợ. |
| Dấu hiệu đã xác thực | Chưa xác định | Cần đặc tả hoặc xác nhận từ quản trị. |

## 4. Bảng Testcase

| ID | Nhóm kiểm thử / kỹ thuật | Tiền điều kiện / phạm vi | Các bước thực hiện (Steps) | Dữ liệu kiểm thử (Test Data) | Kết quả mong đợi (Expected Result) | Trạng thái kế hoạch |
| --- | --- | --- | --- | --- | --- | --- |
| TC01 | Validation Negative / Phân vùng tương đương | CAPTCHA ẩn. | 1. Để trống hai trường.<br>2. Bấm Đăng nhập. | Username: rỗng.<br>Password: rỗng. | O1 + O2: yêu cầu bổ sung thông tin bắt buộc. | Cần chốt oracle |
| TC02 | Validation Negative / Phân vùng tương đương | CAPTCHA ẩn. | 1. Để trống Username.<br>2. Nhập Password.<br>3. Bấm Đăng nhập. | Username: rỗng.<br>Password: `P_BAD`. | O1 + O2: validation cho Username thiếu. | Cần chốt oracle |
| TC03 | Validation Negative / Phân vùng tương đương | CAPTCHA ẩn. | 1. Nhập Username.<br>2. Để trống Password.<br>3. Bấm Đăng nhập. | Username: `U_BAD`.<br>Password: rỗng. | O1 + O2: validation cho Password thiếu. | Cần chốt oracle |
| TC04 | Functional Negative / Phân vùng tương đương | CAPTCHA ẩn; dữ liệu tài khoản không hợp lệ. | 1. Nhập thông tin sai.<br>2. Bấm Đăng nhập. | Username: `U_BAD`.<br>Password: `P_BAD`. | O1: lỗi xác thực và không đăng nhập. Không PASS chỉ vì form còn hiển thị. | Cần chốt oracle |
| TC05 | Functional Negative / Bảng quyết định | CAPTCHA ẩn; Username được xác nhận tồn tại. | 1. Nhập Username tồn tại.<br>2. Nhập mật khẩu sai.<br>3. Submit. | Username: `U_VALID`.<br>Password: được xác nhận sai. | O1: từ chối xác thực. Không thay `U_VALID` bằng tên giả rồi coi đã kiểm thử “đúng user, sai password”. | BLOCKED — thiếu dữ liệu |
| TC06 | Format Negative / Phân vùng tương đương | CAPTCHA ẩn; dùng thông tin đăng nhập sai. | 1. Nhập Username có khoảng trắng đầu/cuối.<br>2. Nhập mật khẩu giả.<br>3. Submit. | Username: `  qa_invalid_<run_id>  `.<br>Password: `P_BAD`. | O1: lỗi xác thực hoặc định dạng theo đặc tả đã chốt. Ca này không chứng minh chức năng trim. | Cần chốt oracle |
| TC07 | Security Negative / Error guessing | Chỉ môi trường thử nghiệm được phép; CAPTCHA ẩn. | 1. Nhập payload vào hai trường.<br>2. Submit một lần.<br>3. Quan sát phản hồi. | Username và Password: `' OR '1'='1`. | O1: không vượt xác thực, không lộ lỗi SQL/stack trace. Kết quả chỉ áp dụng payload này, không chứng minh toàn hệ thống an toàn SQL injection. | BLOCKED — cần môi trường |
| TC08 | Security Negative / Error guessing | Chỉ môi trường thử nghiệm được phép; CAPTCHA ẩn. | 1. Nhập payload Username và mật khẩu giả.<br>2. Submit.<br>3. Theo dõi alert và nội dung phản hồi. | Username: `<script>alert('qa_xss')</script>`.<br>Password: `P_BAD`. | O1: không vượt xác thực; payload không thực thi trong phản hồi quan sát được, không có alert `qa_xss`. Không kết luận về mọi dạng XSS. | BLOCKED — cần môi trường |
| TC09 | Keyboard Negative / So sánh cách submit | CAPTCHA ẩn; dùng dữ liệu sai. | 1. Nhập thông tin sai.<br>2. Tại ô Password, nhấn Enter.<br>3. Đối chiếu TC04. | Username: `U_BAD`.<br>Password: `P_BAD`. | O1: Enter submit và bị từ chối tương đương bấm nút. Phải có tín hiệu submit/lỗi, không PASS chỉ vì còn ở Login. | Cần chốt oracle |
| TC10 | Validation Negative / Phân vùng tương đương | CAPTCHA ẩn; chốt chính sách Username chỉ chứa dấu cách. | 1. Nhập Username ba dấu cách.<br>2. Nhập Password giả.<br>3. Submit. | Username: `   `.<br>Password: `P_BAD`. | O1; nếu đặc tả trim trước validation thì O2 cho Username rỗng, nếu không thì lỗi định dạng/xác thực. Chốt một oracle cụ thể trước triển khai. | Cần chốt oracle |
| TC11 | Validation Negative / Phân vùng tương đương | CAPTCHA ẩn; không mặc định Password được trim. | 1. Nhập Username giả.<br>2. Nhập Password ba dấu cách.<br>3. Submit. | Username: `U_BAD`.<br>Password: `   `. | O1: validation hoặc lỗi xác thực theo chính sách Password đã xác minh. Chốt oracle trước triển khai. | Cần chốt oracle |
| TC12 | Robustness Negative / Error guessing | Môi trường thử nghiệm được phép; CAPTCHA ẩn; chưa có giới hạn độ dài. | 1. Nhập Username dài và Password giả.<br>2. Ghi nhận giá trị thực sau maxlength nếu có.<br>3. Submit. | Username: `a` lặp 256 lần.<br>Password: `P_BAD`. | O1 hoặc validation độ dài theo đặc tả; không có trang lỗi máy chủ/stack trace. Báo đúng độ dài thực đã kiểm thử. Đây chưa phải giá trị biên chính thức. | BLOCKED — cần môi trường và oracle |
| TC13 | CAPTCHA Negative / Bảng quyết định | CAPTCHA hiện; xác định được validation CAPTCHA. | 1. Nhập thông tin sai.<br>2. Để ô CAPTCHA rỗng.<br>3. Submit. | Username: `U_BAD`.<br>Password: `P_BAD`.<br>CAPTCHA: rỗng. | O1 + O3: yêu cầu hoàn tất CAPTCHA, không bỏ qua challenge. | Có điều kiện — khảo sát CAPTCHA |
| TC14 | CAPTCHA Negative / Phân vùng tương đương | CAPTCHA dạng nhập mã; có đáp án chắc chắn sai. | 1. Nhập thông tin sai.<br>2. Nhập CAPTCHA sai.<br>3. Submit. | Username: `U_BAD`.<br>Password: `P_BAD`.<br>CAPTCHA: `C_WRONG`. | O1 + O3: CAPTCHA không hợp lệ, không xác thực. | Có điều kiện — cần `C_WRONG` |
| TC15 | CAPTCHA Negative / Phân vùng tương đương | CAPTCHA dạng mã; chính sách dấu cách đã xác minh. | 1. Nhập thông tin sai.<br>2. Nhập CAPTCHA ba dấu cách.<br>3. Submit. | Username: `U_BAD`.<br>Password: `P_BAD`.<br>CAPTCHA: `   `. | O1 + O3: CAPTCHA thiếu/không hợp lệ theo đặc tả đã chốt. | Có điều kiện — CAPTCHA dạng mã |
| TC16 | CAPTCHA Negative / Chuyển trạng thái | Có refresh; có đáp án hợp lệ của challenge A. | 1. Lấy đáp án A theo cơ chế được phép.<br>2. Refresh sang B, xác nhận challenge đổi.<br>3. Gửi đáp án A với thông tin sai. | Username: `U_BAD`.<br>Password: `P_BAD`.<br>CAPTCHA: đáp án cũ A. | O1 + O3: challenge A bị thay thế không còn được chấp nhận. Nếu đáp án trùng B hoặc không chứng minh challenge đổi thì BLOCKED. | Có điều kiện — cần hai challenge phân biệt |
| TC17 | CAPTCHA Negative / Chuyển trạng thái | Có TTL đã xác nhận; biết thời điểm cấp/hết hạn và đáp án hợp lệ. | 1. Lấy challenge/đáp án hợp lệ.<br>2. Chờ quá TTL với khoảng đệm.<br>3. Gửi đáp án cũ cùng thông tin sai. | Username: `U_BAD`.<br>Password: `P_BAD`.<br>CAPTCHA: mã CAPTCHA hết hạn. | O1 + O3: từ chối hết hạn hoặc yêu cầu challenge mới. Không dùng thời gian chờ tùy ý để chứng minh hết hạn. | BLOCKED — thiếu TTL/dữ liệu |
| TC18 | CAPTCHA + Authentication Negative / Bảng quyết định | CAPTCHA hiện; có `C_VALID` bằng cơ chế được phép. | 1. Nhập thông tin sai.<br>2. Hoàn tất CAPTCHA đúng.<br>3. Submit. | Username: `U_BAD`.<br>Password: `P_BAD`.<br>CAPTCHA: `C_VALID`. | O1: CAPTCHA được chấp nhận nhưng tài khoản sai vẫn bị từ chối. Phân biệt lỗi xác thực và lỗi CAPTCHA, không coi mọi lỗi là PASS. | BLOCKED — thiếu `C_VALID` |
| TC19 | CAPTCHA + Validation Negative / Bảng quyết định | CAPTCHA hiện; có `C_VALID` riêng mỗi biến thể. | 1. Để trống Username, nhập Password giả, hoàn tất CAPTCHA và submit.<br>2. Trong phiên/challenge mới: nhập Username giả, để Password trống, hoàn tất CAPTCHA và submit. | A: Username rỗng, Password `P_BAD`.<br>B: Username `U_BAD`, Password rỗng.<br>CAPTCHA: hợp lệ mỗi biến thể. | O1 + O2 cho trường thiếu. CAPTCHA đúng không thay thế thông tin bắt buộc; không tái dùng mã đã tiêu thụ. | BLOCKED — thiếu `C_VALID` |
| TC20 | CAPTCHA + Keyboard Negative / So sánh cách submit | CAPTCHA hiện, chưa nhập mã. | 1. Nhập thông tin sai.<br>2. Để ô CAPTCHA rỗng.<br>3. Nhấn Enter tại Password. | Username: `U_BAD`.<br>Password: `P_BAD`.<br>CAPTCHA: rỗng. | O1 + O3: Enter không bỏ qua CAPTCHA, tương đương TC13. | Có điều kiện — khảo sát CAPTCHA |
| TC21 | CAPTCHA Negative / Chuyển trạng thái | Môi trường thử nghiệm có chính sách dùng một lần và cách kiểm soát challenge và mã nhập. | 1. Gửi challenge hợp lệ với thông tin sai.<br>2. Gửi lại mã CAPTCHA đã tiêu thụ với thông tin sai. | Username: `U_BAD`.<br>Password: `P_BAD`.<br>CAPTCHA: đã sử dụng. | O1 + O3 lần hai: từ chối replay theo đặc tả. Không điều khiển được dữ liệu qua luồng được phép thì BLOCKED. | BLOCKED — cần đặc tả/môi trường |
| TC22 | CAPTCHA Activation / Chuyển trạng thái | Môi trường thử nghiệm có ngưỡng N, cách reset và giới hạn số lần thử đã xác nhận. | 1. Reset theo cơ chế được cung cấp.<br>2. Submit sai tuần tự tới N.<br>3. Quan sát CAPTCHA.<br>4. Submit thiếu CAPTCHA một lần. | Username: `U_BAD`.<br>Password: `P_BAD`.<br>N: theo đặc tả. | Mỗi lần bị từ chối; CAPTCHA xuất hiện đúng điều kiện và áp dụng O3. Dừng khi có rate limit/lockout ngoài kịch bản. | BLOCKED — chưa biết N; không chạy production |

## 5. Tiêu chí hoàn thành

- Selenium Project cài đặt/chạy được theo README; có cấu hình, fixture trình duyệt, Page Object và báo cáo.
- Các ca trong phạm vi có oracle/tiền điều kiện đã xác nhận được triển khai, mỗi ID một commit riêng. Ca nhiều biến thể parametrized trong cùng commit ID đó.
- Chỉ triển khai các ID còn trong bảng; ca thiếu điều kiện được SKIPPED/BLOCKED rõ lý do, không coi là đã kiểm thử.
- Báo cáo có ID, môi trường, thời điểm, kết quả, lý do skip/block và bằng chứng lỗi. Còn BLOCKED thì ghi phạm vi chưa xác minh, không tuyên bố hoàn tất toàn bộ kiểm thử.
- Kế hoạch chi tiết: [plan.md](plan.md). Bước hiện tại chỉ hoàn thiện yêu cầu và kế hoạch, chưa triển khai hoặc thực thi Selenium.



