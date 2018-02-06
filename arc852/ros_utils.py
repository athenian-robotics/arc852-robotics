from geometry_msgs.msg import Twist


def new_twist(linear_x, angular_z):
    t = Twist()
    t.linear.x = linear_x
    t.linear.y = 0
    t.linear.z = 0
    t.angular.x = 0
    t.angular.y = 0
    t.angular.z = angular_z
    return t
