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
     * 向电机发送命令
     */
    @GetMapping("/motor")
    public String controlMotor(@RequestParam String action) {
        serialService.sendCommand(action);
        return "指令 " + action + " 已发送至电机";
    }
}
