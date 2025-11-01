from pathlib import Path
import re

SRC = Path("test_BaiDuMap_filled_fixed.py")
DST = Path("ci_test_BaiDuMap.py")

code = SRC.read_text(encoding="utf-8")

pattern = r"@pytest\.fixture\(scope=\"function\"\)\s*def driver\(\):.*?yield drv\s*\n\s*drv\.quit\(\)\s*"
replacement = r"""@pytest.fixture(scope="function")
def driver():
    # CI 运行：Selenium Manager + Headless
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    opt = Options()
    opt.add_argument("--headless=new")
    opt.add_argument("--window-size=1920,1080")
    opt.add_argument("--disable-gpu")
    opt.add_argument("--no-sandbox")
    opt.add_argument("--disable-dev-shm-usage")

    drv = webdriver.Chrome(options=opt)  # 不传 Service 路径，让 Selenium Manager 处理
    drv.get("https://map.baidu.com/")
    drv.maximize_window()
    drv.implicitly_wait(10)
    yield drv
    drv.quit()
"""
code_ci = re.sub(pattern, replacement, code, flags=re.S)
DST.write_text(code_ci, encoding="utf-8")
print("[ci] ci_test_BaiDuMap.py generated")
