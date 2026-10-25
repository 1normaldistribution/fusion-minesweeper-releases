# Minesweeper · 融合版

Android 原生扫雷游戏，提供经典扫雷与一代变体扫雷。

- [下载原生正式版 APK（推荐）](https://github.com/1normaldistribution/fusion-minesweeper-releases/releases/latest)
- [安装与升级](docs/INSTALL.md) · [更新记录](CHANGELOG.md) · [后续计划](ROADMAP.md)
- [报告问题](https://github.com/1normaldistribution/fusion-minesweeper-releases/issues/new/choose)

## 当前版本

**原生正式版 1.0.3**，Android 8.0 及以上，ARM64 设备。界面采用 Android View / Canvas，求解在本机完成，可离线使用。没有账号、广告、付费购买或自动上传。

包含经典扫雷六档难度、变体题组与图鉴、教程、主题与调色、手势操作、绘图笔记、提示、回放、成绩和 JSON 备份。二代《14种扫雷变体 2》已列入后续计划，当前版本尚未加入。

## Web 测试版（已停止更新）

[Web 套壳测试 APK 1.0.2](https://github.com/1normaldistribution/fusion-minesweeper-releases/releases/tag/v1.0.2-web-test) **仅用于测试和对照，不是正式版**，不作为日常使用的推荐下载。它使用 Android WebView，与原生正式版是不同应用，进度不会自动互通。

Web 测试版已封存，此后不再更新或维护；只提供 APK，不发布网站或网页源码包。后续修复与功能更新集中在原生正式版。测试包的静态核对已完成，本次没有补做其新图标、开局和变体加载的真机验收。

## 可复用的开发组件

[Android ARM64 CSugar 适配组件](components/android-csugar/)从游戏实际运行的本机求解层提取，包含构建脚本、C 调用接口、命令行程序、手写约束示例及真机检查工具。无需游戏源码、原题库或原版 DLL，即可独立构建和使用。支持布尔/整数约束、必然结论、解枚举及局部极大解。

这不是完整的变体出题器，也不包含原游戏的专有规则与最小成本提示算法。CSugar/Glucose 的原作者、版本和许可随组件保留；本项目公开的是移植适配工作。

此外保留安装、升级、备份迁移、版本记录与必要的许可说明。问题反馈模板仅用于收集可复现的问题，不把它当作算法开源成果。原先仅描述外层字符串容器的 JSON 规范和泛化验收清单已移除。

本仓库新增适配代码及原创文档按 [MIT 许可](LICENSE)开放。完整游戏实现、原题库、原作素材和签名密钥继续保持私有；APK 与第三方内容不因本仓库 MIT 许可而重新授权。随包许可与署名见[第三方说明](THIRD_PARTY_NOTICES.md)。

## 数据与权限

正式 APK 仅声明振动权限，通过系统文件选择器导入、导出 JSON 文件。卸载或清除应用数据可能丢失进度，请先导出备份。旧测试版和正式版使用不同包名，迁移方法见[安装说明](docs/INSTALL.md)。

[隐私政策](PRIVACY.md) · [使用条款](TERMS.md)
