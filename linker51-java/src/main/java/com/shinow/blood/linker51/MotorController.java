package com.shinow.blood.linker51;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class MotorController {
    private final SerialControlService serialService;

    public MotorController(SerialControlService serialService) {
        this.serialService = serialService;
    }

    /**
     * 控制电机转速（占空比）
     *
     * @param level 0-20 之间的数字
     */
    @GetMapping("/motor")
    public String controlMotor(@RequestParam int level) {
        // 安全校验
        if (level <= 0) level = 0;
        if (level > 20) level = 20;

        // 发送二进制数值
        serialService.sendByte(level);

        return "电机速度等级已设定为: " + level + " (占空比: " + (level * 5) + "%)";
    }
}
