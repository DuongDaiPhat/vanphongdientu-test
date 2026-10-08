# Kiểm thử đăng nhập Văn phòng điện tử UTC

Dự án **Python + Selenium 4 + pytest** cho 22 negative testcase TC01–TC22 của Username, Password và CAPTCHA. TC19 có hai biến thể nên pytest thu thập 23 lượt kiểm thử. Bài test PASS khi ứng dụng từ chối đúng; không cần tài khoản đăng nhập thành công.

## Kết quả chạy trực tiếp trên UTC

Đích: <https://vanphongdientu.utc.edu.vn/Login>. Kết quả mới nhất được tổng hợp từ **8 đợt chạy ngày 08/10/2026, 16:17:33–17:10:19 (UTC+7)**.

| Trạng thái | Số lượt |
| --- | --- |
| PASS | **23** |
| FAIL | **0** |
| SKIPPED | **0** |
| BLOCKED | **0** |

Có **22 ID TC01–TC22**; TC19 có hai biến thể nên tổng 23 lượt. Báo cáo lấy kết quả mới nhất của từng biến thể, giữ Run ID và thời điểm nguồn; các lượt lỗi/chờ mã trước khi sửa vẫn được lưu. Kết quả form tham chiếu cục bộ được ghi riêng.

- [Báo cáo HTML với 23 ảnh bằng chứng nhúng](report.html).

TC07/TC08/TC12 đã gửi mỗi ca một lần sau chấp thuận riêng của người dùng. CAPTCHA và tài khoản thử nghiệm được cung cấp theo điều kiện từng ca. TC17 được sửa theo xác nhận CAPTCHA không tự hết hạn: giữ nguyên mã **60 giây**, sau đó mã vẫn được chấp nhận và tài khoản sai bị từ chối. Khoảng quan sát này không chứng minh hiệu lực vô hạn.

## Cài đặt

Đã kiểm tra với Python 3.14, Selenium 4.50.0, pytest 9.1.1 và Chrome 154 trên Windows. Khuyến nghị dùng đúng môi trường này để tái hiện; phiên bản khác cần kiểm tra tương thích.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest --collect-only -q
```

Cài Chrome trước khi chạy. Selenium Manager tìm/tải driver tương thích; lần đầu cần kết nối mạng. Có thể đặt `DRIVER_PATH` và `BROWSER_BINARY` để sử dụng file đã có. Nếu lệnh `python` trên máy dùng launcher bị lỗi, gọi trực tiếp Python đã cài để tạo `.venv`.

## Cấu trúc

```text
src/test/python/e2e/
├── conftest.py                  # Fixture function scope, điều kiện chạy, báo cáo
├── base/
│   ├── base_test.py             # Khởi tạo/đóng WebDriver, timeout
│   ├── settings.py              # Cấu hình .env và biến môi trường
│   ├── reference_server.py      # Form tham chiếu cục bộ để xác minh mã test
│   ├── captcha_assistance.py    # Nhận mã người nhập theo challenge
│   └── html_report.py           # HTML độc lập với ảnh nhúng
├── pages/
│   ├── base_page.py             # Explicit wait, click, type
│   └── login_page.py            # Locator theo name/type và thao tác form
└── tests/
    └── test_login_e2e.py        # TC01–TC22; TC19 parametrized
config/utc.env                  # Profile UTC đã xác minh, không có tài khoản
tools/probe_login.py             # Kiểm tra locator, không submit đăng nhập
tools/probe_captcha.py           # Khảo sát CAPTCHA với giới hạn hữu hạn
tools/run_utc.py                 # Chạy ca được chọn và xuất HTML
tools/merge_reports.py           # Tổng hợp kết quả, giữ nguồn từng biến thể
```

Fixture là nơi duy nhất tạo/đóng browser, mỗi lượt kiểm thử một phiên mới. Mã dùng Page Object và không tự retry submit.

## Locator đã xác minh

Dùng tiền tố `form[action='/Login'][method='post']` và thuộc tính `name/type`. `LoginPage` chờ đúng một phần tử có `name`, `type`, `placeholder` mong đợi trước khi nhập.

| Thành phần | CSS selector trong form |
| --- | --- |
| Username | `input[name='username'][type='text']` |
| Password | `input[name='userpwd'][type='password']` |
| CAPTCHA | `input[name='captcha'][type='text']` |
| Submit | `input.submit_login[type='submit']` |
| Vùng lỗi | `div.error` |
| Ảnh CAPTCHA | `img#captcha` |
| Đổi mã | `a[onclick*="getElementById('captcha')"]` |


Kiểm tra DOM thật, không gửi đăng nhập:

```powershell
.\.venv\Scripts\python.exe tools/probe_login.py
```

Kết quả ở `reports/locator-probe.json` và `reports/locator-probe.png`. Exit code 1 nghĩa là có selector không khớp; CAPTCHA không xuất hiện được ghi SKIPPED trong khảo sát DOM.

## Chạy kiểm chứng mã test cục bộ

```powershell
.\.venv\Scripts\python.exe -m pytest --demo -q --junitxml=reports/reference.xml
.\.venv\Scripts\python.exe -m pytest --demo -q -k "test_tc13_"
```

`--demo` tạo HTTP server chỉ trên `127.0.0.1`, chạy Chrome/Selenium thật, rồi đóng server. Form tham chiếu có hai bố cục DOM, validation, refresh, mã không tự hết hạn, cấp challenge mới sau phản hồi và ngưỡng CAPTCHA. Fixture cung cấp mã tổng hợp trực tiếp từ server thử nghiệm; không giải CAPTCHA của UTC. **PASS ở đây chỉ xác minh mã automation, không chứng minh trang UTC đạt yêu cầu.**

Có thể kiểm tra assertion có phát hiện lỗi bằng các lệnh sau; cả ba lệnh phải trả về lỗi test (exit code 1):

```powershell
.\.venv\Scripts\python.exe -m pytest --demo --demo-defect=captcha-bypass -q -k "test_tc13_" --tb=short
.\.venv\Scripts\python.exe -m pytest --demo --demo-defect=authentication-bypass -q -k "test_tc04_" --tb=short
.\.venv\Scripts\python.exe -m pytest --demo --demo-defect=wrong-message -q -k "test_tc04_" --tb=short
```

## Chạy trên hệ thống đích

Tạo cấu hình riêng nếu chưa có:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

`tools/run_utc.py` nạp profile công khai `config/utc.env` gồm URL, locator lỗi, regex đã quan sát và chính sách CAPTCHA. File `.env` bổ sung dữ liệu riêng như `KNOWN_USERNAME`, `KNOWN_WRONG_PASSWORD`; không commit file này. Biến môi trường có sẵn được ưu tiên. File cấu hình chỉ đọc cặp `KEY=VALUE`, không thực thi biểu thức.

### Các ca cơ bản

TC05 cần Username tồn tại đã xác nhận và mật khẩu giả sai. Những ca khác dùng dữ liệu giả do fixture tạo.

```powershell
.\.venv\Scripts\python.exe tools/run_utc.py --cases TC01 TC02 TC03 TC04 TC05 TC06 TC09 TC10 TC11 --html reports/utc-live/basic-new.html
```

Bộ test kiểm tra DOM/trạng thái CAPTCHA trước khi xác minh oracle và submit. Thiếu oracle hoặc dữ liệu được ghi BLOCKED; CAPTCHA không phù hợp phiên được ghi SKIPPED. Không dùng lỗi CAPTCHA để kết luận ca xác thực tài khoản PASS.

### CAPTCHA thiếu mã và activation

Đã quan sát CAPTCHA xuất hiện sau lần sai thứ 3 trong phiên mới. `--prepare-captcha` dùng tài khoản giả, tối đa 5 lần trong mỗi phiên và dừng ngay khi ô mã xuất hiện. Mỗi testcase có browser riêng.

```powershell
.\.venv\Scripts\python.exe tools/run_utc.py --cases TC13 TC15 TC20 --prepare-captcha --html reports/utc-live/captcha-empty-new.html
.\.venv\Scripts\python.exe tools/run_utc.py --cases TC22 --check-activation --html reports/utc-live/captcha-activation-new.html
```

TC22 dùng `CAPTCHA_TRIGGER_ATTEMPTS=3`, `RESET_STRATEGY=fresh_browser` và giới hạn tổng submit `MAX_LOGIN_ATTEMPTS=5`. Link đổi mã chỉ refresh challenge; không được coi là reset bộ đếm đăng nhập sai.

### CAPTCHA có người nhập mã

Người dùng xác nhận CAPTCHA không tự hết hạn và mỗi lần đăng nhập sai cấp mã mới. TC17 quan sát `CAPTCHA_OBSERVATION_SECONDS=60`. TC16 và TC21 cần hai đáp án A/B khác nhau để kiểm chứng mã cũ bị từ chối.

```powershell
$env:ASSISTED_TIMEOUT = '600'
.\.venv\Scripts\python.exe tools/run_utc.py --cases TC14 TC16 TC17 TC18 TC19 TC21 --prepare-captcha --assisted --check-replay --html reports/utc-live/captcha-assisted-new.html
```

Terminal chỉ ra ảnh challenge và yêu cầu nhập mã hiện tại. TC14 nhận mã đúng rồi đổi một ký tự để tạo mã chắc chắn sai. TC19 dùng challenge riêng cho từng biến thể. Hết thời gian hoặc hủy nhập mã được ghi BLOCKED. Bộ test không dùng OCR hoặc dịch vụ giải CAPTCHA.

Có thể thêm `--captcha-inbox reports/utc-live/captcha-assistance` để nhận mã qua file. `current-request.json` ghi ID challenge, ảnh, thời gian chờ và đường dẫn trả lời. File trả lời chứa `request_id` khớp phiên hiện tại và `code`; mã được xóa sau khi nhận hoặc hết thời gian. Không dùng lại mã của phiên đã đóng.

TC07/TC08/TC12 được chặn mặc định trên production; `--include-payloads` mở các ca này khi có chấp thuận cụ thể. Ba ca đã được thực hiện một lần trong đợt nghiệm thu. TC21/TC22 dùng các cờ riêng ở trên theo chính sách đã xác minh. Không tự retry submit và chạy tuần tự trên hệ thống thật.

## Báo cáo và Git

Mỗi lần pytest tạo JSON và Markdown trong thư mục báo cáo, có ID/biến thể, môi trường, thời điểm UTC, kết quả, dữ liệu giả, browser/version khi có, lý do và screenshot khi lỗi. Runner UTC tự xuất JUnit XML của đợt hiện tại tại `reports/utc-live/junit.xml`; pytest trực tiếp dùng `--junitxml`. `--html` của runner hoặc `--html-report` của pytest tạo HTML độc lập với ảnh nhúng, tìm kiếm và bộ lọc. Báo cáo tổng hợp giữ riêng **BLOCKED** và **SKIPPED** dù pytest biểu diễn cả hai bằng skip.

- PASS: đã thực thi và quan sát đúng loại từ chối.
- FAIL: assertion, locator hoặc hạ tầng không đáp ứng.
- SKIPPED: trạng thái CAPTCHA không phù hợp phiên hiện tại.
- BLOCKED: thiếu oracle, dữ liệu, đặc tả hoặc môi trường được cấu hình.

Không lưu cookie hoặc page source tự động khi lỗi. Các screenshot hỗ trợ CAPTCHA và ảnh lỗi chỉ nằm trong thư mục báo cáo bị ignore. `docs/` được Git theo dõi; môi trường ảo, cache, `.env` và báo cáo bị ignore.

Tổng hợp các đợt UTC đã lưu, không thực thi lại testcase:

```powershell
$sourceReports = @(Get-ChildItem reports/utc-live -Filter '*-results.json' | Select-Object -ExpandProperty FullName)
.\.venv\Scripts\python.exe tools/merge_reports.py @sourceReports --html reports/utc-live/report.html
```

Công cụ lấy kết quả mới nhất theo ID/biến thể và giữ nguồn từng dòng. Chỉ tổng hợp các nguồn cùng hệ thống, môi trường và chế độ chạy. HTML/JSON tổng hợp bao phủ 23 lượt; JUnit XML hiện tại chỉ thuộc đợt cuối. Báo cáo trong `reports/` được tạo tại workspace và bị Git ignore.

Nhánh công việc: `codex/login-negative-tests`. Mỗi TC01–TC22 có commit Conventional Commits tiếng Anh riêng. TC19 gồm hai biến thể trong cùng commit; commit hạ tầng/tài liệu tách riêng.

## Bảng Testcase

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
