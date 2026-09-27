import unittest

class TestWhatsAppEnquiryFormat(unittest.TestCase):
    def test_whatsapp_message_formatting(self):
        template = "Hi, I am interested in the following lighting fixtures:\n{product_list}\nPlease share more details and pricing."
        
        products = [
            {"id": "shp_81001", "name": "Aura Sculptural Travertine & Frosted Glass Table Lamp", "url": "http://localhost:8000/#product=shp_81001"},
            {"id": "shp_81002", "name": "Kyoto Ribbed Terracotta Table Lamp", "url": "http://localhost:8000/#product=shp_81002"},
            {"id": "wc_501", "name": "Bespoke Fluted Amber Glass & Walnut Base Table Lamp", "url": "http://localhost:8000/#product=wc_501"}
        ]
        
        lines = []
        for idx, p in enumerate(products):
            lines.append(f"{idx + 1}. {p['name']} - {p['url']}")
            
        formatted_message = template.replace("{product_list}", "\n".join(lines))
        
        expected = "Hi, I am interested in the following lighting fixtures:\n1. Aura Sculptural Travertine & Frosted Glass Table Lamp - http://localhost:8000/#product=shp_81001\n2. Kyoto Ribbed Terracotta Table Lamp - http://localhost:8000/#product=shp_81002\n3. Bespoke Fluted Amber Glass & Walnut Base Table Lamp - http://localhost:8000/#product=wc_501\nPlease share more details and pricing."
        
        self.assertEqual(formatted_message, expected)
        print("\n--- FORMATTED WHATSAPP LIGHTING ENQUIRY MESSAGE TEST PASSED ---")
        print(formatted_message)
        print("----------------------------------------------------------------")

if __name__ == "__main__":
    unittest.main()
