# Minesweeper · 融合版

Android 原生扫雷游戏，提供经典扫雷与一代变体扫雷。

- [下载最新 APK](https://github.com/1normaldistribution/fusion-minesweeper-releases/releases/latest)
- [安装与升级](docs/INSTALL.md) · [更新记录](CHANGELOG.md) · [后续计划](ROADMAP.md)
- [报告问题](https://github.com/1normaldistribution/fusion-minesweeper-releases/issues/new/choose)

## 当前版本

**1.0.0**，Android 8.0 及以上，ARM64 设备。界面采用 Android View / Canvas，求解在本机完成，可离线使用。没有账号、广告、付费购买或自动上传。

包含经典扫雷六档难度、变体题组与图鉴、教程、主题与调色、手势操作、绘图笔记、提示、回放、成绩和 JSON 备份。二代《14种扫雷变体 2》已列入后续计划，当前版本尚未加入。

## 本仓库公开什么

这里公开 APK 下载、版本记录、使用文档、[JSON 备份格式](docs/BACKUP_FORMAT.md)、[结构规范](schemas/native-storage-v1.schema.json)、[验收与复现清单](docs/ACCEPTANCE.md)及问题反馈模板。

原创文档、格式规范和反馈模板以 [MIT 许可](LICENSE)开放，便于复用。游戏实现源码、题库、求解器和原作素材不在此仓库发布。仓库文档许可不适用于 APK 或第三方内容；随包许可与署名见[第三方说明](THIRD_PARTY_NOTICES.md)。

## 数据与权限

正式 APK 仅声明振动权限，通过系统文件选择器导入、导出 JSON 文件。卸载或清除应用数据可能丢失进度，请先导出备份。旧测试版和正式版使用不同包名，迁移方法见[安装说明](docs/INSTALL.md)。

[隐私政策](PRIVACY.md) · [使用条款](TERMS.md)
