import os
import sys
import time
import zipfile
import subprocess
import shutil
from pathlib import Path

class ZIPWordlistTester:
    def __init__(self):
        self.wordlist_path = "rockyou.txt"
        self.attempts = 0
        self.start_time = None
        self.colors = self.setup_colors()

    def setup_colors(self):
        """Setup ANSI color codes"""
        return {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'reset': '\033[0m',
            'bold': '\033[1m'
        }

    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')

    def print_header(self):
        """Display the framed header"""
        header = "**********Cracking...***********"
        print(f"{self.colors['blue']}{header}{self.colors['reset']}")

    def print_footer(self):
        """Display the framed footer"""
        footer = "**********************************"
        print(f"{self.colors['blue']}{footer}{self.colors['reset']}")

    def print_status(self, password, status, message=""):
        """Display current attempt status"""
        status_color = self.colors['green'] if status == "Accepted" else self.colors['red']
        status_symbol = "✓" if status == "Accepted" else "X"

        status_line = f"trying: {password} : ({status_color}{status_symbol}{self.colors['reset']})"
        if message:
            status_line += f" {message}"

        print(status_line)


        meta_info = f"Attempt: {self.attempts}"
        if self.start_time:
            elapsed = time.time() - self.start_time
            meta_info += f" | Time: {elapsed:.2f}s"
        print(f"{self.colors['yellow']}{meta_info}{self.colors['reset']}")

    def check_7z_available(self):
        """Check if 7z is available in system PATH"""
        return shutil.which("7z") is not None

    def test_password_zipfile(self, zip_path, password):
        """
        Test password using Python's zipfile module.
        Returns: (is_correct, method_description)
        """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                if not zip_file.namelist():
                    return False, "Empty archive"

                first_file = zip_file.namelist()[0]

                test_content = zip_file.read(first_file, pwd=password.encode('utf-8'))

                try:
                    test_content.decode('utf-8', errors='strict')
                    is_likely_text = True
                except:
                    is_likely_text = False

                return True, "ZipCrypto"

        except RuntimeError as e:
            if "password" in str(e).lower() or "bad password" in str(e).lower():
                return False, "ZipCrypto - Bad password"
            else:
                return False, f"ZipCrypto - Error: {str(e)}"
        except zipfile.BadZipFile:
            return False, "Invalid ZIP file"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def test_password_7z(self, zip_path, password):
        """Test password using 7z command-line tool"""
        try:
            result = subprocess.run([
                "7z", "t", f"-p{password}", zip_path
            ], capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                return True, "7z"
            elif result.returncode == 1:
                return False, "7z - Wrong password"
            else:
                return False, f"7z - Error code {result.returncode}"

        except subprocess.TimeoutExpired:
            return False, "7z timeout"
        except Exception as e:
            return False, f"7z error: {str(e)}"

    def test_password(self, zip_path, password):
        """Test password with fallback logic - ONLY return True if password is definitely correct"""
        result, method = self.test_password_zipfile(zip_path, password)

        if result is True:
            if self.check_7z_available():
                result_7z, method_7z = self.test_password_7z(zip_path, password)
                if result_7z:
                    return True, f"Verified with {method} + 7z"
                else:
                    return False, f"{method} but 7z disagrees"
            return True, method
        else:
            if self.check_7z_available():
                result_7z, method_7z = self.test_password_7z(zip_path, password)
                return result_7z, method_7z

            return False, method

    def validate_zip_file(self, zip_path):
        """Validate that the ZIP file is accessible and has content"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as test_zip:
                file_list = test_zip.namelist()
                if not file_list:
                    print(f"{self.colors['red']}Error: ZIP file is empty{self.colors['reset']}")
                    return False

                try:
                    test_zip.read(file_list[0])
                    print(f"{self.colors['yellow']}Warning: ZIP file appears to be unencrypted{self.colors['reset']}")
                    time.sleep(2)
                except RuntimeError:
                    pass

                return True
        except zipfile.BadZipFile:
            print(f"{self.colors['red']}Error: File is not a valid ZIP archive{self.colors['reset']}")
            return False
        except Exception as e:
            print(f"{self.colors['red']}Error accessing ZIP file: {str(e)}{self.colors['reset']}")
            return False

    def validate_inputs(self, zip_path):
        """Validate that required files exist"""
        if not os.path.exists(zip_path):
            print(f"{self.colors['red']}Error: ZIP file '{zip_path}' not found{self.colors['reset']}")
            return False

        if not os.path.exists(self.wordlist_path):
            print(f"{self.colors['red']}Error: Wordlist '{self.wordlist_path}' not found{self.colors['reset']}")
            print("Please ensure rockyou.txt is in the same directory as this script")
            return False

        if not self.validate_zip_file(zip_path):
            return False

        return True

    def show_success(self, password, method):
        """Display success message with optional system features"""
        self.clear_screen()

        if shutil.which("figlet"):
            os.system(f'figlet "PASSWORD FOUND"')
        elif shutil.which("toilet"):
            os.system(f'toilet "PASSWORD FOUND"')
        else:
            print(f"{self.colors['green']}{'*' * 50}{self.colors['reset']}")
            print(f"{self.colors['green']}*** PASSWORD FOUND ***{self.colors['reset']}")
            print(f"{self.colors['green']}{'*' * 50}{self.colors['reset']}")

        print(f"\n{self.colors['green']}Password: {self.colors['bold']}{password}{self.colors['reset']}")
        print(f"Method: {method}")
        print(f"Total attempts: {self.attempts}")
        print(f"Total time: {time.time() - self.start_time:.2f} seconds")

        print(f"\n{self.colors['yellow']}Verifying password one more time...{self.colors['reset']}")
        final_result, final_method = self.test_password(sys.argv[1], password)
        if final_result:
            print(f"{self.colors['green']}✓ Password verified successfully{self.colors['reset']}")
        else:
            print(f"{self.colors['red']}✗ Password verification failed!{self.colors['reset']}")
            print(f"{self.colors['red']}This indicates a false positive - please investigate{self.colors['reset']}")

        if shutil.which("notify-send"):
            os.system(f'notify-send "ZIP Wordlist Tester" "Password found: {password}"')

        if shutil.which("paplay"):
            os.system("paplay /usr/share/sounds/freedesktop/stereo/complete.oga 2>/dev/null || true")

        print(f"\n{self.colors['yellow']}Press Enter to exit...{self.colors['reset']}")
        input()

    def run(self, zip_path):
        """Main execution function"""
        if not self.validate_inputs(zip_path):
            sys.exit(1)

        self.start_time = time.time()
        seven_zip_available = self.check_7z_available()

        print(f"{self.colors['yellow']}7z available: {seven_zip_available}{self.colors['reset']}")
        print(f"{self.colors['yellow']}Starting attack on {zip_path}{self.colors['reset']}")
        time.sleep(2)

        try:
            with open(self.wordlist_path, 'r', encoding='utf-8', errors='ignore') as wordlist:
                for line in wordlist:
                    password = line.strip()
                    if not password:
                        continue

                    self.attempts += 1
                    self.clear_screen()
                    self.print_header()

                    result, method = self.test_password(zip_path, password)

                    if result:
                        self.print_status(password, "Accepted", f"[{method}]")
                        self.print_footer()
                        self.show_success(password, method)
                        return
                    else:
                        self.print_status(password, "Failed", f"[{method}]")
                        self.print_footer()

                    time.sleep(0.01)

            self.clear_screen()
            print(f"{self.colors['red']}No matching password found in wordlist{self.colors['reset']}")
            print(f"Total attempts: {self.attempts}")
            print(f"Total time: {time.time() - self.start_time:.2f} seconds")

        except KeyboardInterrupt:
            print(f"\n{self.colors['yellow']}Process interrupted by user{self.colors['reset']}")
            print(f"Attempts made: {self.attempts}")
            print(f"Time elapsed: {time.time() - self.start_time:.2f} seconds")

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <target.zip>")
        print("FOR AUTHORIZED USE ONLY - EDUCATIONAL PURPOSES")
        sys.exit(1)

    zip_path = sys.argv[1]

    print("\n" + "="*60)
    print("ZIP Wordlist Tester - FOR AUTHORIZED USE ONLY")
    print("Use only on files you own or have explicit permission to test")
    print("="*60)
    print("Press Ctrl+C to abort at any time")
    print("="*60)
    time.sleep(3)

    tester = ZIPWordlistTester()
    tester.run(zip_path)

if __name__ == "__main__":
    main()
