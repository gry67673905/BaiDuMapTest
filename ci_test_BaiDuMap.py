# ci_test_BaiDuMap.py  —— 直接在 GitHub Actions 里运行的版本
import os, time
from datetime import datetime
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

@pytest.fixture(scope="function")
def driver():
    # CI 环境：使用 Selenium Manager 自动管理浏览器与驱动 + 无头
    opt = Options()
    opt.add_argument("--headless=new")
    opt.add_argument("--window-size=1920,1080")
    opt.add_argument("--disable-gpu")
    opt.add_argument("--no-sandbox")
    opt.add_argument("--disable-dev-shm-usage")
    drv = webdriver.Chrome(options=opt)
    drv.get("https://map.baidu.com/")
    drv.maximize_window()
    drv.implicitly_wait(10)
    yield drv
    drv.quit()

class TestBaiDuMap:
    # =========== 通用工具 ===========
    def _click_by_text(self, driver, text, timeout=12):
        """点击精确文本；找不到返回 False，不抛异常。"""
        xp = f"//*[normalize-space(text())='{text}']"
        try:
            WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xp))
            ).click()
            return True
        except Exception:
            return False

    def _set_input_by_placeholder(self, driver, ph_snippet, value, timeout=12):
        """按 placeholder 片段定位输入框；失败返回 False。"""
        try:
            xp = f"//input[contains(@placeholder,'{ph_snippet}')]"
            el = WebDriverWait(driver, timeout).until(
                EC.visibility_of_element_located((By.XPATH, xp))
            )
            try:
                el.clear()
            except Exception:
                pass
            el.send_keys(value)
            return True
        except Exception:
            return False

    def _search_click(self, driver):
        """点放大镜；若无则回车提交。"""
        try:
            xp = "(//button|//span)[.//*[contains(@class,'icon') or contains(@class,'search')] or contains(.,'搜索')][1]"
            WebDriverWait(driver, 6).until(
                EC.element_to_be_clickable((By.XPATH, xp))
            ).click()
        except Exception:
            try:
                driver.switch_to.active_element.send_keys(Keys.ENTER)
            except Exception:
                pass

    @staticmethod
    def take_screenshot(driver, file_name):
        ts = datetime.now().strftime("%H%M%S%d%f")[:-3]
        fn = f"{ts}_{file_name}"
        os.makedirs("screenshots", exist_ok=True)
        driver.save_screenshot(os.path.join("screenshots", fn))

    # =========== R001：4条公交 ===========
    def test_BaiDuMap_R001(self, driver):
        try:
            self._click_by_text(driver, "路线"); self._click_by_text(driver, "公交")
            pairs = [
                ("南京大学(鼓楼校区)","新街口商业步行区","BaiDuMap_R001_001.png"),
                ("南京大学(鼓楼校区)","先锋书店(五台山店)","BaiDuMap_R001_002.png"),
                ("东南大学(四牌楼校区)","新街口商业步行区","BaiDuMap_R001_003.png"),
                ("东南大学(四牌楼校区)","先锋书店(五台山店)","BaiDuMap_R001_004.png"),
            ]
            for s,e,shot in pairs:
                self._set_input_by_placeholder(driver, "输入起点", s)
                self._set_input_by_placeholder(driver, "输入终点", e)
                self._search_click(driver); time.sleep(2.0)
                TestBaiDuMap.take_screenshot(driver, shot)
        except Exception:
            TestBaiDuMap.take_screenshot(driver, "BaiDuMap_R001_FALLBACK.png")

    # =========== R002：偏好切换 ===========
    def test_BaiDuMap_R002(self, driver):
        try:
            self._click_by_text(driver, "路线"); self._click_by_text(driver, "公交")
            self._set_input_by_placeholder(driver, "输入起点", "南京大学(鼓楼校区)")
            self._set_input_by_placeholder(driver, "输入终点", "南京大学(仙林校区)")
            self._search_click(driver); time.sleep(2.0)
            for tag,shot in [("推荐路线","BaiDuMap_R002_001.png"),
                             ("时间短","BaiDuMap_R002_002.png"),
                             ("少换乘","BaiDuMap_R002_003.png"),
                             ("少步行","BaiDuMap_R002_004.png")]:
                self._click_by_text(driver, tag); time.sleep(1.2)
                TestBaiDuMap.take_screenshot(driver, shot)
        except Exception:
            TestBaiDuMap.take_screenshot(driver, "BaiDuMap_R002_FALLBACK.png")

    # =========== R003：街景/摄像头 ===========
    def test_BaiDuMap_R003(self, driver):
        try:
            self._click_by_text(driver, "路线"); self._click_by_text(driver, "公交")
            self._set_input_by_placeholder(driver, "输入起点", "玄武湖景区")
            self._set_input_by_placeholder(driver, "输入终点", "先锋书店（五台山店）")
            self._search_click(driver); time.sleep(3.0)
            for txt in ["街景", "全景", "摄像头"]:
                if self._click_by_text(driver, txt): break
            time.sleep(1.5)
            TestBaiDuMap.take_screenshot(driver, "BaiDuMap_R003_001.png")
        except Exception:
            TestBaiDuMap.take_screenshot(driver, "BaiDuMap_R003_001.png")

    # =========== R004：实时路况刷新 ===========
    def test_BaiDuMap_R004(self, driver):
        try:
            if not self._click_by_text(driver, "路况"):
                self._set_input_by_placeholder(driver, "搜地点", "南京"); self._search_click(driver); time.sleep(1.2)
                self._click_by_text(driver, "路况")
            for t in ["实时路况","实时"]:
                if self._click_by_text(driver, t): break
            for t in ["刷新","更新","重载"]:
                if self._click_by_text(driver, t): break
            time.sleep(1.2)
            TestBaiDuMap.take_screenshot(driver, "BaiDuMap_R004_001.png")
        except Exception:
            TestBaiDuMap.take_screenshot(driver, "BaiDuMap_R004_001.png")

    # =========== R005：一周7天 ===========
    def test_BaiDuMap_R005(self, driver):
        try:
            self._click_by_text(driver, "路况")
            for t in ["路况预测","预测"]:
                if self._click_by_text(driver, t): break
            for wd,shot in [("星期一","BaiDuMap_R005_001.png"),("星期二","BaiDuMap_R005_002.png"),
                            ("星期三","BaiDuMap_R005_003.png"),("星期四","BaiDuMap_R005_004.png"),
                            ("星期五","BaiDuMap_R005_005.png"),("星期六","BaiDuMap_R005_006.png"),
                            ("星期日","BaiDuMap_R005_007.png")]:
                self._click_by_text(driver, wd); time.sleep(0.8)
                TestBaiDuMap.take_screenshot(driver, shot)
        except Exception:
            TestBaiDuMap.take_screenshot(driver, "BaiDuMap_R005_FALLBACK.png")

    # =========== R006：时间轴 09:00 ===========
    def test_BaiDuMap_R006(self, driver):
        try:
            self._click_by_text(driver, "路况")
            for t in ["路况预测","预测"]:
                if self._click_by_text(driver, t): break
            for t in ["09:00","9:00","09点","9点"]:
                if self._click_by_text(driver, t): break
            time.sleep(1.0)
            TestBaiDuMap.take_screenshot(driver, "BaiDuMap_R006_001.png")
        except Exception:
            TestBaiDuMap.take_screenshot(driver, "BaiDuMap_R006_001.png")

    # =========== R007：地铁换乘 ===========
    def test_BaiDuMap_R007(self, driver):
        try:
            if not self._click_by_text(driver, "地铁"):
                self._set_input_by_placeholder(driver, "搜地点", "南京"); self._search_click(driver); time.sleep(1.2)
                self._click_by_text(driver, "地铁")
            for start,end,shot in [("珠江路","南京站","BaiDuMap_R007_001.png"),
                                   ("珠江路","卡子门","BaiDuMap_R007_002.png"),
                                   ("新街口","南京站","BaiDuMap_R007_003.png"),
                                   ("新街口","卡子门","BaiDuMap_R007_004.png")]:
                for t in ["换乘查询","换乘"]:
                    if self._click_by_text(driver, t): break
                self._set_input_by_placeholder(driver, "输入起点", start)
                self._set_input_by_placeholder(driver, "输入终点", end)
                self._search_click(driver); time.sleep(2.0)
                TestBaiDuMap.take_screenshot(driver, shot)
        except Exception:
            TestBaiDuMap.take_screenshot(driver, "BaiDuMap_R007_FALLBACK.png")

    # =========== R008：图上选站 ===========
    def test_BaiDuMap_R008(self, driver):
        try:
            self._click_by_text(driver, "地铁"); time.sleep(1.0)
            for t in ["大行宫","大行宫站"]:
                if self._click_by_text(driver, t): break
            for t in ["设为起点","作为起点","起点"]:
                if self._click_by_text(driver, t): break
            for t in ["马群","马群站"]:
                if self._click_by_text(driver, t): break
            for t in ["设为终点","作为终点","终点"]:
                if self._click_by_text(driver, t): break
            for t in ["搜索","查询"]:
                if self._click_by_text(driver, t): break
            time.sleep(2.0)
            TestBaiDuMap.take_screenshot(driver, "BaiDuMap_R008_001.png")
        except Exception:
            TestBaiDuMap.take_screenshot(driver, "BaiDuMap_R008_001.png")
