# Android ARM64 CSugar 适配组件

从融合版实际使用的本机求解适配层提取。其他开发者可以构建 `libcsugar.so`，输入布尔/整数约束，取得可行解、必然成立的变量、解枚举或局部极大解。无需安装融合版，无需 .NET、WebView、原版游戏 DLL 或原题库。

CSugar 和 Glucose 均为已有的上游项目。本目录公开的是安卓构建与调用适配，不把上游算法声称为本项目原创；也不包含《14种扫雷变体》的专有规则、提示解释算法或完整出题器。

## 构建并实际运行

需要 Python 3.10+ 和官方 Android NDK（实测 r27c）。

```text
python build.py --ndk /path/to/android-ndk-r27c
python test_device.py --adb /path/to/adb
```

构建默认下载锁定提交的上游文件，逐文件验证 SHA-256；已准备上游目录时可传 `--upstream /path/to/upstream` 离线构建。支持 Windows/Linux/macOS 的 NDK 路径，当前发布前实测构建主机为 Windows。

输出 `build/libcsugar.so`、`build/solver-cli`、构建报告。库的最低 API 为 23，ABI 为 arm64-v8a，ELF LOAD 段按 16KB 对齐；这与游戏 APK 的 Android 8.0 最低版本是两项不同要求。

设备检查只在唯一的 `/data/local/tmp/csugar-component-*` 目录运行手写小例并删除自身文件，不安装应用，不读取或改动游戏进度。多台设备请使用 `--serial`。

## 一个可复用的例子

`examples/clue-inference.csp` 用三个未知格演示相邻数字约束：a+b=1、b+c=1、a+c=0，得到 a、c 安全、b 有雷。没有使用原游戏题目。

```text
adb push build/libcsugar.so /data/local/tmp/
adb push build/solver-cli /data/local/tmp/
adb shell chmod 700 /data/local/tmp/solver-cli
adb shell 'LD_LIBRARY_PATH=/data/local/tmp /data/local/tmp/solver-cli' < examples/clue-inference.csp
```

输出为 `sat`，随后 `a false`、`b true`、`c false`。`test_device.py` 还检查不确定局面、矛盾局面、整数变量、两个解的枚举、局部极大解和错误传递。

## 调用与协议

C ABI 为 `const char* Call(const char*)`，错误信息由 `csugar_last_error()` 返回。返回字符串由库持有，只在下一次调用前有效；立即复制结果。使用静态缓冲区，不可并发调用；宿主须串行调度。原游戏将其放在独立求解进程中，本组件没有移植游戏界面或进度管理。

- `(bool a)` 定义布尔变量，`(int n 0 2)` 定义整数变量；约束使用 CSugar 表达式。
- 无 `#` 行：返回一组可行赋值，或 `s UNSATISFIABLE`。
- `# a b`：只返回在所有解中值不变的目标变量。仅返回 `sat` 表示有解，但目标都不确定。
- `#` 配合 `$2`：最多枚举两组目标赋值。尾部 `unsat` 是本适配协议的结束标记，即使达到数量上限也会输出；不能拿这个标记当成已穷尽所有解的证明。只有在请求至少两解且实际不足两解时，才可据此判断目标投影唯一。
- `$-2`：求布尔目标的局部极大解，按现有协议仅报告值为 false 的目标；它不是最大基数优化，也不是最小成本提示。
- `?` 结束一条请求。CLI 每个进程处理一条请求。

输入应来自可信的约束生成器。上游部分畸形输入会直接结束进程；C ABI 的异常转换不覆盖 abort/exit。需要处理任意外部输入时，应另加输入校验并放在独立进程中。

上游提交、完整文件校验见 `upstream-lock.json`，上游许可见 `licenses/`。本目录新增的适配、构建及示例按仓库 MIT 许可提供；上游源码仍遵循其各自许可。
