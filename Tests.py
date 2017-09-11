from Bodies import *

def test_body_movement(): # Testing body movement behavior
    try:
        test_body = Body(0, (0, 0), (2, 0))
        test_body.apply_velocity(2.5)
        assert test_body.position == (5, 0)
        test_body.acceleration = V2(0, 1)
        test_body.apply_velocity(2.5)
        assert test_body.position == (10, 0)
        test_body.apply_acceleration(5)
        test_body.apply_velocity(1)
        assert test_body.position == (12, 5)
        print("Body movement - SUCCESS")
        return 0
    except:
        print("Body movement - FAILED")
        return -1

test_body_movement()
