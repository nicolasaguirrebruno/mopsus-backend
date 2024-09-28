INSERT_USER_QUERY = """
INSERT INTO `seraphic-camera-436421-v8.mopsus.users` (email, company_name)
VALUES
"""

INSERT_USER_COUNTER_QUERY = """
INSERT INTO `seraphic-camera-436421-v8.mopsus.login_counter` (email, try_counter)
VALUES
"""

RESET_COUNTER_QUERY = """
UPDATE `seraphic-camera-436421-v8.mopsus.login_counter` SET try_counter = 0 WHERE email =
"""

SELECT_COUNTER_QUERY = """
SELECT try_counter FROM `seraphic-camera-436421-v8.mopsus.login_counter` WHERE email =
"""

UPDATE_COUNTER_QUERY = """
UPDATE `seraphic-camera-436421-v8.mopsus.login_counter`
SET try_counter = try_counter + 1 WHERE email =
"""
