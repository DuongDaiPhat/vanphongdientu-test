# Kiểm thử đăng nhập Văn phòng điện tử UTC

Dự án **Python + Selenium 4 + pytest** cho 22 negative testcase TC01–TC22 của Username, Password và CAPTCHA. TC19 có hai biến thể nên pytest thu thập 23 lượt kiểm thử. Bài test PASS khi ứng dụng từ chối đúng; không cần tài khoản đăng nhập thành công.

Yêu cầu và dữ liệu: [docs/requirements.md](docs/requirements.md). Kế hoạch và tiến độ: [docs/plan.md](docs/plan.md). Kết quả bàn giao: [docs/execution.md](docs/execution.md).

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
│   └── reference_server.py      # Form tham chiếu cục bộ để xác minh mã test
├── pages/
│   ├── base_page.py             # Explicit wait, click, type
│   └── login_page.py            # Locator theo CAPTCHA và thao tác form
└── tests/
    └── test_login_e2e.py        # TC01–TC22; TC19 parametrized
tools/probe_login.py             # Kiểm tra locator, không submit đăng nhập
```

Fixture là nơi duy nhất tạo/đóng browser, mỗi lượt kiểm thử một phiên mới. Mã dùng Page Object và không tự retry submit.

## Locator theo trạng thái

Các selector giữ đúng hai bộ người dùng cung cấp, cùng tiền tố `body > div > div.main > div.right > div.form > form > `:

| Trạng thái | Username | Password | CAPTCHA |
| --- | --- | --- | --- |
| Không có CAPTCHA | `input[type=text]:nth-child(2)` | `input[type=password]:nth-child(3)` | Không nhập |
| Có CAPTCHA | `input[type=text]:nth-child(6)` | `input[type=password]:nth-child(7)` | `input[type=text]:nth-child(5)` |

`LoginPage` quan sát ô CAPTCHA có hiển thị hay không rồi chọn selector trước mỗi thao tác. Kiểm tra đúng một phần tử và đúng `name`, `type`, `placeholder`. Không âm thầm dùng selector khác khi vị trí DOM thay đổi. Việc phát hiện CAPTCHA theo `name` chỉ đọc trạng thái; việc nhập liệu vẫn qua CSS đã cung cấp.

Kiểm tra DOM thật, không gửi đăng nhập:

```powershell
.\.venv\Scripts\python.exe tools/probe_login.py
```

Kết quả ở `reports/locator-probe.json` và `reports/locator-probe.png`. Exit code 1 nghĩa là có selector không khớp; CAPTCHA không xuất hiện được ghi SKIPPED. Ở lần kiểm tra hiện tại, cả hai selector không CAPTCHA đều khớp 0 phần tử trên UTC; xem báo cáo bàn giao trước khi chạy trên hệ thống thật.

## Chạy kiểm chứng mã test cục bộ

```powershell
.\.venv\Scripts\python.exe -m pytest --demo -q --junitxml=reports/reference.xml
.\.venv\Scripts\python.exe -m pytest --demo -q -k "test_tc13_"
```

`--demo` tạo HTTP server chỉ trên `127.0.0.1`, chạy Chrome/Selenium thật, rồi đóng server. Form tham chiếu có hai bố cục DOM, validation, refresh, hết hạn, mã dùng một lần và ngưỡng CAPTCHA. Fixture cung cấp mã tổng hợp trực tiếp từ server thử nghiệm; không giải CAPTCHA của UTC. **PASS ở đây chỉ xác minh mã automation, không chứng minh trang UTC đạt yêu cầu.**

Có thể kiểm tra assertion có phát hiện lỗi bằng các lệnh sau; cả ba lệnh phải trả về lỗi test (exit code 1):

```powershell
.\.venv\Scripts\python.exe -m pytest --demo --demo-defect=captcha-bypass -q -k "test_tc13_" --tb=short
.\.venv\Scripts\python.exe -m pytest --demo --demo-defect=authentication-bypass -q -k "test_tc04_" --tb=short
.\.venv\Scripts\python.exe -m pytest --demo --demo-defect=wrong-message -q -k "test_tc04_" --tb=short
```

## Chạy trên hệ thống đích

```powershell
Copy-Item .env.example .env
```

File `.env` tự được đọc như các cặp `KEY=VALUE`; không thực thi biểu thức. Biến môi trường có sẵn được ưu tiên. Không commit `.env`.

Trước khi thực thi trên UTC, cần xác minh lại locator và điền **selector vùng lỗi cùng regex lỗi quan sát thực tế**: `ERROR_SELECTOR`, `AUTH_ERROR_PATTERN`, `USERNAME_ERROR_PATTERN`, `PASSWORD_ERROR_PATTERN`, `CAPTCHA_ERROR_PATTERN`. Không dùng thông báo của form tham chiếu làm đặc tả UTC. `AUTHENTICATED_SELECTOR` bổ sung kiểm tra không xuất hiện nội dung đã xác thực khi có locator được xác nhận.

```powershell
$env:BASE_URL = 'https://vanphongdientu.utc.edu.vn/Login'
$env:HEADLESS = 'true'
.\.venv\Scripts\python.exe -m pytest -q -m "negative and not captcha and not security and not assisted and not test_env_only" --junitxml=reports/login-negative.xml
.\.venv\Scripts\python.exe -m pytest -q -k "test_tc01_" --junitxml=reports/tc01.xml
```

Thiếu oracle thì bài test được ghi **BLOCKED trước khi mở browser**, không đoán thông báo và không submit để lấy PASS. TC05 cần `KNOWN_USERNAME` và `KNOWN_WRONG_PASSWORD` được xác nhận. Chạy tuần tự; không dùng plugin chạy song song để thử nhiều lần đăng nhập trên hệ thống thật.

Ca CAPTCHA chỉ chạy khi challenge hiện trong phiên mới. TC14/TC16/TC17/TC18/TC19/TC21 cần mã đúng hoặc mã được xác nhận sai. Có thể nhập thủ công với timeout hữu hạn:

```powershell
.\.venv\Scripts\python.exe -m pytest --allow-assisted -s -q -k "test_tc18_"
```

Quan sát ảnh chụp được chỉ ra trong terminal, nhập mã hiện tại. TC14 nhận mã đúng rồi đổi một ký tự cùng độ dài để chắc chắn tạo mã sai. Không có dữ liệu thì hủy/timeout và ghi BLOCKED. Môi trường test chính thức có thể thay fixture `captcha_solver` bằng API test được cấp, không dùng OCR hoặc dịch vụ giải CAPTCHA.

TC07/TC08/TC12/TC21/TC22 được chặn mặc định. Chỉ mở bằng `--allow-test-env` khi `ENVIRONMENT=test`, `APPROVED_TEST_HOST` khớp hostname đích và hostname khác UTC production. TC21 cần đặc tả mã dùng một lần; TC22 cần ngưỡng N và reset đã xác minh, số submit không vượt `MAX_LOGIN_ATTEMPTS`. Không lặp vô hạn để ép CAPTCHA xuất hiện.

## Báo cáo và Git

Mỗi lần pytest tạo JSON và Markdown trong `reports/`, có ID/biến thể, môi trường, thời điểm UTC, kết quả, dữ liệu giả, browser/version khi có, lý do và screenshot khi lỗi. JUnit XML bật qua `--junitxml`. Báo cáo tổng hợp giữ riêng **BLOCKED** và **SKIPPED** dù pytest biểu diễn cả hai bằng skip.

- PASS: đã thực thi và quan sát đúng loại từ chối.
- FAIL: assertion, locator hoặc hạ tầng không đáp ứng.
- SKIPPED: trạng thái CAPTCHA không phù hợp phiên hiện tại.
- BLOCKED: thiếu oracle, dữ liệu, đặc tả hoặc môi trường được cấu hình.

Không lưu cookie hoặc page source tự động khi lỗi. Các screenshot hỗ trợ CAPTCHA và ảnh lỗi chỉ nằm trong thư mục báo cáo bị ignore. `docs/` được Git theo dõi; môi trường ảo, cache, `.env` và báo cáo bị ignore.

Nhánh công việc: `codex/login-negative-tests`. Mỗi TC01–TC22 có commit Conventional Commits tiếng Anh riêng. TC19 gồm hai biến thể trong cùng commit; commit hạ tầng/tài liệu tách riêng.
