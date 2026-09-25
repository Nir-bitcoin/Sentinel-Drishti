# translator.py
# 5 languages  - Indian major languages


lang_names = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu",
    
}


class AlertTranslator:

    def __init__(self):
        pass

    def translate(self, text, lang="hi"):
        out = self._translate_rule_based(text, lang)
        return {
            "text": out,
            "language": lang_names.get(lang, "Unknown"),
        }

    def _translate_rule_based(self, text, lang):
        # hindi
        if lang == "hi":
            text = text.replace("BLOCK_AND_ALERT", "रोकें और सतर्क करें")
            text = text.replace("ALLOW", "अनुमति दें")
            text = text.replace("PASTE to personal email", "व्यक्तिगत ईमेल में पेस्ट")
            text = text.replace("USB file transfer", "यूएसबी फ़ाइल ट्रांसफर")
            text = text.replace("Cloud upload", "क्लाउड अपलोड")
            text = text.replace("Message send", "संदेश भेजें")
         # marathi
        elif lang == "mr":
            text = text.replace("BLOCK_AND_ALERT", "रोखा आणि सतर्क करा")
            text = text.replace("ALLOW", "परवानगी द्या")
            text = text.replace("PASTE to personal email", "वैयक्तिक ईमेल")
            text = text.replace("USB file transfer", "USB फाइल ट्रान्सफर")
            text = text.replace("Cloud upload", "क्लाउड अपलोड")
            text = text.replace("Message send", "संदेश पाठवा")

        # tamil
        elif lang == "ta":
            text = text.replace("BLOCK_AND_ALERT", "தடுத்து எச்சரிக்கவும்")
            text = text.replace("ALLOW", "அனுமதி")
            text = text.replace("PASTE to personal email", "தனிப்பட்ட மின்னஞ்சல்")
            text = text.replace("USB file transfer", "USB கோப்பு பரிமாற்றம்")
            text = text.replace("Cloud upload", "கிளவுட் பதிவேற்றம்")
            text = text.replace("Message send", "செய்தி அனுப்பு")

        # telugu
        elif lang == "te":
            text = text.replace("BLOCK_AND_ALERT", "నిరోధించి హెచ్చరించండి")
            text = text.replace("ALLOW", "అనుమతించు")
            text = text.replace("PASTE to personal email", "వ్యక్తిగత ఇమెయిల్")
            text = text.replace("USB file transfer", "USB ఫైల్ బదిలీ")
            text = text.replace("Cloud upload", "క్లౌడ్ అప్లోడ్")
            text = text.replace("Message send", "సందేశం పంపు")

       

        return text


if __name__ == "__main__":
    t = AlertTranslator()
    print(t.translate("BLOCK_AND_ALERT - USB file transfer", "hi"))
    print(t.translate("BLOCK_AND_ALERT - USB file transfer", "ta"))