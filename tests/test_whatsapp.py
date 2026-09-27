import unittest

class TestWhatsAppEnquiryFormat(unittest.TestCase):
    def test_whatsapp_message_formatting(self):
        template = "Hi, I am interested in the following products:\n{product_list}\nPlease share more details and pricing."
        
        products = [
            {"id": "shp_81001", "name": "Royal Isfahan Masterpiece Pure Silk Carpet", "url": "http://localhost:8000/#product=shp_81001"},
            {"id": "shp_81002", "name": "Antique Tabriz Floral Medallion Rug", "url": "http://localhost:8000/#product=shp_81002"},
            {"id": "wc_501", "name": "Bespoke Royal Jaipur Hand-Tufted Wool Rug", "url": "http://localhost:8000/#product=wc_501"}
        ]
        
        lines = []
        for idx, p in enumerate(products):
            lines.append(f"{idx + 1}. {p['name']} - {p['url']}")
            
        formatted_message = template.replace("{product_list}", "\n".join(lines))
        
        expected_start = "Hi, I am interested in the following products:\n1. Royal Isfahan Masterpiece Pure Silk Carpet - http://localhost:8000/#product=shp_81001\n2. Antique Tabriz Floral Medallion Rug - http://localhost:8000/#product=shp_81002\n3. Bespoke Royal Jaipur Hand-Tufted Wool Rug - http://localhost:8000/#product=wc_501\nPlease share more details and pricing."
        
        self.assertEqual(formatted_message, expected_start)
        print("\n--- FORMATTED WHATSAPP ENQUIRY MESSAGE TEST PASSED ---")
        print(formatted_message)
        print("------------------------------------------------------")

if __name__ == "__main__":
    unittest.main()
