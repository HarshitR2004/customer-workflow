"""
Prompt templates for the 6 sequential steps in the AI Customer Support Workflow.

NOTE: These prompts intentionally incorporate structural inefficiencies:
- Sequential single-purpose calls rather than combined extraction
- Deliberate repetition of previous step results to bloat prompt context
- Full injection of the entire 1,500+ word DemoShop policy manual without RAG or filtering
- Dedicated review and rewrite prompts executing regardless of draft quality
"""

from langchain_core.prompts import PromptTemplate

# ==============================================================================
# Step 1: Complaint Classification Prompt
# ==============================================================================
CLASSIFICATION_TEMPLATE = """You are an automated customer ticket triage classifier for an e-commerce platform called DemoShop.

Your sole responsibility is to classify the incoming customer message into exactly one primary category from the following supported list:
- shipping (delivery delays, lost packages, courier tracking questions, customs issues)
- refunds (money return requests, refund status inquiries, charge discrepancies)
- payments (duplicate transactions, checkout errors, billing statement queries, payment method failures)
- product issues (damaged goods, defective hardware, technical malfunctions, warranty requests)

Customer Message:
\"\"\"{ticket_text}\"\"\"

Instructions:
Identify the primary issue. Respond with ONLY the exact category name in lowercase (shipping, refunds, payments, or product issues). Do not provide conversational filler or explanations.
Category:"""

CLASSIFICATION_PROMPT = PromptTemplate.from_template(CLASSIFICATION_TEMPLATE)


# ==============================================================================
# Step 2: Sentiment Analysis Prompt
# Deliberately kept as a separate LLM call rather than being merged with classification.
# ==============================================================================
SENTIMENT_TEMPLATE = """You are an emotional sentiment analyzer for customer support messages at DemoShop.

Evaluate the emotional state and tone conveyed by the customer in their message.
Possible sentiment classifications:
- positive (happy, satisfied, complimentary, grateful)
- neutral (matter-of-fact, calm, informational inquiry, polite inquiry)
- frustrated (annoyed, impatient, inconvenienced, expressing disappointment)
- angry (outraged, threatening escalation, severe dissatisfaction, demanding immediate action)

Customer Message:
\"\"\"{ticket_text}\"\"\"

Instructions:
Evaluate the sentiment accurately based on punctuation, phrasing, and emotional keywords.
Respond with ONLY one word representing the sentiment: positive, neutral, frustrated, or angry.
Sentiment:"""

SENTIMENT_PROMPT = PromptTemplate.from_template(SENTIMENT_TEMPLATE)


# ==============================================================================
# Step 3: Urgency Detection Prompt
# Deliberately repeats earlier classification and sentiment outputs to demonstrate
# redundant context passing and token bloat.
# ==============================================================================
URGENCY_TEMPLATE = """You are an urgency assessment agent for DemoShop customer support dispatch.

Determine the response priority level for this support case.

[REDUNDANT CONTEXT REPEATED FROM PREVIOUS STEPS]
Original Customer Complaint:
\"\"\"{ticket_text}\"\"\"

Previously Determined Ticket Classification:
{classification}

Previously Evaluated Customer Sentiment:
{sentiment}

Additional System Note:
The ticket has already undergone Step 1 (Classification: {classification}) and Step 2 (Sentiment: {sentiment}).
Given the combination of the customer's issue type ({classification}) and emotional state ({sentiment}), determine how urgently a human or automated agent must respond.

Priority Levels:
- Low (informational inquiries, positive feedback, non-time-sensitive questions)
- Medium (moderate delivery inquiries, minor product issues, polite return requests)
- High (severe shipping delays, damaged items with anger, financial duplicate charges, urgent cancellation windows)

Instructions:
Analyze the repeated context above. Respond with ONLY the urgency level: Low, Medium, or High.
Urgency:"""

URGENCY_PROMPT = PromptTemplate.from_template(URGENCY_TEMPLATE)


# ==============================================================================
# Step 4: Response Generation Prompt
# Deliberately injects the entire knowledge base (thousands of tokens) regardless
# of what category the ticket belongs to, alongside all previous outputs and mock order.
# ==============================================================================
RESPONSE_GENERATION_TEMPLATE = """You are a customer support representative for DemoShop, a premier digital retailer.

Your task is to draft an initial empathetic, informative, and professional response to the customer.

--------------------------------------------------------------------------------
CUSTOMER TICKET DETAILS & ACCUMULATED CONTEXT:
--------------------------------------------------------------------------------
Original Customer Message:
\"\"\"{ticket_text}\"\"\"

Triage Assessment:
- Category: {classification}
- Detected Sentiment: {sentiment}
- Priority / Urgency Level: {urgency}

Associated Order Information:
{order_details}

--------------------------------------------------------------------------------
COMPLETE DEMOSHOP COMPANY POLICY & KNOWLEDGE BASE MANUAL:
(Every representative must consult and abide by the entire company manual below)
--------------------------------------------------------------------------------
{knowledge_base}
--------------------------------------------------------------------------------

Instructions for Response Generation:
1. Address the customer warmly and acknowledge their specific issue.
2. If order details are available, cite the relevant order facts (e.g., tracking number, order status, or delivery date).
3. Apply DemoShop's official policy from the knowledge base above accurately.
4. Maintain a reassuring, supportive tone matching the customer's sentiment.
5. Provide clear, actionable next steps.

Draft Support Response:"""

RESPONSE_GENERATION_PROMPT = PromptTemplate.from_template(RESPONSE_GENERATION_TEMPLATE)


# ==============================================================================
# Step 5: Response Review Prompt
# Reviews the generated response for correctness, tone, and policy adherence.
# ==============================================================================
REVIEW_TEMPLATE = """You are a senior Quality Assurance (QA) supervisor at DemoShop Customer Experience.

Perform a thorough editorial and policy compliance review of the drafted customer support response.

Original Customer Message:
\"\"\"{ticket_text}\"\"\"

Customer Assessment:
- Issue Category: {classification}
- Sentiment: {sentiment}
- Urgency: {urgency}

Mock Order Information:
{order_details}

Draft Customer Response Under Review:
\"\"\"{draft_response}\"\"\"

Review Criteria:
1. Correctness: Does the draft accurately cite the customer's order status and abide by DemoShop policies?
2. Tone: Is the tone empathetic, polite, professional, and well-calibrated to the customer's sentiment ({sentiment})?
3. Clarity & Completeness: Are instructions and next steps unambiguous and free of robotic jargon?

Instructions:
Provide a constructive critique. Identify any weak phrasing, missed details, or opportunities to make the response more helpful.
Format your output as:
- Tone Assessment: <brief critique>
- Policy & Accuracy Check: <brief critique>
- Suggested Improvements: <bulleted list of specific changes to make>"""

REVIEW_PROMPT = PromptTemplate.from_template(REVIEW_TEMPLATE)


# ==============================================================================
# Step 6: Response Rewriting Prompt
# Rewrites the draft into the final customer-facing response based on QA review feedback.
# ==============================================================================
REWRITE_TEMPLATE = """You are DemoShop's lead customer communications specialist.

Rewrite the drafted customer support response into the final polished version, incorporating the QA supervisor's critique and suggested improvements.

Original Customer Message:
\"\"\"{ticket_text}\"\"\"

Draft Response:
\"\"\"{draft_response}\"\"\"

QA Supervisor Review Feedback & Suggested Improvements:
\"\"\"{review_feedback}\"\"\"

Instructions:
Produce the final, ready-to-send customer support response.
- Incorporate all valid critique points from the supervisor review.
- Ensure the greeting is warm, empathetic, clear, and professional.
- State clear solutions and concrete next steps.
- Sign off professionally as "DemoShop Support Team".
- Return ONLY the final customer-facing message. Do not include internal commentary, meta-notes, or greetings to the supervisor.

Final Customer Support Response:"""

REWRITE_PROMPT = PromptTemplate.from_template(REWRITE_TEMPLATE)
