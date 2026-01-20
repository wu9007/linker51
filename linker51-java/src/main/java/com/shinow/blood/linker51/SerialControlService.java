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

    /**
     * 发送单个字节（0-20），对应单片机的 compare_value
     */
    public void sendByte(int level) {
        if (comPort != null && comPort.isOpen()) {
            // 将 int 强制转为 byte
            byte[] buffer = new byte[]{(byte) level};
            comPort.writeBytes(buffer, 1);
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
