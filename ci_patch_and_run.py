import io, re, sys, os, shutil, textwrap

SRC = "test_BaiDuMap_filled.py"
DST = "ci_test_BaiDuMap.py"

code = open(SRC, "r", encoding="utf-8").read()

# 1) 强制使用 Selenium Manager + headless，替换 driver fixture
pattern = r"@pytest\.fixture\(\s*scope=\"function\"\s*\)\s*def driver\(\):.*?return driver\s*"
new_fixture = r'''
@pytest.fixture(scope="function")
def driver():
    # CI 运行：使用 Selenium Manager 自动处理驱动 + Headless 模式
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # 关键点：不传 executable_path，交给 Selenium Manager 自动下载/管理
    drv = webdriver.Chrome(options=options)
    drv.get("https://map.baidu.com/")
    drv.maximize_window()
    drv.implicitly_wait(10)
    yield drv
    drv.quit()
'''
code2 = re.sub(pattern, new_fixture, code, flags=re.S)

# 2) 输出到 CI 版本
open(DST, "w", encoding="utf-8").write(code2)
print(f"[ci] Patched test written to {DST}")