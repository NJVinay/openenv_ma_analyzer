"""
training/sft_data.py — 20 SFT examples for format warm-up.

Each example is a (prompt, completion) pair teaching the model
the exact JSON output format for each task tier.
"""

SFT_EXAMPLES = [
    # === EASY TIER: Red Flag Scan (clause_type + reason) ===
    {
        "prompt": "You are reviewing an M&A deal document (NDA or LOI). Identify the single highest-risk clause.\n\nDocument:\nMUTUAL NON-DISCLOSURE AGREEMENT\n1. CONFIDENTIALITY\nEach Party agrees to hold in strict confidence all Confidential Information.\n2. LIABILITY CAP\nThe aggregate liability shall not exceed ten percent (10%) of the Transaction Value.\n\nRespond with ONLY valid JSON: {\"clause_type\": \"<type>\", \"reason\": \"<why>\"}",
        "completion": "{\"clause_type\": \"liability_cap\", \"reason\": \"The liability cap at 10% of transaction value is unusually low for an NDA and may leave the disclosing party underprotected against significant breaches.\"}"
    },
    {
        "prompt": "You are reviewing an M&A deal document (NDA or LOI). Identify the single highest-risk clause.\n\nDocument:\nCONFIDENTIALITY AGREEMENT\n1. SCOPE\nConfidential Information means all non-public information.\n2. NON-COMPETE\nThe Receiving Party shall not compete worldwide for 36 months.\n\nRespond with ONLY valid JSON: {\"clause_type\": \"<type>\", \"reason\": \"<why>\"}",
        "completion": "{\"clause_type\": \"non_compete\", \"reason\": \"A 36-month worldwide non-compete is overbroad in scope and duration, potentially unenforceable and highly restrictive to the receiving party.\"}"
    },
    {
        "prompt": "You are reviewing an M&A deal document (NDA or LOI). Identify the single highest-risk clause.\n\nDocument:\nNDA — PROJECT PHOENIX\n1. PURPOSE\nParties entering acquisition discussions.\n2. IP OWNERSHIP\nDerivative works automatically vest in the Disclosing Party.\n\nRespond with ONLY valid JSON: {\"clause_type\": \"<type>\", \"reason\": \"<why>\"}",
        "completion": "{\"clause_type\": \"ip_ownership\", \"reason\": \"Automatic vesting of all derivative works in the disclosing party without consideration is a one-sided IP transfer clause that could strip the receiving party of valuable innovations.\"}"
    },
    {
        "prompt": "You are reviewing an M&A deal document (NDA or LOI). Identify the single highest-risk clause.\n\nDocument:\nLETTER OF INTENT\n1. TRANSACTION\nBuyer to acquire 100% of Target for USD 450M.\n2. EXCLUSIVITY\n180-day exclusivity period barring competing transactions.\n\nRespond with ONLY valid JSON: {\"clause_type\": \"<type>\", \"reason\": \"<why>\"}",
        "completion": "{\"clause_type\": \"exclusivity\", \"reason\": \"A 180-day exclusivity period is exceptionally long and prevents the target from exploring better offers, creating significant lock-in risk.\"}"
    },
    {
        "prompt": "You are reviewing an M&A deal document (NDA or LOI). Identify the single highest-risk clause.\n\nDocument:\nLOI — STRATEGIC ACQUISITION\n1. OVERVIEW\nAcquirer proposes to acquire all assets of Target.\n2. INDEMNIFICATION\nSeller indemnification survives 5 years with no cap or basket.\n\nRespond with ONLY valid JSON: {\"clause_type\": \"<type>\", \"reason\": \"<why>\"}",
        "completion": "{\"clause_type\": \"indemnification\", \"reason\": \"Uncapped indemnification surviving for 5 years exposes the seller to unlimited liability, far exceeding market standard terms.\"}"
    },
    {
        "prompt": "You are reviewing an M&A deal document (NDA or LOI). Identify the single highest-risk clause.\n\nDocument:\nLOI — PARTNERSHIP AND ACQUISITION\n1. STRUCTURE\nTwo-step acquisition: 51% then remaining 49%.\n2. CHANGE OF CONTROL\nBuyer may terminate without liability on any change of control event.\n\nRespond with ONLY valid JSON: {\"clause_type\": \"<type>\", \"reason\": \"<why>\"}",
        "completion": "{\"clause_type\": \"change_of_control\", \"reason\": \"The broad definition of change of control (20% threshold) combined with unilateral termination rights gives the buyer excessive exit flexibility at the target's expense.\"}"
    },
    {
        "prompt": "You are reviewing an M&A deal document (NDA or LOI). Identify the single highest-risk clause.\n\nDocument:\nNDA\n1. CONFIDENTIALITY\nAll information shared is confidential for 2 years.\n2. GOVERNING LAW\nGoverned by laws of the Cayman Islands.\n\nRespond with ONLY valid JSON: {\"clause_type\": \"<type>\", \"reason\": \"<why>\"}",
        "completion": "{\"clause_type\": \"governing_law\", \"reason\": \"Cayman Islands governing law may limit enforcement options and is unusual for domestic transactions, potentially disadvantaging one party in disputes.\"}"
    },
    # === MEDIUM TIER: Risk Quantification ===
    {
        "prompt": "Assess deal risk and identify exposure clauses.\n\nDocument:\nSPA SECTION 7\n7.1 Liability capped at 20% of Total Consideration.\n7.2 Claims barred after 18 months.\n7.4 MAC clause allows buyer to terminate.\n\nRespond with JSON: {\"risk_level\": \"<level>\", \"exposure_clauses\": [...], \"reasoning\": \"<analysis>\"}",
        "completion": "{\"risk_level\": \"medium\", \"exposure_clauses\": [\"liability_cap\", \"indemnification\", \"termination\"], \"reasoning\": \"The 20% liability cap with a first-dollar basket provides moderate protection. The MAC clause gives the buyer termination rights, but the 18-month claims window limits long-tail risk exposure.\"}"
    },
    {
        "prompt": "Assess deal risk and identify exposure clauses.\n\nDocument:\nSPA SECTION 9\n9.2 Non-compete: 36 months, all jurisdictions where Company operates.\n9.3 Non-solicitation: 24 months for employees and customers.\n9.4 Governed by English law, exclusive jurisdiction.\n\nRespond with JSON: {\"risk_level\": \"<level>\", \"exposure_clauses\": [...], \"reasoning\": \"<analysis>\"}",
        "completion": "{\"risk_level\": \"medium\", \"exposure_clauses\": [\"non_compete\", \"non_solicitation\", \"governing_law\"], \"reasoning\": \"The 36-month non-compete across all operating jurisdictions is broad but geographically limited. The 24-month non-solicitation is market standard. English law jurisdiction adds complexity for non-UK parties.\"}"
    },
    {
        "prompt": "Assess deal risk and identify exposure clauses.\n\nDocument:\nSPA SECTION 11\n11.3 10% escrow for 24 months.\n11.4 Long Stop Date of 90 days with mutual termination rights.\n\nRespond with JSON: {\"risk_level\": \"<level>\", \"exposure_clauses\": [...], \"reasoning\": \"<analysis>\"}",
        "completion": "{\"risk_level\": \"low\", \"exposure_clauses\": [\"termination\", \"liability_cap\", \"escrow\"], \"reasoning\": \"The 10% escrow is standard for warranty claims protection. The 90-day long stop with mutual termination is balanced. Overall risk is low as mechanisms are well-structured.\"}"
    },
    {
        "prompt": "Assess deal risk and identify exposure clauses.\n\nDocument:\nSPA SECTION 5\n5.1 Seller liability uncapped for fraud and tax warranties.\n5.2 General warranty claims capped at 50% of consideration.\n5.3 No basket or deductible applies.\n\nRespond with JSON: {\"risk_level\": \"<level>\", \"exposure_clauses\": [...], \"reasoning\": \"<analysis>\"}",
        "completion": "{\"risk_level\": \"high\", \"exposure_clauses\": [\"liability_cap\", \"indemnification\"], \"reasoning\": \"Uncapped liability for fraud and tax combined with a 50% general cap and zero basket creates significant seller exposure. The absence of any deductible means even trivial claims can proceed.\"}"
    },
    {
        "prompt": "Assess deal risk and identify exposure clauses.\n\nDocument:\nSPA SECTION 8\n8.1 Buyer may withhold 15% pending completion accounts.\n8.2 Earnout over 3 years tied to EBITDA targets.\n8.3 Seller must maintain D&O insurance for 6 years post-close.\n\nRespond with JSON: {\"risk_level\": \"<level>\", \"exposure_clauses\": [...], \"reasoning\": \"<analysis>\"}",
        "completion": "{\"risk_level\": \"medium\", \"exposure_clauses\": [\"liability_cap\", \"indemnification\", \"termination\"], \"reasoning\": \"The 15% holdback and 3-year earnout create moderate risk for the seller. The 6-year D&O insurance requirement is above market standard but provides important protection for directors and officers.\"}"
    },
    # === HARD TIER: Clause Rewrite ===
    {
        "prompt": "Rewrite this problematic clause to protect the acquirer.\n\nClause: The Financial Statements do not materially overstate assets or understate liabilities. Since the Balance Sheet Date, there has been no Material Adverse Change.\n\nRespond with JSON: {\"issue\": \"<problem>\", \"rewritten_clause\": \"<new text>\", \"justification\": \"<why>\"}",
        "completion": "{\"issue\": \"The clause uses vague materiality qualifiers without defining thresholds, and the MAC definition lacks specificity, allowing the seller to dispute what constitutes a material adverse change.\", \"rewritten_clause\": \"The Financial Statements fairly present in all material respects the financial position of the Company as of the Balance Sheet Date. For purposes of this Agreement, a deviation exceeding five percent (5%) of any line item shall be deemed material. Since the Balance Sheet Date, there has been no event, occurrence, or development that has had or would reasonably be expected to have a Material Adverse Effect, defined as any change resulting in a decline of more than ten percent (10%) in the consolidated net assets or revenue of the Company.\", \"justification\": \"Adding quantitative materiality thresholds (5% line item, 10% net assets) eliminates ambiguity and protects the acquirer by providing clear, enforceable benchmarks for breach claims. The expanded MAC definition prevents the seller from arguing that significant negative changes were not material.\"}"
    },
    {
        "prompt": "Rewrite this problematic clause to protect the acquirer.\n\nClause: The Seller makes no representation regarding hazardous substances on formerly owned properties or compliance with Environmental Laws prior to 2020. Buyer accepts environmental condition as-is.\n\nRespond with JSON: {\"issue\": \"<problem>\", \"rewritten_clause\": \"<new text>\", \"justification\": \"<why>\"}",
        "completion": "{\"issue\": \"The as-is environmental carve-out completely shifts environmental liability to the acquirer, eliminating all seller responsibility for pre-existing contamination and historical non-compliance.\", \"rewritten_clause\": \"The Seller represents that, to the Knowledge of the Seller after reasonable inquiry, there are no known Environmental Claims or material violations of Environmental Laws relating to any property currently or formerly owned by the Company. The Seller shall indemnify the Buyer for any environmental liabilities arising from conditions existing prior to the Closing Date, subject to a cap of fifteen percent (15%) of the Total Consideration and a claims period of seven (7) years from Closing.\", \"justification\": \"Replacing the blanket as-is disclaimer with a knowledge-qualified representation and a capped indemnity protects the acquirer against hidden environmental liabilities while providing the seller with reasonable limits on exposure through the 15% cap and 7-year claims window.\"}"
    },
    {
        "prompt": "Rewrite this problematic clause to protect the acquirer.\n\nClause: All employees have executed valid invention assignment agreements. No employee is in breach of such agreement.\n\nRespond with JSON: {\"issue\": \"<problem>\", \"rewritten_clause\": \"<new text>\", \"justification\": \"<why>\"}",
        "completion": "{\"issue\": \"The blanket assertion that all employees have valid assignments and none are in breach is unrealistically absolute and lacks verification mechanisms, exposing the acquirer to undiscovered IP ownership disputes.\", \"rewritten_clause\": \"To the Knowledge of the Seller, all current and former employees, consultants, and contractors who have contributed to Company Intellectual Property have executed invention assignment agreements substantially in the form attached as Schedule 10.3. The Seller has conducted a review of such agreements within the past twelve (12) months and has disclosed all known exceptions in the Disclosure Letter. The Seller shall indemnify the Buyer against any losses arising from any failure of such agreements to be valid and enforceable.\", \"justification\": \"Adding knowledge qualification, a reference schedule, a recent review requirement, and specific indemnification protects the acquirer by ensuring transparency about IP assignment status while providing a remedy if undisclosed gaps emerge post-acquisition.\"}"
    },
    {
        "prompt": "Rewrite this problematic clause to protect the acquirer.\n\nClause: The Company has full power and authority to enter into this Agreement. The Sale Shares are free and clear of all Encumbrances.\n\nRespond with JSON: {\"issue\": \"<problem>\", \"rewritten_clause\": \"<new text>\", \"justification\": \"<why>\"}",
        "completion": "{\"issue\": \"The authority and title representations lack supporting evidence requirements and do not address potential third-party consents or change of control triggers that could invalidate the transaction.\", \"rewritten_clause\": \"The Seller has full corporate power and authority to enter into and perform its obligations under this Agreement, and all necessary corporate approvals have been obtained, evidence of which is attached as Schedule 8.1. The Seller is the sole legal and beneficial owner of the Sale Shares, free and clear of all Encumbrances, and no consent of any third party is required for the transfer of the Sale Shares to the Buyer. No change of control provision in any material contract to which the Company is a party would be triggered by the consummation of the Transaction.\", \"justification\": \"Requiring evidence of corporate approvals, adding explicit third-party consent confirmation, and addressing change of control triggers in material contracts protects the acquirer against post-closing disputes about transaction validity and contract continuity.\"}"
    },
    {
        "prompt": "You are reviewing an M&A deal document (NDA or LOI). Identify the single highest-risk clause.\n\nDocument:\nNDA\n1. CONFIDENTIALITY\nAll information is confidential.\n2. TERMINATION\nEither party may terminate with 30 days notice. Upon termination, all obligations cease immediately including return of materials.\n\nRespond with ONLY valid JSON: {\"clause_type\": \"<type>\", \"reason\": \"<why>\"}",
        "completion": "{\"clause_type\": \"termination\", \"reason\": \"Immediate cessation of all obligations upon termination, including confidentiality, creates a risk that sensitive information can be freely used or disclosed after the 30-day notice period.\"}"
    },
    {
        "prompt": "Assess deal risk and identify exposure clauses.\n\nDocument:\nSPA SECTION 6\n6.1 Representations survive indefinitely.\n6.2 No limitation on buyer's right to claim.\n6.3 Seller personally guarantees all warranties.\n\nRespond with JSON: {\"risk_level\": \"<level>\", \"exposure_clauses\": [...], \"reasoning\": \"<analysis>\"}",
        "completion": "{\"risk_level\": \"critical\", \"exposure_clauses\": [\"representations\", \"indemnification\", \"liability_cap\"], \"reasoning\": \"Indefinite survival of representations with no claims limitation and personal guarantees creates maximum seller exposure. This is far outside market norms and represents critical risk for the seller.\"}"
    },
    {
        "prompt": "Rewrite this problematic clause to protect the acquirer.\n\nClause: The Company is in full compliance with all applicable laws. All required licenses have been obtained.\n\nRespond with JSON: {\"issue\": \"<problem>\", \"rewritten_clause\": \"<new text>\", \"justification\": \"<why>\"}",
        "completion": "{\"issue\": \"The unqualified compliance representation is unrealistically broad and exposes the seller to breach claims for any minor regulatory infraction, while also lacking specificity about which laws and licenses are material.\", \"rewritten_clause\": \"The Company is in compliance in all material respects with all applicable laws, regulations, and ordinances, except as set forth in the Disclosure Letter. All material licenses, permits, and authorizations required for the lawful conduct of the Business have been obtained, are in full force and effect, and are listed in Schedule 9.2. The Seller shall promptly notify the Buyer of any non-compliance discovered prior to Closing.\", \"justification\": \"Adding materiality qualification, a disclosure letter exception, a schedule of required licenses, and a pre-closing notification obligation protects the acquirer by ensuring full visibility into the compliance landscape while making the representation practically enforceable.\"}"
    },
]
