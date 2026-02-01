import numpy as np
from dataclasses import dataclass
from ikpy.chain import Chain
from ikpy.link import OriginLink, URDFLink
import config

@dataclass
class RobotArmConfig:
    base_height: float = config.ARM_BASE_HEIGHT
    shoulder_z_offset: float = config.ARM_SHOULDER_OFFSET_Z
    upper_arm_length: float = config.ARM_UPPER_ARM_LEN
    forearm_length: float = config.ARM_FOREARM_LEN

    servo_min_level: int = config.SERVO_MIN_VAL
    servo_max_level: int = config.SERVO_MAX_VAL

    # 初始姿态
    home_angles: tuple = (0, np.pi / 2, np.pi / 2, np.pi / 2, 0)

    def build_chain(self) -> Chain:
        """
        数构建 IKPy Chain
        """
        return Chain(name='bottle_arm', links=[
            OriginLink(),
            URDFLink(
                name="base",
                bounds=(0, np.pi),
                origin_translation=np.array([0, 0, self.base_height]),
                origin_orientation=np.array([0, 0, -np.pi / 2]),
                rotation=np.array([0, 0, 1])
            ),
            URDFLink(
                name="shoulder",
                bounds=(0, np.pi),
                origin_translation=np.array([0, 0, self.shoulder_z_offset]),
                origin_orientation=np.array([-np.pi / 2, 0, 0]),
                rotation=np.array([1, 0, 0])
            ),
            URDFLink(
                name="elbow",
                bounds=(0, np.pi),
                origin_translation=np.array([0, self.upper_arm_length, 0]),
                origin_orientation=np.array([-np.pi / 2, 0, 0]),
                rotation=np.array([1, 0, 0])
            ),
            URDFLink(
                name="tip",
                bounds=(0, 0.001),
                origin_translation=np.array([0, self.forearm_length, 0]),
                origin_orientation=np.array([0, 0, 0]),
                rotation=np.array([0, 0, 0])
            ),
        ])
