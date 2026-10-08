# Kế hoạch triển khai Selenium login tests bằng Python

## 1. Mục tiêu và phạm vi

Xây dựng Selenium Project bằng **Python + Selenium 4 + pytest** để kiểm thử đăng nhập thất bại tại <https://vanphongdientu.utc.edu.vn/Login>, theo ID và oracle trong [requirements.md](requirements.md).

Phạm vi chỉ gồm **Username, Password, CAPTCHA** và thao tác submit bằng nút Đăng nhập hoặc phím Enter. Chỉ giữ các negative testcase tương ứng; không cần đăng nhập thành công. Ca cần Username tồn tại hoặc mã CAPTCHA đúng được ghi phụ thuộc riêng, không giả lập kết quả PASS khi thiếu dữ liệu.

Bảng yêu cầu sau khi thu hẹp còn **22 ca**, gồm **10 ca CAPTCHA**. ID được đánh lại liên tiếp từ TC01 đến TC22 theo thứ tự trong bảng. Repository hiện chưa có mã nguồn kiểm thử; tài liệu này mô tả cấu trúc và các bước sẽ triển khai.

## 2. Locator sử dụng

Các selector và element dưới đây do người dùng cung cấp. Triển khai nguyên CSS selector bằng `By.CSS_SELECTOR`, chưa coi là đã chạy kiểm chứng trên trình duyệt.

| Trạng thái | Trường | CSS selector | Element |
| --- | --- | --- | --- |
| Không có CAPTCHA | Username | `body > div > div.main > div.right > div.form > form > input[type=text]:nth-child(2)` | `<input placeholder="Tên đăng nhập" type="text" name="username">` |
| Không có CAPTCHA | Password | `body > div > div.main > div.right > div.form > form > input[type=password]:nth-child(3)` | `<input placeholder="Mật khẩu" type="password" name="userpwd">` |
| Có CAPTCHA | Username | `body > div > div.main > div.right > div.form > form > input[type=text]:nth-child(6)` | `<input placeholder="Tên đăng nhập" type="text" name="username">` |
| Có CAPTCHA | Password | `body > div > div.main > div.right > div.form > form > input[type=password]:nth-child(7)` | `<input placeholder="Mật khẩu" type="password" name="userpwd">` |
| Có CAPTCHA | CAPTCHA | `body > div > div.main > div.right > div.form > form > input[type=text]:nth-child(5)` | `<input placeholder="Mã bảo mật" type="text" name="captcha">` |

Đặt các locator theo hai trạng thái trong `LoginPage`. Xác định CAPTCHA đang hiển thị bằng quan sát DOM trước khi chọn cặp selector; không dựa vào thứ tự chạy testcase. Trước khi nhập, kiểm tra selector khớp đúng một phần tử có `name`, `type`, `placeholder` tương ứng. Vì `nth-child` phụ thuộc vị trí DOM, kiểm tra cả khi CAPTCHA hiện và ẩn; không âm thầm thay selector nếu vị trí đổi. Khi CAPTCHA không hiển thị, chỉ các ca yêu cầu CAPTCHA được phân loại theo tiền điều kiện; Username/Password vẫn phải khớp chính xác.

Locator nút submit, vùng lỗi, ảnh/challenge và refresh CAPTCHA cần khảo sát riêng. Chỉ dùng các thành phần này để thực thi và quan sát ca kiểm thử của ba trường trong phạm vi.

## 3. Cấu trúc thư mục theo ảnh tham khảo

Giữ cách phân lớp `base / pages / tests` và đường dẫn `src/test/.../e2e` như ảnh; chuyển phần ngôn ngữ thành `python`, dùng tên file Python và pytest. Các page/test thuộc nghiệp vụ khác trong ảnh không được đưa vào phạm vi đăng nhập.

```text
vanphongdientu-test/
├── README.md
├── requirements.txt
├── pytest.ini
├── .env.example
├── docs/
│   ├── requirements.md
│   └── plan.md
├── src/
│   └── test/
│       └── python/
│           └── e2e/
│               ├── __init__.py
│               ├── conftest.py          # Fixture pytest, cấu hình, bằng chứng lỗi
│               ├── base/
│               │   ├── __init__.py
│               │   └── base_test.py     # BaseTest: WebDriver, timeout, cleanup
│               ├── pages/
│               │   ├── __init__.py
│               │   ├── base_page.py     # BasePage: wait, click, type, đọc nội dung
│               │   └── login_page.py    # LoginPage: Username, Password, CAPTCHA
│               └── tests/
│                   ├── __init__.py
│                   └── test_login_e2e.py # TestLoginE2E: negative login tests
└── reports/                             # Sinh khi chạy, không commit
```

### Vai trò các lớp và fixture

| Thành phần | Trách nhiệm |
| --- | --- |
| `BaseTest` | Hàm tạo WebDriver, Chrome options, timeout và đóng driver. Được fixture gọi để quản lý vòng đời; không chứa testcase nghiệp vụ. |
| `conftest.py` | Fixture `driver` ở scope function: gọi `BaseTest` tạo browser, yield cho test, thu bằng chứng khi lỗi và luôn quit khi teardown. Đọc cấu hình, kiểm tra môi trường và phân loại skip/block. |
| `BasePage` | Nhận driver; cung cấp explicit wait, click, clear/type và đọc nội dung. Không chứa assertion riêng của từng testcase. |
| `LoginPage(BasePage)` | Chứa ba locator đã cung cấp; mở trang, điền Username/Password/CAPTCHA, submit nút/Enter, đọc lỗi và nhận biết CAPTCHA hiển thị. |
| `TestLoginE2E` | Nhận fixture `driver`, tạo `LoginPage`, thực thi từng ID và assertion O1/O2/O3. Tên hàm chứa ID, ví dụ `test_tc01_empty_credentials`. |

Fixture là điểm duy nhất điều phối vòng đời browser để tránh tạo driver hai lần. Không dùng kế thừa `unittest.TestCase` hoặc setup/teardown kiểu Java/JUnit. Mỗi test có phiên mới; ca TC19 dùng parametrization với challenge riêng cho từng biến thể.

### Cấu hình thu thập và import

Trong `pytest.ini`, cấu hình dự kiến:

```ini
[pytest]
testpaths = src/test/python/e2e/tests
pythonpath = src/test/python
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    negative: Negative login scenarios
    captcha: Requires a visible CAPTCHA
    security: Security payload scenarios
    assisted: Requires manual or official test support
    test_env_only: Requires an approved test environment
```

Import từ package `e2e`, ví dụ `from e2e.pages.login_page import LoginPage`. `conftest.py` đặt ở thư mục cha `e2e/` để pytest áp dụng fixture cho các test bên dưới; `base_test.py` không bị thu thập thành testcase.

`requirements.txt` chốt phiên bản sau kiểm tra tương thích. `.env.example` chỉ chứa cấu hình mẫu: URL, browser, headless, timeout, môi trường; triển khai rõ cơ chế đọc file/biến môi trường. Không chứa tài khoản thật. Chrome là browser mặc định, hỗ trợ chế độ có giao diện và headless.

## 4. Thứ tự thực hiện và đầu ra

| Bước | Công việc | Đầu ra / điều kiện chuyển bước |
| --- | --- | --- |
| 1. Khảo sát | Kiểm tra ba CSS selector và thuộc tính element; xác minh submit, Enter, lỗi validation/xác thực/CAPTCHA, dấu hiệu chưa xác thực. Quan sát CAPTCHA nếu có sẵn, không submit lặp để ép xuất hiện. | Cập nhật locator hỗ trợ và oracle từ bằng chứng; điều kiện chưa xác định ghi BLOCKED. |
| 2. Khung Python | Tạo cấu trúc mục 3, dependency, pytest config, đọc cấu hình, `BaseTest` và fixture driver. | Thu thập test được; smoke check hạ tầng mở/đóng browser thành công, không cần đăng nhập thành công. |
| 3. Page Objects | Viết `BasePage`, `LoginPage`; thêm explicit wait, thao tác ba trường, submit, đọc lỗi, nhận diện CAPTCHA và bằng chứng. | Không sleep cố định cho tải trang; không nuốt lỗi để báo PASS. Commit hạ tầng không gộp nhiều ID testcase. |
| 4. Negative cơ bản | Lần lượt TC01, TC02, TC03, TC04, TC06, TC09, TC10, TC11 khi oracle đã chốt. | Một ID một commit; xác minh CAPTCHA ẩn. CAPTCHA hiện thì ghi rõ lý do chưa chạy ca cơ bản; không dùng lỗi CAPTCHA để kết luận lỗi tài khoản. |
| 5. Ca phụ thuộc | TC05 khi có Username tồn tại và mật khẩu chắc chắn sai; TC07, TC08, TC12 khi có môi trường thử nghiệm và oracle phù hợp. | Không dùng Username giả để tuyên bố đã kiểm thử tài khoản tồn tại. Payload bảo mật không chạy mặc định trên trang công khai. |
| 6. CAPTCHA thiếu/sai | TC13, TC14, TC15, TC20 trên ô nhập mã `name=captcha`. | TC13/TC20 để rỗng; TC14 có mã chắc chắn sai; TC15 nhập dấu cách. Chứng minh riêng lỗi CAPTCHA. |
| 7. Vòng đời CAPTCHA | TC16, TC17, TC18, TC19, TC21, TC22 khi có mã đúng, TTL, ngưỡng và cơ chế thử nghiệm. | Chứng minh refresh/hết hạn/replay; mã đúng lấy thủ công hoặc cơ chế test chính thức. Không đủ điều kiện thì BLOCKED hoặc chạy assisted. |
| 8. Bàn giao | Chạy tập ca đủ điều kiện, phân tích FAIL, lưu bằng chứng, hoàn thiện README/báo cáo, kiểm tra lịch sử commit. | Có kết quả PASS/FAIL/SKIPPED/BLOCKED, hướng dẫn chạy lại và danh sách phạm vi chưa xác minh. |

## 5. Assertion và quản lý CAPTCHA

1. Mỗi ca bắt đầu bằng browser mới, form sẵn sàng, ba selector được kiểm tra theo trạng thái áp dụng. Ca yêu cầu CAPTCHA chỉ chạy khi ô mã thực sự hiển thị.
2. Sau submit, chờ tín hiệu lỗi/validation đã xác minh rồi kiểm tra trạng thái chưa xác thực theo O1. URL hoặc việc form còn hiển thị không đủ để PASS.
3. Với CAPTCHA, cần bằng chứng mã bị từ chối hoặc được chấp nhận theo mục đích ca. “Sai tài khoản” đơn thuần không chứng minh CAPTCHA được kiểm tra.
4. Chỉ nhập mã qua ô CAPTCHA đã cung cấp. Không dùng dịch vụ giải CAPTCHA, OCR hoặc chỉnh dữ liệu bảo vệ để bypass. Ảnh mã/refresh chỉ được thao tác khi đã khảo sát và có hỗ trợ thực tế.
5. Ca cần người cung cấp mã đúng dùng marker `assisted` và timeout hữu hạn; dữ liệu test chính thức chỉ dùng đúng môi trường được cấp.
6. CAPTCHA không xuất hiện: SKIPPED vì không áp dụng trong phiên. CAPTCHA hiện nhưng thiếu mã/TTL/chính sách: BLOCKED. Báo cáo phân biệt hai trạng thái dù pytest đều biểu diễn bằng skip.
7. Fixture mô phỏng có thể kiểm tra mã xử lý nhưng không thay bằng chứng E2E trên hệ thống đích. Không tự retry submit thất bại vì có thể thay đổi bộ đếm CAPTCHA/lockout.

## 6. Kế hoạch Git

Hiện `.gitignore` chứa `docs/`. Khi triển khai lưu lịch sử, điều chỉnh ignore để theo dõi tài liệu, đồng thời bỏ qua môi trường ảo, `.env`, cache, báo cáo và screenshot. File bị ignore chưa được coi là đã commit.

Commit tài liệu/hạ tầng tách riêng:

```text
docs(testing): update login scope locators and Python structure
chore(test): initialize Python Selenium pytest project
refactor(test): add base test fixtures and page objects
```

Sau đó mỗi commit testcase chỉ thêm/sửa **một ID** cùng phần hỗ trợ trực tiếp cần thiết:

```text
test(login): add TC01 empty credentials validation
test(login): add TC02 missing username validation
test(login): add TC03 missing password validation
test(login): add TC04 invalid credentials rejection
test(login): add TC06 padded invalid username rejection
test(login): add TC09 invalid login using Enter
test(login): add TC10 whitespace username rejection
test(login): add TC11 whitespace password rejection
test(captcha): add TC13 empty captcha validation
```

Áp dụng cùng quy tắc cho các ID còn trong bảng khi đủ điều kiện. Không tạo commit giả cho ca chưa triển khai hoặc ID đã bỏ. TC19 nhiều biến thể vẫn là một commit cho ID đó. Sửa lỗi sau này dùng commit riêng cùng ID, ví dụ `fix(test): correct TC13 captcha error assertion`.

Trước mỗi commit: kiểm tra diff, thu thập test, chạy ca tương ứng nếu đủ điều kiện, xem báo cáo/bằng chứng. Không stage file ngoài phạm vi. Dùng nhánh `codex/login-negative-tests` khi bắt đầu triển khai nếu chưa có nhánh công việc phù hợp.

## 7. Lệnh chạy dự kiến

Các lệnh sẽ được hỗ trợ sau khi tạo dự án, **chưa chạy được với repository hiện tại**. PowerShell tại thư mục dự án:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest --collect-only -q

$env:BASE_URL = 'https://vanphongdientu.utc.edu.vn/Login'
$env:HEADLESS = 'true'
.\.venv\Scripts\python.exe -m pytest src/test/python/e2e/tests/test_login_e2e.py -m "negative and not captcha and not security and not assisted and not test_env_only" --junitxml=reports/login-negative.xml
.\.venv\Scripts\python.exe -m pytest src/test/python/e2e/tests/test_login_e2e.py -k "tc01" --junitxml=reports/tc01.xml
```

Chạy tuần tự sau khi xác nhận oracle, dữ liệu và điều kiện. Lệnh mặc định không kích hoạt TC22 hoặc ca bảo mật. Kết hợp marker với kiểm tra môi trường trong fixture để lệnh `pytest` thông thường cũng không vô tình chạy ca cần môi trường thử nghiệm. Tạo `reports/` khi bắt đầu lần chạy.

README bổ sung lệnh chạy CAPTCHA/môi trường riêng sau khi biết cách cung cấp mã, cơ chế hỗ trợ và cấu hình thực tế.

## 8. Báo cáo và nghiệm thu

Mỗi lần chạy ghi ID, biến thể, thời điểm, môi trường, browser/version, dữ liệu giả, kết quả và lý do. Khi lỗi lưu screenshot/thông tin đủ chẩn đoán; tránh thu thập cookie hoặc dữ liệu tài khoản thật. JUnit XML là đầu ra máy đọc; bảng tổng hợp tách BLOCKED và SKIPPED theo lý do pytest.

- **Hoàn tất dự án kiểm thử:** cấu trúc Python đúng mục 3; cài đặt/thu thập test thành công; README đúng; ca bám ID, oracle, commit và ba trường trong phạm vi.
- **Hoàn tất xác minh phạm vi:** các ca đủ điều kiện đã chạy, đối chiếu kết quả và có bằng chứng. Còn BLOCKED phải báo rõ phần thiếu, không tuyên bố đã xác minh toàn bộ CAPTCHA/chức năng.

Đầu vào còn thiếu: kiểm chứng DOM của các selector; locator submit/lỗi/ảnh mã/refresh; Username tồn tại cho TC05; môi trường phù hợp cho payload và reset/kích hoạt; mã CAPTCHA thử nghiệm, TTL, chính sách refresh/replay, ngưỡng N. Có thể làm khung dự án và ca độc lập trong khi các mục này chưa có.

Yêu cầu hiện tại chỉ cập nhật tài liệu và cấu trúc dự kiến trong plan; chưa tạo project, thực thi testcase hoặc tạo commit.


