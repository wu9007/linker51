package com.shinow.blood.linker51;

import com.fazecast.jSerialComm.SerialPort;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import org.springframework.stereotype.Service;

@Service
public class SerialControlService {
    private SerialPort comPort;

    /**
     * 项目启动时自动初始化串口
     */
    @PostConstruct
    public void init() {
        comPort = SerialPort.getCommPort("COM4");
        comPort.setBaudRate(9600);
        if (comPort.openPort()) {
            System.out.println("成功连接到51单片机！");
        }
    }

    public void sendCommand(String cmd) {
        if (comPort != null && comPort.isOpen()) {
            byte[] bytes = cmd.getBytes();
            comPort.writeBytes(bytes, bytes.length);
        }
    }

    /**
     * 项目关闭时自动释放串口
     */
    @PreDestroy
    public void stop() {
        if (comPort != null) comPort.closePort();
    }
}
