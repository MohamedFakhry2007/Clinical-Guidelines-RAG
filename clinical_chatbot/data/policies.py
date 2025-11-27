"""
Medical Protocols for the Clinical AI Assistant.

This module contains clinical guidelines and triage protocols
and functions to populate the database.
"""

import logging
from clinical_chatbot.database import add_policy_document, get_all_policy_documents

# Set up logger
logger = logging.getLogger(__name__)

# Standard Medical Protocols (Synthetic Data for Demonstration)
MEDICAL_PROTOCOLS = [
    {
        "title": "بروتوكول التعامل مع ألم الصدر (Chest Pain Protocol)",
        "content": """
1. التقييم الأولي:
- يجب إجراء تخطيط القلب (ECG) خلال 10 دقائق من وصول المريض.
- قياس العلامات الحيوية: ضغط الدم، النبض، وتشبع الأكسجين.

2. الفرز (Triage):
- إذا كان هناك ارتفاع في قطعة ST (STEMI): تفعيل بروتوكول القسطرة فوراً.
- إذا لم يكن هناك ارتفاع (NSTEMI/Unstable Angina): إجراء تحليل إنزيمات القلب (Troponin).

3. العلاج الفوري (MONA):
- مورفين (Morphine) إذا استمر الألم.
- أكسجين (Oxygen) إذا كان التشبع أقل من 90%.
- نيتروجليسرين (Nitroglycerin) تحت اللسان.
- أسبرين (Aspirin) 300 مجم مضغ.

4. موانع الاستعمال:
- تجنب النيتروجليسرين إذا كان ضغط الدم الانقباضي أقل من 90 مم زئبق.
        """
    },
    {
        "title": "بروتوكول الإنتان (Sepsis Protocol - Hour-1 Bundle)",
        "content": """
يجب إتمام الخطوات التالية خلال الساعة الأولى من الاشتباه بالإنتان:

1. قياس مستوى اللاكتات (Lactate Level):
- إعادة القياس إذا كان اللاكتات الأولي > 2 mmol/L.

2. المزارع الدموية (Blood Cultures):
- يجب سحب المزارع قبل بدء المضادات الحيوية.

3. المضادات الحيوية:
- إعطاء مضادات حيوية واسعة الطيف (Broad-spectrum antibiotics) وريدياً فوراً.

4. السوائل الوريدية:
- إعطاء 30 مل/كجم من السوائل المتبلورة (Crystalloid) في حالة انخفاض الضغط أو اللاكتات ≥ 4 mmol/L.

5. قابضات الأوعية (Vasopressors):
- استخدام النورأدرينالين للحفاظ على متوسط ضغط شرياني (MAP) ≥ 65 mm Hg.
        """
    },
    {
        "title": "إدارة ارتفاع ضغط الدم الطارئ (Hypertensive Crisis)",
        "content": """
التعريف: ارتفاع ضغط الدم الانقباضي > 180 أو الانبساطي > 120.

1. الطوارئ (Emergency) مقابل الإلحاح (Urgency):
- Emergency: وجود تلف في الأعضاء المستهدفة (دماغ، قلب، كلى). يتطلب خفض الضغط فوراً عبر الوريد (IV).
- Urgency: لا يوجد تلف في الأعضاء. يتم خفض الضغط تدريجياً عبر الفم.

2. الأدوية الوريدية المفضلة (IV):
- Labetalol أو Nicardipine.

3. الهدف العلاجي:
- خفض الضغط بنسبة لا تزيد عن 25% في الساعة الأولى لتجنب نقص التروية الدماغية.
- الهدف هو الوصول لضغط 160/100 خلال 2-6 ساعات.
        """
    },
    {
        "title": "بروتوكول السكتة الدماغية (Stroke Protocol)",
        "content": """
1. التقييم السريع (FAST):
- الوجه (Face)، الذراع (Arm)، الكلام (Speech)، الوقت (Time).

2. التصوير:
- إجراء أشعة مقطعية (CT Brain Non-contrast) فوراً لاستبعاد النزيف.

3. العلاج المذيب للجلطة (tPA):
- يُعطى إذا كان وقت بدء الأعراض أقل من 4.5 ساعات.
- استبعاد وجود نزيف في الأشعة.
- ضغط الدم يجب أن يكون أقل من 185/110 قبل البدء.

4. المراقبة:
- فحص عصبي كل 15 دقيقة خلال الساعة الأولى.
- ممنوع إعطاء مضادات الصفائح (Aspirin) خلال 24 ساعة من إعطاء tPA.
        """
    }
]

def populate_database():
    """
    Populate the database with Medical Protocols.
    """
    logger.info("Checking if database needs to be populated with medical protocols")
    
    existing_docs = get_all_policy_documents()
    
    if existing_docs:
        logger.info(f"Database already contains {len(existing_docs)} documents")
        return
    
    logger.info("Populating database with Medical Protocols")
    
    for protocol in MEDICAL_PROTOCOLS:
        doc_id = add_policy_document(protocol["title"], protocol["content"])
        if doc_id:
            logger.debug(f"Added protocol '{protocol['title']}' with ID {doc_id}")
        else:
            logger.error(f"Failed to add protocol '{protocol['title']}'")
    
    logger.info(f"Successfully added {len(MEDICAL_PROTOCOLS)} protocols to the database")