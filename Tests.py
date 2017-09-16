from Bodies import *

def test_body_movement(): # Testing body movement behavior
    print("Testing body movement...")
    test_body = Body(0, (0, 0), (2, 0))
    test_body.apply_motion(2.5)
    assert test_body.position == (5, 0)
    test_body.acceleration = V2(0, 1)
    test_body.apply_motion(4)
    assert test_body.position == (13, 16)
    test_body.acceleration = V2(0, -1)
    test_body.apply_motion(6)
    assert test_body.position == (25, 4)
    print("Body movement - SUCCESS")

test_body_movement()
