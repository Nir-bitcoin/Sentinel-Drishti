Multi-Language Alerts

=====================



Alerts ko local language mein dikhane ka idea tha kyunki

India mein har state ki apni bhasha hai. Judge ne bola tha

India-relevant banane ke liye.



5 languages add kiye - Hindi, Marathi, Tamil, Telugu, English.

Terminal pe sirf EN + HI dikhate hain kyunki output lamba ho jata hai.

Baaki 3 languages ke examples neeche hain.





Supported Languages

\-------------------



&#x20;   en    English     130M speakers

&#x20;   hi    Hindi       600M speakers

&#x20;   mr    Marathi     85M speakers

&#x20;   ta    Tamil       85M speakers

&#x20;   te    Telugu      95M speakers





PII Alert (EN + HI + MR + TA + TE)

\----------------------------------



Same alert har language mein kaise dikhta hai:



&#x20;   EN: BLOCK\_AND\_ALERT - PASTE to personal email

&#x20;   HI: रोकें और सतर्क करें - व्यक्तिगत ईमेल में पेस्ट

&#x20;   MR: थांबवा आणि सतर्क करा - वैयक्तिक ईमेल

&#x20;   TA: தடுத்து எச்சரிக்கவும் - தனிப்பட்ட மின்னஞ்சல்

&#x20;   TE: నిరోధించి హెచ్చరించండి - వ్యక్తిగత ఇమెయిల్





USB Alert

\---------



Yeh USB wala case hai:



&#x20;   EN: BLOCK\_AND\_ALERT - USB file transfer

&#x20;   HI: रोकें और सतर्क करें - यूएसबी फ़ाइल ट्रांसफर

&#x20;   MR: थांबवा आणि सतर्क करा - USB फाइल ट्रान्सफर

&#x20;   TA: தடுத்து எச்சரிக்கவும் - USB கோப்பு பரிமாற்றம்

&#x20;   TE: నిరోధించి హెచ్చరించండి - USB ఫైల్ బదిలీ





Note

\----



Terminal demo mein sirf EN aur HI dikhate hain kyunki poora output

bahut lamba ho jata. Baaki 3 languages code mein available hain

(src/reasoning/translator.py) aur UI/dashboard mein dikha sakte hain.



Real translation ke liye Qwen3-1.7B use karenge production mein

(woh multilingual hai). Abhi demo ke liye rule-based mappings hain

kyunki hardware validation pending hai.

