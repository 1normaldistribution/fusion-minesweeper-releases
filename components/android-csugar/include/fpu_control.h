#pragma once
// Glucose includes this glibc-only header on every Linux target. Its library
// sources never use the x87 control APIs (only its unused command-line mains do).
// Android ARM64 has no x87 FPU, so no compatibility definitions are needed.
#if !defined(__ANDROID__) || !defined(__aarch64__)
#error This include adapter is only valid for Android ARM64.
#endif
