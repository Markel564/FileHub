import unittest
from functions.windows_to_unix import windows_to_unix_path

class TestOs(unittest.TestCase):

    def test_windows_to_unix_Correct(self):

        wPaths = open("files/windowsPathsCorrect.txt", "r")
        uPaths = open("files/unixPathsCorrect.txt", "r")

        windowsPaths = wPaths.readlines()
        unixPaths = uPaths.readlines()

        for win_path, unix_path in zip(windowsPaths, unixPaths):
            win_path = win_path.strip()
            unix_path = unix_path.strip()
            self.assertEqual(windows_to_unix_path(rf"{win_path}"), unix_path)

        wPaths.close()
        uPaths.close()

if __name__ == "__main__":
    unittest.main()

