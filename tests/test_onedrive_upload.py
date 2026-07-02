import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from modules.onedrive import upload_file


class OneDriveUploadTests(unittest.TestCase):
    def test_upload_file_uses_upload_session_for_large_files(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            local_file = os.path.join(tmp_dir, "big.bin")
            with open(local_file, "wb") as handle:
                handle.write(b"x" * (5 * 1024 * 1024))

            with mock.patch("modules.onedrive.requests.post") as mock_post, \
                 mock.patch("modules.onedrive.requests.put") as mock_put:

                mock_post.return_value.status_code = 200
                mock_post.return_value.json.return_value = {
                    "uploadUrl": "https://example.test/upload"
                }
                mock_post.return_value.raise_for_status.return_value = None

                mock_put.return_value.status_code = 200
                mock_put.return_value.json.return_value = {"id": "item-123"}
                mock_put.return_value.raise_for_status.return_value = None

                item_id = upload_file("token", "user@example.com", local_file, "folder", "big.bin")

                self.assertEqual(item_id, "item-123")
                self.assertEqual(mock_post.call_count, 1)
                self.assertGreaterEqual(mock_put.call_count, 1)


if __name__ == "__main__":
    unittest.main()
