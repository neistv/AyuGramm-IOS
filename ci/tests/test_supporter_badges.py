import json
import struct
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class SupporterBadgeTests(unittest.TestCase):
    def test_compact_seed_keeps_custom_badge_metadata(self):
        data = json.loads((ROOT / "assets" / "ayu_supporters_seed.json").read_text())
        badges = {item["id"]: item["badge"] for item in data["customBadges"]}

        self.assertEqual(badges[1226061708]["documentId"], 5266966399934291023)
        self.assertIn("text", badges[1226061708])
        self.assertIn(5800413909, data["developers"])

    def test_port_preserves_badge_types_and_premium_slot(self):
        patch = (ROOT / "patches" / "ayugram-custom-features.patch").read_text()

        self.assertIn('json["customBadges"]', patch)
        self.assertIn('json["supporterChannels"]', patch)
        self.assertIn("case custom(documentId: Int64, text: String?)", patch)
        self.assertIn("statusIcon = credibilityIcon", patch)
        self.assertIn("titleStatusIcon = .premium", patch)
        self.assertIn("currentStatusIconContent = currentCredibilityIconContent", patch)

    def test_static_badge_assets_use_centerable_square_canvases(self):
        image_set = ROOT / "assets" / "branding" / "ExteraBadge.imageset"
        expected = {
            "extera_badge.png": (16, 16),
            "extera_badge@2x.png": (32, 32),
            "extera_badge@3x.png": (48, 48),
        }

        for name, size in expected.items():
            data = (image_set / name).read_bytes()
            self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
            self.assertEqual(struct.unpack(">II", data[16:24]), size)


if __name__ == "__main__":
    unittest.main()
