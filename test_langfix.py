import unittest
import os
from langfix import analyze_file

class TestLangFix(unittest.TestCase):

    def setUp(self):
        # Create a perfectly safe Python file
        with open("test_good.py", "w") as f:
            f.write('def add(a, b):\n    """Adds two numbers."""\n    return a + b\n')
            
        # Create a dangerous Python file
        with open("test_bad.py", "w") as f:
            f.write('password = "secret123"\n')

    def tearDown(self):
        # Clean up test files
        if os.path.exists("test_good.py"): os.remove("test_good.py")
        if os.path.exists("test_bad.py"): os.remove("test_bad.py")

    def test_good_code(self):
        score, vibe, note = analyze_file("test_good.py")
        self.assertEqual(vibe, "AWESOME")
        self.assertEqual(score, 100)

    def test_security_flaw(self):
        score, vibe, note = analyze_file("test_bad.py")
        self.assertEqual(vibe, "COOKED")
        self.assertEqual(score, 10)
        self.assertIn("Hardcoded secret", note)

if __name__ == '__main__':
    unittest.main()
