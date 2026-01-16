#!/usr/bin/env python3
"""
Unitree Go2 WASD Keyboard Controller

Controls:
  W/S: Forward/Backward
  A/D: Turn Left/Right
  Q/E: Strafe Left/Right
  Space: Stop
  C: Crouch (lower stance)
  V: Stand tall (raise stance)
  1-4: Speed presets (0.2, 0.4, 0.6, 0.8 m/s)
  R: Reset to default stance
  ESC/Ctrl+C: Quit
"""

import sys
import termios
import tty
import select
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Pose

# Key mappings
MOVE_BINDINGS = {
    'w': (1.0, 0.0, 0.0),   # Forward
    's': (-1.0, 0.0, 0.0),  # Backward
    'a': (0.0, 0.0, 1.0),   # Turn left
    'd': (0.0, 0.0, -1.0),  # Turn right
    'q': (0.0, 1.0, 0.0),   # Strafe left
    'e': (0.0, -1.0, 0.0),  # Strafe right
    'W': (1.0, 0.0, 0.0),   # Forward (caps)
    'S': (-1.0, 0.0, 0.0),  # Backward (caps)
    'A': (0.0, 0.0, 1.0),   # Turn left (caps)
    'D': (0.0, 0.0, -1.0),  # Turn right (caps)
    'Q': (0.0, 1.0, 0.0),   # Strafe left (caps)
    'E': (0.0, -1.0, 0.0),  # Strafe right (caps)
}

SPEED_BINDINGS = {
    '1': 0.2,
    '2': 0.4,
    '3': 0.6,
    '4': 0.8,
}

HELP_MSG = """
╔══════════════════════════════════════════════════════════════╗
║              UNITREE GO2 WASD CONTROLLER                      ║
╠══════════════════════════════════════════════════════════════╣
║  Movement:                                                    ║
║    W/S     : Forward / Backward                             ║
║    A/D     : Turn Left / Turn Right                         ║
║    Q/E     : Strafe Left / Strafe Right                     ║
║    SPACE   : Emergency Stop                                 ║
║                                                              ║
║  Stance:                                                     ║
║    C       : Crouch (lower body height)                     ║
║    V       : Stand Tall (raise body height)                 ║
║    R       : Reset to default stance                        ║
║                                                              ║
║  Speed Presets:                                             ║
║    1       : Slow (0.2 m/s)                                 ║
║    2       : Medium (0.4 m/s)                               ║
║    3       : Fast (0.6 m/s)                                 ║
║    4       : Very Fast (0.8 m/s)                            ║
║                                                              ║
║  ESC / Ctrl+C : Quit                                        ║
╚══════════════════════════════════════════════════════════════╝
"""


class Go2WasdController(Node):
    """WASD Keyboard controller for Unitree Go2 robot."""
    
    def __init__(self):
        super().__init__('go2_wasd_controller')
        
        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.body_pose_pub = self.create_publisher(Pose, 'body_pose', 10)
        
        # Movement parameters
        self.linear_speed = 0.4  # m/s
        self.angular_speed = 1.0  # rad/s
        self.strafe_speed = 0.3  # m/s
        
        # Stance parameters
        self.body_height = 0.0  # offset from nominal
        self.height_step = 0.05 # smaller steps for finer control
        self.min_height = -0.5
        self.max_height = 0.5
        
        # Current velocity state
        self.linear_x = 0.0
        self.linear_y = 0.0
        self.angular_z = 0.0
        
        # Terminal settings
        self.settings = termios.tcgetattr(sys.stdin)
        
        self.get_logger().info('Go2 WASD Controller initialized')
        self.get_logger().info(f'Linear speed: {self.linear_speed} m/s, Angular speed: {self.angular_speed} rad/s')
        
    def get_key(self, timeout=0.1):
        """Read a single keypress with timeout."""
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], timeout)
        if rlist:
            key = sys.stdin.read(1)
        else:
            key = ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key
    
    def publish_velocity(self):
        """Publish current velocity command."""
        msg = Twist()
        msg.linear.x = self.linear_x * self.linear_speed
        msg.linear.y = self.linear_y * self.strafe_speed
        msg.angular.z = self.angular_z * self.angular_speed
        self.cmd_vel_pub.publish(msg)
        
    def publish_body_height(self):
        """Publish body height command via Pose."""
        msg = Pose()
        msg.position.z = self.body_height
        msg.orientation.w = 1.0 # Valid quaternion
        self.body_pose_pub.publish(msg)
        
    def stop(self):
        """Stop all movement."""
        self.linear_x = 0.0
        self.linear_y = 0.0
        self.angular_z = 0.0
        self.publish_velocity()
        
    def crouch(self):
        """Lower body height."""
        self.body_height = max(self.min_height, self.body_height - self.height_step)
        self.get_logger().info(f'Body height offset: {self.body_height:.2f}')
        
    def stand_tall(self):
        """Raise body height."""
        self.body_height = min(self.max_height, self.body_height + self.height_step)
        self.get_logger().info(f'Body height offset: {self.body_height:.2f}')
        
    def reset_stance(self):
        """Reset to default stance."""
        self.body_height = 0.0
        self.stop()
        self.get_logger().info('Reset to default stance')
        
    def set_speed(self, speed):
        """Set linear movement speed."""
        self.linear_speed = speed
        self.get_logger().info(f'Speed set to {speed} m/s')
        
    def run(self):
        """Main control loop."""
        print(HELP_MSG)
        print(f"\nCurrent speed: {self.linear_speed} m/s")
        print("Waiting for key input...")
        
        try:
            while rclpy.ok():
                key = self.get_key(timeout=0.1) # 10Hz loop approx
                
                if key == '\x03' or key == '\x1b':  # Ctrl+C or ESC
                    self.stop()
                    print("\nExiting...")
                    break
                    
                if key == ' ':  # Space - stop
                    self.stop()
                    print("STOP!")
                    
                elif key in MOVE_BINDINGS:
                    x, y, z = MOVE_BINDINGS[key]
                    self.linear_x = x
                    self.linear_y = y
                    self.angular_z = z
                    
                elif key in SPEED_BINDINGS:
                    self.set_speed(SPEED_BINDINGS[key])
                    
                elif key == 'c' or key == 'C':
                    self.crouch()
                    
                elif key == 'v' or key == 'V':
                    self.stand_tall()
                    
                elif key == 'r' or key == 'R':
                    self.reset_stance()
                    
                # Always publish in every loop iteration (watchdog heartbeat)
                self.publish_velocity()
                self.publish_body_height()
                        
        except Exception as e:
            self.get_logger().error(f'Error: {e}')
        finally:
            self.stop()
            self.publish_body_height()
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)


def main(args=None):
    rclpy.init(args=args)
    
    try:
        controller = Go2WasdController()
        controller.run()
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
