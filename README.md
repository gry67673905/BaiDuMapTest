# BaiduMap Test – Cloud Runner

本仓库用于 **零安装** 运行百度地图测试脚本：使用 GitHub Actions 在云端执行 Selenium（headless），生成 `screenshots/` 和回填 Excel。

## 使用方法（仅需 3 步）
1. 把本仓库上传到你自己的 GitHub 账号（或新建空仓库后上传这些文件）。
2. 在仓库页面点击 **Actions** → 选择 **Run BaiduMap Tests** → **Run workflow**。
3. 等待工作流完成后，在 **Artifacts** 下载：
   - `screenshots.zip`（以及 `screenshots` 整个文件夹）
   - `BaiDuMap_测试用例_提交版.xlsx`

> 说明：提交给比赛的平台仍使用根目录下的 `test_BaiDuMap_filled.py`（其驱动路径保留为官方路径），云端运行时会生成一个仅用于 CI 的 `ci_test_BaiDuMap.py`，以便在云端通过 Selenium Manager 自动处理浏览器与驱动，并启用无头模式。

## 仓库结构
- `test_BaiDuMap_filled.py` – 官方模板基础上已填充 8 个测试函数（R001-R008）
- `update_case_screenshots.py` – 回填 Excel 的截图文件名
- `BaiDuMap_测试用例_初稿.xlsx` – 已填好 22 条用例
- `.github/workflows/run.yml` – 云端执行脚本
- `ci_patch_and_run.py` – 生成并运行 `ci_test_BaiDuMap.py` 的小工具脚本