package com.shinow.blood.linker51;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/vision")
public class VisionController {

    private final SerialControlService serialService;

    public VisionController(SerialControlService serialService) {
        this.serialService = serialService;
    }

    @GetMapping("/update")
    public String handleUpdate(@RequestParam int x, @RequestParam int y) {
        int level;

        if (x < 0) {
            level = 0;
        } else {
            // 映射计算
            level = 5 + (int) ((x / 640.0) * 20);
            // 确保不会超过 25
            level = Math.min(level, 25);
        }

        System.out.printf("坐标(%d, %d) -> 指令 Level: %d%n", x, y, level);

        // 发送给串口
        serialService.sendByte(level);

        return "Level: " + level;
    }
}
