\# Sentinel Drishti



> \*\*On-Device AI Compliance \& Data Loss Prevention Agent for Snapdragon-Powered HP PCs\*\*



\## 🎯 Problem



Indian enterprises deal with a huge amount of sensitive information every day. Protecting this data is especially difficult in environments where sending information to cloud-based security systems is not suitable because of privacy, compliance, or data-sovereignty requirements.



Many existing DLP solutions depend on cloud infrastructure. This can introduce additional privacy concerns, network dependency, and recurring infrastructure costs.



\*\*Sentinel Drishti\*\* focuses on solving this problem directly on the user's device, keeping sensitive information local instead of sending it to an external cloud service.



\## 💡 Solution



\*\*Sentinel Drishti\*\* is a fully offline, NPU-accelerated AI agent designed to detect sensitive information and potential data-exfiltration attempts directly on a Snapdragon-powered HP PC.



The system analyzes screen content locally, uses an AI model to understand the context of the activity, and decides whether the action should trigger a DLP response.



When a suspicious activity is detected, the system can trigger a physical alert using an Arduino, while also recording the event in a local audit log.



The entire workflow works without requiring an internet connection.



\## 🏗️ Architecture



\### Layer 1: PERCEPTION — NPU



\*\*InternVL3.5-2B\*\* analyzes the screen and identifies relevant sensitive information or content.



\### Layer 2: REASONING — NPU



\*\*Qwen3-1.7B-Instruct\*\* analyzes the detected information and classifies the user's activity or intent.



\### Layer 3: ACTION — CPU + Arduino



The DLP engine applies the required security policy and can trigger a physical alert through Arduino.



The event is also recorded in a local audit log for later review.



\## 🤖 Qualcomm AI Hub Models Used



| Model               | Task                         | NPU Performance |

| ------------------- | ---------------------------- | --------------- |

| InternVL3.5-2B      | Screen content understanding | \~200 ms         |

| Qwen3-1.7B-Instruct | Intent classification        | \~15 tok/s       |



\## 📊 Benchmarks



| Stage                 | CPU Fallback |         NPU | Improvement |

| --------------------- | -----------: | ----------: | ----------: |

| Screen analysis       |    \~2,500 ms |     \~200 ms |        \~12× |

| Intent classification |   \~3–4 tok/s | \~14.9 tok/s |         \~4× |

| End-to-end            |       \~3.5 s |     <500 ms |         \~7× |



> \*\*Note:\*\* Benchmark values depend on the device, model configuration, input size, and runtime environment.



\## 🚀 Setup



\### 1. Clone the repository



```bash

git clone https://github.com/Nir-bitcoin/Sentinel-Drishti.git

cd Sentinel-Drishti

```



\### 2. Install the required dependencies



```bash

pip install -r requirements.txt

```



\### 3. Download the models



```bash

python scripts/download\_models.py

```



\### 4. Start the API



```bash

uvicorn src.api.routes:app --reload

```



\### 5. Run the Arduino simulation



```bash

python simulation/simulated\_arduino.py

```



\## 🎬 Demo



A typical demonstration looks like this:



\*\*PII copy attempt → NPU detects sensitive content → AI evaluates the activity → DLP response is triggered → Arduino activates the buzzer and red LED → event is saved to the local audit log.\*\*



The same workflow can be demonstrated with the system disconnected from Wi-Fi to show that the core detection pipeline operates locally.



\## 🔐 Key Features



\* Fully offline AI processing

\* Snapdragon NPU acceleration

\* Screen content understanding

\* AI-based intent classification

\* Local DLP decision engine

\* Physical security alert using Arduino

\* Local audit logging

\* No cloud dependency for the detection pipeline

\* Designed with enterprise privacy and data-sovereignty requirements in mind



\## 🏆 Challenge



\*\*Snapdragon® AI Lab Build \& Present Challenge 2026\*\*



\## 📜 License



MIT



\## 👤 Author

&#x20;

\*\*Niranjan Vishe\*\*  

GitHub: \[Nir-bitcoin](https://github.com/Nir-bitcoin)

linkdin:\[Nir-vishe](https://www.linkedin.com/in/nirvishe/)

