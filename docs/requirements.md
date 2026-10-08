# Yêu cầu kiểm thử chức năng đăng nhập

## 1. Mục tiêu và phạm vi

Tạo Selenium Project tự động kiểm thử đăng nhập thất bại tại <https://vanphongdientu.utc.edu.vn/Login>.

- Không có mật khẩu hợp lệ để đăng nhập thành công; TC05 có Username tồn tại do người dùng xác nhận. Chỉ thực thi luồng đăng nhập bị từ chối hoặc dữ liệu bị validation chặn.
- “Testcase fail” được hiểu là **negative testcase**: bài test PASS khi ứng dụng từ chối đúng, không phải cố tình làm bài test thất bại.
- Phạm vi gồm ba trường Username, Password, CAPTCHA và thao tác submit form. CAPTCHA là ô nhập mã dạng text theo HTML người dùng cung cấp; đã xác minh lỗi và ngưỡng xuất hiện quan sát; người dùng xác nhận không tự hết hạn, mỗi lần đăng nhập sai cấp mã mới.
- Chỉ giữ negative testcase thuộc ba trường trên. ID được đánh lại liên tiếp TC01–TC22 theo thứ tự bảng; bảng hiện có 22 ca, gồm 10 ca CAPTCHA.
- Mỗi testcase được triển khai trong một commit riêng, dùng Conventional Commits bằng tiếng Anh, ví dụ `test(login): add TC01 empty credentials validation`.
- Không dò mật khẩu hoặc lặp request vô hạn để ép CAPTCHA xuất hiện. Ca payload mặc định được giới hạn ở môi trường thử nghiệm; ba payload đã được người dùng chấp thuận riêng trên UTC và gửi mỗi ca một lần. Chuẩn bị CAPTCHA dùng tài khoản giả, tối đa 5 lần mỗi phiên và dừng khi challenge hiện.

## 2. Căn cứ, dữ liệu và oracle

Đã khảo sát DOM và submit dữ liệu rỗng/giả trực tiếp trên UTC, xác minh locator và bốn loại thông báo lỗi ngày 08/10/2026. Người dùng đã cho phép sửa locator khác thực tế; xem [utc_live_execution.md](utc_live_execution.md) cho kết quả chạy mới nhất. [execution.md](execution.md) giữ kết quả giai đoạn trước.

### Quy ước dữ liệu

| Ký hiệu | Ý nghĩa |
| --- | --- |
| `U_BAD` | Tài khoản giả dành cho kiểm thử, ví dụ `qa_invalid_<run_id>`; xác nhận chưa được cấp phát khi có môi trường thử nghiệm. Không dùng tài khoản người thật. |
| `P_BAD` | Mật khẩu giả `InvalidPass_123!`, không phải thông tin xác thực thực. |
| `U_VALID` | Username được người dùng xác nhận tồn tại; lưu riêng trong .env và che trong dữ liệu báo cáo. |
| `C_WRONG` | Đáp án được xác nhận sai với challenge hiện tại, không chỉ một chuỗi đoán ngẫu nhiên. |
| `C_VALID` | Mã CAPTCHA hợp lệ lấy thủ công hoặc qua cơ chế test chính thức trong môi trường được phép; không bypass CAPTCHA. |

Mỗi ca bắt đầu bằng phiên trình duyệt mới, mở `/Login`, chờ form sẵn sàng và kiểm tra tiền điều kiện CAPTCHA. Không dùng trạng thái của ca trước để tạo tiền điều kiện ngầm cho ca sau.

### Oracle kiểm thử

- **O1 — Từ chối xác thực:** có lỗi/validation tương ứng; form đăng nhập vẫn hiển thị hoặc quay lại trang đăng nhập; không xuất hiện dấu hiệu đã xác thực được xác minh khi khảo sát. Không kết luận chỉ từ URL hoặc HTTP 200.
- **O2 — Validation:** có lỗi trình duyệt hoặc ứng dụng cho trường bắt buộc thiếu. Không mặc định ứng dụng phải chặn request phía client; không yêu cầu nguyên văn câu lỗi chưa được xác minh.
- **O3 — CAPTCHA:** có tín hiệu challenge chưa hoàn tất hoặc lỗi CAPTCHA tương ứng; vẫn chưa xác thực. “Sai tài khoản” đơn thuần không chứng minh CAPTCHA hoạt động.
- Chốt locator, nội dung lỗi và dấu hiệu xác thực trước khi triển khai assertion. Thiếu oracle thì BLOCKED, không nới assertion chỉ để PASS.
- CAPTCHA không xuất hiện: ca yêu cầu CAPTCHA là SKIPPED vì không áp dụng trong phiên. CAPTCHA có nhưng thiếu dữ liệu/đặc tả/cơ chế thử: BLOCKED. Nếu pytest biểu diễn cả hai bằng skip, báo cáo phải giữ riêng phân loại và lý do.
- PASS/FAIL chỉ ghi sau thực thi. Cả 22 ID đã có mã test; trạng thái trong bảng phản ánh lượt chạy trực tiếp trên UTC ngày 08/10/2026. Kết quả form tham chiếu cục bộ được báo riêng.

## 3. Locator đã cập nhật theo DOM thực tế

Sau khi người dùng cho phép sửa locator, dùng thuộc tính `name` và `type` trong form thay cho vị trí `nth-child`. Selector được kiểm tra duy nhất một phần tử và đúng `name`, `type`, `placeholder` trước khi nhập.

| Thành phần | CSS selector | Trạng thái kiểm chứng trên UTC |
| --- | --- | --- |
| Form | `form[action='/Login'][method='post']` | Đã xác minh. |
| Username | `form[action='/Login'][method='post'] input[name='username'][type='text']` | Đã xác minh trước và sau submit. |
| Password | `form[action='/Login'][method='post'] input[name='userpwd'][type='password']` | Đã xác minh trước và sau submit. |
| CAPTCHA | `form[action='/Login'][method='post'] input[name='captcha'][type='text']` | Đã xác minh trực tiếp khi CAPTCHA hiển thị. |
| Submit | `form[action='/Login'][method='post'] > input.submit_login[type='submit']` | Đã xác minh submit bằng nút. |
| Lỗi | `form[action='/Login'][method='post'] > div.error` | Đã xác minh sau submit. |
| Ảnh CAPTCHA | `form[action='/Login'][method='post'] img#captcha` | Đã quan sát trên UTC sau 3 lần sai trong phiên mới. |
| Đổi mã CAPTCHA | `form[action='/Login'][method='post'] a[onclick*="getElementById('captcha')"]` | Link đổi src của ảnh; không coi là reset bộ đếm sai. |

Trang mới không CAPTCHA có Username/Password ở vị trí 1/2. Sau submit sai, ứng dụng chèn `div.error` ở đầu form nên vị trí chuyển thành 2/3. Locator theo thuộc tính hoạt động ở cả hai bố cục. Không cần tạo submit ngầm để thay đổi DOM.

Các thông báo đã quan sát trực tiếp qua Selenium ngày 08/10/2026:

- Thiếu Username: `Bạn chưa nhập tên đăng nhập`.
- Thiếu Password: `Bạn chưa nhập mật khẩu`.
- Thông tin sai: `Tài khoản hoặc mật khẩu không đúng.`.
- CAPTCHA rỗng: `Mã bảo mật không đúng`.

Profile các oracle đã xác minh nằm trong `config/utc.env`. Thông báo CAPTCHA rỗng đã được quan sát; lỗi và form đăng nhập là bằng chứng từ chối quan sát được. Báo cáo lượt chạy thật được ghi riêng trong [utc_live_execution.md](utc_live_execution.md).

## 4. Bảng Testcase

| ID | Nhóm kiểm thử / kỹ thuật | Tiền điều kiện / phạm vi | Các bước thực hiện (Steps) | Dữ liệu kiểm thử (Test Data) | Kết quả mong đợi (Expected Result) | Kết quả UTC hiện tại |
| --- | --- | --- | --- | --- | --- | --- |
| TC01 | Validation Negative / Phân vùng tương đương | CAPTCHA ẩn. | 1. Để trống hai trường.<br>2. Bấm Đăng nhập. | Username: rỗng.<br>Password: rỗng. | O1 + O2: yêu cầu bổ sung thông tin bắt buộc. | PASS — UTC 08/10/2026 |
| TC02 | Validation Negative / Phân vùng tương đương | CAPTCHA ẩn. | 1. Để trống Username.<br>2. Nhập Password.<br>3. Bấm Đăng nhập. | Username: rỗng.<br>Password: `P_BAD`. | O1 + O2: validation cho Username thiếu. | PASS — UTC 08/10/2026 |
| TC03 | Validation Negative / Phân vùng tương đương | CAPTCHA ẩn. | 1. Nhập Username.<br>2. Để trống Password.<br>3. Bấm Đăng nhập. | Username: `U_BAD`.<br>Password: rỗng. | O1 + O2: validation cho Password thiếu. | PASS — UTC 08/10/2026 |
| TC04 | Functional Negative / Phân vùng tương đương | CAPTCHA ẩn; dữ liệu tài khoản không hợp lệ. | 1. Nhập thông tin sai.<br>2. Bấm Đăng nhập. | Username: `U_BAD`.<br>Password: `P_BAD`. | O1: lỗi xác thực và không đăng nhập. Không PASS chỉ vì form còn hiển thị. | PASS — UTC 08/10/2026 |
| TC05 | Functional Negative / Bảng quyết định | CAPTCHA ẩn; Username được xác nhận tồn tại. | 1. Nhập Username tồn tại.<br>2. Nhập mật khẩu sai.<br>3. Submit. | Username: `U_VALID`.<br>Password: được xác nhận sai. | O1: từ chối xác thực. Không thay `U_VALID` bằng tên giả rồi coi đã kiểm thử “đúng user, sai password”. | PASS — UTC 08/10/2026 |
| TC06 | Format Negative / Phân vùng tương đương | CAPTCHA ẩn; dùng thông tin đăng nhập sai. | 1. Nhập Username có khoảng trắng đầu/cuối.<br>2. Nhập mật khẩu giả.<br>3. Submit. | Username: `  qa_invalid_<run_id>  `.<br>Password: `P_BAD`. | O1: lỗi xác thực hoặc định dạng theo đặc tả đã chốt. Ca này không chứng minh chức năng trim. | PASS — UTC 08/10/2026 |
| TC07 | Security Negative / Error guessing | Mặc định môi trường thử nghiệm; production cần chấp thuận riêng. CAPTCHA ẩn. | 1. Nhập payload vào hai trường.<br>2. Submit một lần.<br>3. Quan sát phản hồi. | Username và Password: `' OR '1'='1`. | O1: không vượt xác thực, không lộ lỗi SQL/stack trace. Kết quả chỉ áp dụng payload này, không chứng minh toàn hệ thống an toàn SQL injection. | PASS — UTC 08/10/2026 |
| TC08 | Security Negative / Error guessing | Mặc định môi trường thử nghiệm; production cần chấp thuận riêng. CAPTCHA ẩn. | 1. Nhập payload Username và mật khẩu giả.<br>2. Submit.<br>3. Theo dõi alert và nội dung phản hồi. | Username: `<script>alert('qa_xss')</script>`.<br>Password: `P_BAD`. | O1: không vượt xác thực; payload không thực thi trong phản hồi quan sát được, không có alert `qa_xss`. Không kết luận về mọi dạng XSS. | PASS — UTC 08/10/2026 |
| TC09 | Keyboard Negative / So sánh cách submit | CAPTCHA ẩn; dùng dữ liệu sai. | 1. Nhập thông tin sai.<br>2. Tại ô Password, nhấn Enter.<br>3. Đối chiếu TC04. | Username: `U_BAD`.<br>Password: `P_BAD`. | O1: Enter submit và bị từ chối tương đương bấm nút. Phải có tín hiệu submit/lỗi, không PASS chỉ vì còn ở Login. | PASS — UTC 08/10/2026 |
| TC10 | Validation Negative / Phân vùng tương đương | CAPTCHA ẩn; chốt chính sách Username chỉ chứa dấu cách. | 1. Nhập Username ba dấu cách.<br>2. Nhập Password giả.<br>3. Submit. | Username: `   `.<br>Password: `P_BAD`. | O1; nếu đặc tả trim trước validation thì O2 cho Username rỗng, nếu không thì lỗi định dạng/xác thực. Chốt một oracle cụ thể trước triển khai. | PASS — UTC 08/10/2026 |
| TC11 | Validation Negative / Phân vùng tương đương | CAPTCHA ẩn; không mặc định Password được trim. | 1. Nhập Username giả.<br>2. Nhập Password ba dấu cách.<br>3. Submit. | Username: `U_BAD`.<br>Password: `   `. | O1: validation hoặc lỗi xác thực theo chính sách Password đã xác minh. Chốt oracle trước triển khai. | PASS — UTC 08/10/2026 |
| TC12 | Robustness Negative / Error guessing | Mặc định môi trường thử nghiệm; production cần chấp thuận riêng. CAPTCHA ẩn. | 1. Nhập Username dài và Password giả.<br>2. Ghi nhận giá trị thực sau maxlength nếu có.<br>3. Submit. | Username: `a` lặp 256 lần.<br>Password: `P_BAD`. | O1 hoặc validation độ dài theo đặc tả; không có trang lỗi máy chủ/stack trace. Báo đúng độ dài thực đã kiểm thử. Đây chưa phải giá trị biên chính thức. | PASS — UTC 08/10/2026 |
| TC13 | CAPTCHA Negative / Bảng quyết định | CAPTCHA hiện; xác định được validation CAPTCHA. | 1. Nhập thông tin sai.<br>2. Để ô CAPTCHA rỗng.<br>3. Submit. | Username: `U_BAD`.<br>Password: `P_BAD`.<br>CAPTCHA: rỗng. | O1 + O3: yêu cầu hoàn tất CAPTCHA, không bỏ qua challenge. | PASS — UTC 08/10/2026 |
| TC14 | CAPTCHA Negative / Phân vùng tương đương | CAPTCHA dạng nhập mã; có đáp án chắc chắn sai. | 1. Nhập thông tin sai.<br>2. Nhập CAPTCHA sai.<br>3. Submit. | Username: `U_BAD`.<br>Password: `P_BAD`.<br>CAPTCHA: `C_WRONG`. | O1 + O3: CAPTCHA không hợp lệ, không xác thực. | PASS — UTC 08/10/2026 |
| TC15 | CAPTCHA Negative / Phân vùng tương đương | CAPTCHA dạng mã; chính sách dấu cách đã xác minh. | 1. Nhập thông tin sai.<br>2. Nhập CAPTCHA ba dấu cách.<br>3. Submit. | Username: `U_BAD`.<br>Password: `P_BAD`.<br>CAPTCHA: `   `. | O1 + O3: CAPTCHA thiếu/không hợp lệ theo đặc tả đã chốt. | PASS — UTC 08/10/2026 |
| TC16 | CAPTCHA Negative / Chuyển trạng thái | Có refresh; có đáp án hợp lệ của challenge A. | 1. Lấy đáp án A theo cơ chế được phép.<br>2. Refresh sang B, xác nhận challenge đổi.<br>3. Gửi đáp án A với thông tin sai. | Username: `U_BAD`.<br>Password: `P_BAD`.<br>CAPTCHA: đáp án cũ A. | O1 + O3: challenge A bị thay thế không còn được chấp nhận. Nếu đáp án trùng B hoặc không chứng minh challenge đổi thì BLOCKED. | PASS — UTC 08/10/2026; xác nhận A/B khác nhau, mã A sau refresh bị từ chối |
| TC17 | CAPTCHA + Authentication Negative / Chuyển trạng thái | Người dùng xác nhận CAPTCHA không tự hết hạn; có mã đúng, không bấm đổi mã. | 1. Nhận mã CAPTCHA đúng thủ công.<br>2. Chờ 60 giây, không đổi mã.<br>3. Gửi mã đó với tài khoản sai. | Username: `U_BAD`.<br>Password: `P_BAD`.<br>CAPTCHA: mã đúng trước thời gian chờ. | O1: CAPTCHA còn được chấp nhận, trả lỗi xác thực tài khoản. Báo đúng thời gian quan sát; một lần chờ 60 giây không chứng minh hiệu lực vô hạn. | PASS — UTC 08/10/2026; mã còn hợp lệ sau 60 giây không đổi challenge |
| TC18 | CAPTCHA + Authentication Negative / Bảng quyết định | CAPTCHA hiện; có `C_VALID` bằng cơ chế được phép. | 1. Nhập thông tin sai.<br>2. Hoàn tất CAPTCHA đúng.<br>3. Submit. | Username: `U_BAD`.<br>Password: `P_BAD`.<br>CAPTCHA: `C_VALID`. | O1: CAPTCHA được chấp nhận nhưng tài khoản sai vẫn bị từ chối. Phân biệt lỗi xác thực và lỗi CAPTCHA, không coi mọi lỗi là PASS. | PASS — UTC 08/10/2026 |
| TC19 | CAPTCHA + Validation Negative / Bảng quyết định | CAPTCHA hiện; có `C_VALID` riêng mỗi biến thể. | 1. Để trống Username, nhập Password giả, hoàn tất CAPTCHA và submit.<br>2. Trong phiên/challenge mới: nhập Username giả, để Password trống, hoàn tất CAPTCHA và submit. | A: Username rỗng, Password `P_BAD`.<br>B: Username `U_BAD`, Password rỗng.<br>CAPTCHA: hợp lệ mỗi biến thể. | O1 + O2 cho trường thiếu. CAPTCHA đúng không thay thế thông tin bắt buộc; không tái dùng mã đã tiêu thụ. | PASS — UTC 08/10/2026; cả hai biến thể thiếu Username/Password |
| TC20 | CAPTCHA + Keyboard Negative / So sánh cách submit | CAPTCHA hiện, chưa nhập mã. | 1. Nhập thông tin sai.<br>2. Để ô CAPTCHA rỗng.<br>3. Nhấn Enter tại Password. | Username: `U_BAD`.<br>Password: `P_BAD`.<br>CAPTCHA: rỗng. | O1 + O3: Enter không bỏ qua CAPTCHA, tương đương TC13. | PASS — UTC 08/10/2026 |
| TC21 | CAPTCHA Negative / Chuyển trạng thái | Người dùng xác nhận mỗi lần đăng nhập sai cấp CAPTCHA mới; có mã đúng cho challenge A và B. | 1. Gửi mã A đúng với tài khoản sai.<br>2. Nhận mã B sau phản hồi, xác nhận A khác B.<br>3. Gửi lại A với tài khoản sai. | Username: `U_BAD`.<br>Password: `P_BAD`.<br>CAPTCHA: đáp án A đã bị thay thế. | O1 + O3 lần hai: từ chối mã A. Nếu A và B trùng đáp án thì chưa thể kết luận và ghi BLOCKED. | PASS — UTC 08/10/2026; mã A bị từ chối sau khi lỗi đăng nhập cấp B |
| TC22 | CAPTCHA Activation / Chuyển trạng thái | Browser mới không CAPTCHA; ngưỡng N quan sát được và giới hạn số lần thử đã xác nhận. | 1. Khởi tạo browser mới, xác minh CAPTCHA ẩn.<br>2. Submit sai tuần tự tới N.<br>3. Quan sát CAPTCHA.<br>4. Submit thiếu CAPTCHA một lần. | Username: `U_BAD`.<br>Password: `P_BAD`.<br>N: theo đặc tả. | Mỗi lần bị từ chối; CAPTCHA xuất hiện đúng điều kiện và áp dụng O3. Dừng khi có rate limit/lockout ngoài kịch bản. | PASS — UTC 08/10/2026 |

## 5. Tiêu chí hoàn thành

- Selenium Project cài đặt/chạy được theo README; có cấu hình, fixture trình duyệt, Page Object và báo cáo.
- Các ca trong phạm vi có oracle/tiền điều kiện đã xác nhận được triển khai, mỗi ID một commit riêng. Ca nhiều biến thể parametrized trong cùng commit ID đó.
- Chỉ triển khai các ID còn trong bảng; ca thiếu điều kiện được SKIPPED/BLOCKED rõ lý do, không coi là đã kiểm thử.
- Báo cáo có ID, môi trường, thời điểm, kết quả, lý do skip/block và bằng chứng lỗi. Còn BLOCKED thì ghi phạm vi chưa xác minh, không tuyên bố hoàn tất toàn bộ kiểm thử.
- Hướng dẫn chạy và tổng hợp báo cáo: [README.md](../README.md). Đã triển khai Selenium và chạy các ca đủ điều kiện trên UTC. Kết quả mới nhất: 23 lượt PASS cho 22 ID, không còn BLOCKED/SKIPPED; các lần chạy lại ca assisted vẫn cần mã thủ công của challenge mới. Báo cáo mới nhất: [utc_live_execution.md](utc_live_execution.md).
