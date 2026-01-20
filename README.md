# Linker51 - 软硬结合电机控制项目
Linker51 是一个基于 Spring Boot 和 51单片机 的控制项目。通过 Java 上位机发送指令，经由串口通信控制下位机驱动直流电机。

## 🛠 硬件环境
- 开发板: 普中 A2 (芯片: STC89C52RC)
- 驱动模块: 板载 ULN2003 驱动电路 
- 负载: 标配小型直流电机 (接 P1.0 引脚)
- 通信接口: 板载 USB 转 TTL (CH340)
- 电脑配置: 识别为 COM4，波特率 9600

## 📂 项目结构
```text
Linker51/
├── linker51-java/    # Spring Boot 4.0.1 (JDK 17 + Gradle 8.14.2)
└── linker51-mcu/     # Keil C51 工程
```
## 🖥 运行指南
### 第一步：硬件连接
1. 将直流电机连接至普中 A2 开发板的 电机接口（对应 P1.0 引脚控制）。 
2. 使用 USB 线将开发板连接至电脑，确认驱动已安装（CH340）。

### 第二步：烧录单片机代码
1. 使用 Keil 编译 linker51-mcu 目录下的源码，生成 .hex 文件。 
2. 打开 STC-ISP 软件，选择单片机型号为 STC89C52RC。 
3. 加载 .hex 文件，点击“下载/编程”，然后给开发板冷启动（重新拨动电源开关）。

### 第三步：启动 Java 上位机
1. 确保已关闭 STC-ISP 的串口占用。 
2. 在 `linker51-java` 目录下使用 Gradle 启动：

```shell
./gradlew bootRun
```
### 第四步：控制电机
通过浏览器访问以下接口即可看到电机反应： 
- 开启电机: http://localhost:8080/motor?action=1
- 关闭电机: http://localhost:8080/motor?action=0

## ⚠️ 避坑说明
- 端口独占: 运行 Java 应用前，必须关闭任何其他占用 COM4 的串口调试工具。 
- 波特率一致性: 源码中 TH1=0xFA 严格对应 11.0592MHz 晶振下的 9600 波特率，请勿修改。 
- 端口号变更: 若设备管理器显示非 COM4，请手动修改 SerialControlService 中的配置。