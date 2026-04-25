"""
server/data/deals.py — M&A Deal Document Corpus.

Contains 12 DealDocument objects (3 per deal_type: NDA, LOI, SPA, reps_and_warranties)
with realistic legal prose and ground-truth labels for grading.
"""

import random
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class DealDocument:
    """A single M&A deal document with ground-truth labels."""
    id: str
    deal_type: Literal["NDA", "LOI", "SPA", "reps_and_warranties"]
    risk_tier: Literal["easy", "medium", "hard"]
    excerpt: str
    expected_red_flag: str
    expected_risk_level: str
    expected_exposure_clauses: list[str] = field(default_factory=list)
    expected_issue_keywords: list[str] = field(default_factory=list)
    target_clause: str = ""


# ──────────────────────────────────────────────────────────────
# NDA Documents (Easy tier — red-flag-scan)
# ──────────────────────────────────────────────────────────────

NDA_DOCS = [
    DealDocument(
        id="nda_001",
        deal_type="NDA",
        risk_tier="easy",
        excerpt=(
            "MUTUAL NON-DISCLOSURE AGREEMENT\n\n"
            "1. CONFIDENTIALITY OBLIGATIONS\n"
            "Each Party agrees to hold in strict confidence all Confidential Information "
            "received from the Disclosing Party and shall not disclose such information to "
            "any third party without the prior written consent of the Disclosing Party. "
            "The Receiving Party shall use the Confidential Information solely for the "
            "purpose of evaluating the proposed Transaction.\n\n"
            "2. LIABILITY CAP\n"
            "The aggregate liability of either Party under or in connection with this "
            "Agreement, whether arising in contract, tort (including negligence), "
            "misrepresentation, breach of statutory duty or otherwise, shall not in any "
            "circumstances exceed an amount equal to ten percent (10%) of the proposed "
            "Transaction Value. Neither Party shall be liable for any indirect, "
            "consequential, special or punitive damages.\n\n"
            "3. TERM\n"
            "This Agreement shall remain in effect for a period of two (2) years from the "
            "Effective Date, after which all obligations shall terminate except for those "
            "that by their nature survive termination."
        ),
        expected_red_flag="liability_cap",
        expected_risk_level="medium",
        expected_exposure_clauses=["liability_cap", "consequential_damages"],
        expected_issue_keywords=["cap", "liability", "ten percent", "transaction value"],
        target_clause=(
            "The aggregate liability of either Party under or in connection with this "
            "Agreement, whether arising in contract, tort (including negligence), "
            "misrepresentation, breach of statutory duty or otherwise, shall not in any "
            "circumstances exceed an amount equal to ten percent (10%) of the proposed "
            "Transaction Value."
        ),
    ),
    DealDocument(
        id="nda_002",
        deal_type="NDA",
        risk_tier="easy",
        excerpt=(
            "CONFIDENTIALITY AND NON-DISCLOSURE AGREEMENT\n\n"
            "1. SCOPE OF CONFIDENTIAL INFORMATION\n"
            "For purposes of this Agreement, 'Confidential Information' means any and all "
            "non-public information disclosed by either Party, including but not limited to "
            "financial data, customer lists, trade secrets, and proprietary technology.\n\n"
            "2. NON-COMPETE RESTRICTION\n"
            "During the term of this Agreement and for a period of thirty-six (36) months "
            "thereafter, the Receiving Party shall not, directly or indirectly, engage in, "
            "own, manage, operate, consult for, or be employed by any entity that competes "
            "with the Disclosing Party's business in any market where the Disclosing Party "
            "operates or plans to operate. This restriction applies worldwide and covers all "
            "lines of business, including those not related to the Transaction.\n\n"
            "3. REMEDIES\n"
            "The Parties acknowledge that any breach of this Agreement may cause irreparable "
            "harm and that monetary damages may be inadequate."
        ),
        expected_red_flag="non_compete",
        expected_risk_level="high",
        expected_exposure_clauses=["non_compete", "non_solicitation"],
        expected_issue_keywords=["non-compete", "worldwide", "thirty-six months", "competes"],
        target_clause=(
            "During the term of this Agreement and for a period of thirty-six (36) months "
            "thereafter, the Receiving Party shall not, directly or indirectly, engage in, "
            "own, manage, operate, consult for, or be employed by any entity that competes "
            "with the Disclosing Party's business in any market where the Disclosing Party "
            "operates or plans to operate."
        ),
    ),
    DealDocument(
        id="nda_003",
        deal_type="NDA",
        risk_tier="easy",
        excerpt=(
            "NON-DISCLOSURE AGREEMENT — PROJECT PHOENIX\n\n"
            "1. PURPOSE\n"
            "The Parties are entering into discussions regarding a potential acquisition "
            "(the 'Transaction') and wish to protect certain proprietary information.\n\n"
            "2. INTELLECTUAL PROPERTY\n"
            "All intellectual property, including patents, copyrights, trade secrets, and "
            "know-how disclosed during the evaluation period shall remain the exclusive "
            "property of the Disclosing Party. Any derivative works, improvements, or "
            "modifications created by the Receiving Party using the Disclosing Party's "
            "Confidential Information shall automatically vest in and become the sole "
            "property of the Disclosing Party without further consideration. The Receiving "
            "Party hereby irrevocably assigns all rights, title, and interest in such "
            "derivative works to the Disclosing Party.\n\n"
            "3. GOVERNING LAW\n"
            "This Agreement shall be governed by and construed in accordance with the laws "
            "of the State of Delaware."
        ),
        expected_red_flag="ip_ownership",
        expected_risk_level="high",
        expected_exposure_clauses=["ip_ownership", "assignment_clause"],
        expected_issue_keywords=["intellectual property", "derivative works", "assigns", "vest"],
        target_clause=(
            "Any derivative works, improvements, or modifications created by the Receiving "
            "Party using the Disclosing Party's Confidential Information shall automatically "
            "vest in and become the sole property of the Disclosing Party without further "
            "consideration."
        ),
    ),
]


# ──────────────────────────────────────────────────────────────
# LOI Documents (Easy tier — red-flag-scan)
# ──────────────────────────────────────────────────────────────

LOI_DOCS = [
    DealDocument(
        id="loi_001",
        deal_type="LOI",
        risk_tier="easy",
        excerpt=(
            "LETTER OF INTENT — ACQUISITION OF TARGET CO.\n\n"
            "1. PROPOSED TRANSACTION\n"
            "Buyer intends to acquire one hundred percent (100%) of the issued and "
            "outstanding shares of Target Co. for a total consideration of USD 450,000,000 "
            "(the 'Purchase Price'), subject to customary adjustments.\n\n"
            "2. EXCLUSIVITY\n"
            "Upon execution of this Letter, Target Co. and its shareholders shall not, "
            "for a period of one hundred and eighty (180) days (the 'Exclusivity Period'), "
            "directly or indirectly: (a) solicit, initiate, or encourage any inquiry or "
            "proposal relating to any Competing Transaction; (b) participate in any "
            "discussions or negotiations regarding a Competing Transaction; or (c) provide "
            "any non-public information to any third party in connection with a Competing "
            "Transaction. Target Co. shall immediately terminate any existing discussions "
            "with third parties regarding alternative transactions.\n\n"
            "3. DUE DILIGENCE\n"
            "Target Co. shall provide Buyer with full access to its books, records, and "
            "management personnel during the Exclusivity Period."
        ),
        expected_red_flag="exclusivity",
        expected_risk_level="high",
        expected_exposure_clauses=["exclusivity", "non_solicitation"],
        expected_issue_keywords=["exclusivity", "180 days", "competing transaction", "terminate"],
        target_clause=(
            "Upon execution of this Letter, Target Co. and its shareholders shall not, "
            "for a period of one hundred and eighty (180) days (the 'Exclusivity Period'), "
            "directly or indirectly: (a) solicit, initiate, or encourage any inquiry or "
            "proposal relating to any Competing Transaction."
        ),
    ),
    DealDocument(
        id="loi_002",
        deal_type="LOI",
        risk_tier="easy",
        excerpt=(
            "NON-BINDING LETTER OF INTENT\n\n"
            "1. OVERVIEW\n"
            "This Letter of Intent sets forth the principal terms under which Acquirer "
            "proposes to acquire substantially all of the assets of Target.\n\n"
            "2. INDEMNIFICATION\n"
            "The Seller shall indemnify, defend, and hold harmless the Buyer and its "
            "affiliates, directors, officers, employees, and agents from and against any "
            "and all losses, damages, liabilities, costs, and expenses (including "
            "reasonable attorneys' fees) arising from or related to: (a) any breach of "
            "any representation or warranty made by the Seller; (b) any breach of any "
            "covenant or agreement of the Seller; and (c) any third-party claims relating "
            "to the operation of the business prior to the Closing Date. The Seller's "
            "indemnification obligations shall survive the Closing for a period of five "
            "(5) years and shall not be subject to any cap, basket, or other limitation.\n\n"
            "3. CONDITIONS PRECEDENT\n"
            "The Closing shall be subject to satisfactory completion of due diligence, "
            "receipt of all required regulatory approvals, and execution of definitive "
            "agreements."
        ),
        expected_red_flag="indemnification",
        expected_risk_level="high",
        expected_exposure_clauses=["indemnification", "liability_cap"],
        expected_issue_keywords=["indemnify", "no cap", "five years", "unlimited"],
        target_clause=(
            "The Seller's indemnification obligations shall survive the Closing for a "
            "period of five (5) years and shall not be subject to any cap, basket, or "
            "other limitation."
        ),
    ),
    DealDocument(
        id="loi_003",
        deal_type="LOI",
        risk_tier="easy",
        excerpt=(
            "LETTER OF INTENT — STRATEGIC PARTNERSHIP AND ACQUISITION\n\n"
            "1. TRANSACTION STRUCTURE\n"
            "Buyer proposes a two-step acquisition: (i) an initial purchase of 51% of "
            "Target's equity for USD 200,000,000, followed by (ii) a mandatory put/call "
            "option for the remaining 49% within 24 months.\n\n"
            "2. CHANGE OF CONTROL\n"
            "In the event of a Change of Control of Target prior to Closing, Buyer shall "
            "have the right to terminate this Letter of Intent without liability. For "
            "purposes of this Letter, 'Change of Control' means: (a) the acquisition by "
            "any person or group of more than twenty percent (20%) of the voting securities "
            "of Target; (b) a merger or consolidation of Target with any other entity; or "
            "(c) a sale of all or substantially all of Target's assets. Target shall provide "
            "Buyer with not less than five (5) business days' prior written notice of any "
            "proposed Change of Control event.\n\n"
            "3. BREAK FEE\n"
            "If Target terminates this Letter or fails to consummate the Transaction for "
            "any reason, Target shall pay Buyer a break fee equal to three percent (3%) of "
            "the Purchase Price."
        ),
        expected_red_flag="change_of_control",
        expected_risk_level="high",
        expected_exposure_clauses=["change_of_control", "termination"],
        expected_issue_keywords=["change of control", "twenty percent", "terminate", "break fee"],
        target_clause=(
            "In the event of a Change of Control of Target prior to Closing, Buyer shall "
            "have the right to terminate this Letter of Intent without liability."
        ),
    ),
]


# ──────────────────────────────────────────────────────────────
# SPA Documents (Medium tier — risk-quantification)
# ──────────────────────────────────────────────────────────────

SPA_DOCS = [
    DealDocument(
        id="spa_001",
        deal_type="SPA",
        risk_tier="medium",
        excerpt=(
            "SHARE PURCHASE AGREEMENT — SECTION 7: RISK ALLOCATION\n\n"
            "7.1 LIMITATION OF LIABILITY\n"
            "The aggregate liability of the Seller under this Agreement shall not exceed "
            "twenty percent (20%) of the Total Consideration. No claim may be brought "
            "unless the aggregate amount of all claims exceeds USD 500,000 (the 'Basket'), "
            "in which event the Seller shall be liable for the full amount of all claims "
            "from the first dollar.\n\n"
            "7.2 TIME LIMITATION\n"
            "No claim under this Agreement may be brought after the date falling eighteen "
            "(18) months after the Completion Date, except for claims relating to Tax "
            "Warranties, which may be brought within seven (7) years.\n\n"
            "7.3 INSURANCE\n"
            "The Seller shall procure and maintain warranty and indemnity insurance with "
            "a coverage limit of not less than thirty percent (30%) of the Total "
            "Consideration for a period of thirty-six (36) months from the Completion Date.\n\n"
            "7.4 MATERIAL ADVERSE CHANGE\n"
            "If, between the date of this Agreement and Completion, a Material Adverse "
            "Change occurs, the Buyer may elect to: (a) complete the Transaction at a "
            "reduced Purchase Price; (b) require the Seller to remedy the Material Adverse "
            "Change; or (c) terminate this Agreement without liability to the Seller."
        ),
        expected_red_flag="liability_cap",
        expected_risk_level="medium",
        expected_exposure_clauses=["liability_cap", "indemnification", "termination"],
        expected_issue_keywords=["twenty percent", "basket", "material adverse change", "cap"],
        target_clause=(
            "The aggregate liability of the Seller under this Agreement shall not exceed "
            "twenty percent (20%) of the Total Consideration."
        ),
    ),
    DealDocument(
        id="spa_002",
        deal_type="SPA",
        risk_tier="medium",
        excerpt=(
            "SHARE PURCHASE AGREEMENT — SECTION 9: COVENANTS\n\n"
            "9.1 CONDUCT OF BUSINESS PENDING COMPLETION\n"
            "Between the date of this Agreement and Completion, the Seller shall procure "
            "that the Company: (a) carries on its business in the ordinary course; "
            "(b) does not enter into any contract with a value exceeding USD 100,000 "
            "without the Buyer's prior written consent; (c) does not declare or pay any "
            "dividend or make any distribution to shareholders.\n\n"
            "9.2 NON-COMPETE\n"
            "For a period of thirty-six (36) months following Completion, the Seller and "
            "each Warrantor shall not, and shall procure that their Connected Persons do "
            "not, directly or indirectly carry on, be engaged in, or be interested in any "
            "business that is competitive with the Business in any jurisdiction where the "
            "Company operates.\n\n"
            "9.3 NON-SOLICITATION\n"
            "For a period of twenty-four (24) months following Completion, the Seller "
            "shall not solicit or entice away any employee, customer, or supplier of the "
            "Company.\n\n"
            "9.4 GOVERNING LAW\n"
            "This Agreement shall be governed by English law and the parties submit to the "
            "exclusive jurisdiction of the English courts."
        ),
        expected_red_flag="non_compete",
        expected_risk_level="medium",
        expected_exposure_clauses=["non_compete", "non_solicitation", "governing_law"],
        expected_issue_keywords=["non-compete", "thirty-six months", "competitive", "jurisdiction"],
        target_clause=(
            "For a period of thirty-six (36) months following Completion, the Seller and "
            "each Warrantor shall not, and shall procure that their Connected Persons do "
            "not, directly or indirectly carry on, be engaged in, or be interested in any "
            "business that is competitive with the Business."
        ),
    ),
    DealDocument(
        id="spa_003",
        deal_type="SPA",
        risk_tier="medium",
        excerpt=(
            "SHARE PURCHASE AGREEMENT — SECTION 11: COMPLETION MECHANICS\n\n"
            "11.1 COMPLETION ACCOUNTS\n"
            "Within sixty (60) Business Days after the Completion Date, the Buyer shall "
            "prepare and deliver to the Seller draft Completion Accounts setting out the "
            "Net Asset Value as at the Effective Time.\n\n"
            "11.2 PURCHASE PRICE ADJUSTMENT\n"
            "The Purchase Price shall be adjusted upward or downward on a dollar-for-dollar "
            "basis to reflect the difference between the Estimated Net Asset Value and the "
            "Final Net Asset Value as determined from the Completion Accounts.\n\n"
            "11.3 ESCROW\n"
            "At Completion, the Buyer shall deposit ten percent (10%) of the Total "
            "Consideration into an escrow account to be held for a period of twenty-four "
            "(24) months to satisfy any warranty claims. The Seller shall have no access "
            "to the escrowed funds during this period.\n\n"
            "11.4 TERMINATION RIGHTS\n"
            "If Completion does not occur within ninety (90) days of the date of this "
            "Agreement (the 'Long Stop Date'), either party may terminate this Agreement "
            "by written notice, provided that the terminating party is not in breach of "
            "its obligations."
        ),
        expected_red_flag="termination",
        expected_risk_level="low",
        expected_exposure_clauses=["termination", "liability_cap", "escrow"],
        expected_issue_keywords=["escrow", "ten percent", "long stop date", "termination"],
        target_clause=(
            "At Completion, the Buyer shall deposit ten percent (10%) of the Total "
            "Consideration into an escrow account to be held for a period of twenty-four "
            "(24) months to satisfy any warranty claims."
        ),
    ),
]


# ──────────────────────────────────────────────────────────────
# Reps & Warranties Documents (Hard tier — clause-rewrite)
# ──────────────────────────────────────────────────────────────

REPS_DOCS = [
    DealDocument(
        id="reps_001",
        deal_type="reps_and_warranties",
        risk_tier="hard",
        excerpt=(
            "REPRESENTATIONS AND WARRANTIES OF THE SELLER\n\n"
            "8.1 The Seller represents and warrants to the Buyer that:\n\n"
            "(a) CORPORATE AUTHORITY: The Seller has full power and authority to enter into "
            "and perform its obligations under this Agreement.\n\n"
            "(b) TITLE TO SHARES: The Seller is the sole legal and beneficial owner of the "
            "Sale Shares, free and clear of all Encumbrances.\n\n"
            "(c) FINANCIAL STATEMENTS: The Financial Statements have been prepared in "
            "accordance with GAAP applied on a consistent basis and give a true and fair "
            "view of the state of affairs of the Company as at the Balance Sheet Date. "
            "The Financial Statements do not materially overstate the assets or materially "
            "understate the liabilities of the Company. Since the Balance Sheet Date, there "
            "has been no Material Adverse Change in the financial condition, results of "
            "operations, or business prospects of the Company. The Company has no "
            "liabilities, whether absolute, accrued, contingent, or otherwise, that are "
            "not reflected or reserved against in the Financial Statements, except for "
            "liabilities incurred in the ordinary course of business since the Balance "
            "Sheet Date that, individually or in the aggregate, are not material."
        ),
        expected_red_flag="representations",
        expected_risk_level="high",
        expected_exposure_clauses=["representations", "material_adverse_change"],
        expected_issue_keywords=["material adverse change", "contingent liabilities", "overstate", "gaap"],
        target_clause=(
            "The Financial Statements do not materially overstate the assets or materially "
            "understate the liabilities of the Company. Since the Balance Sheet Date, there "
            "has been no Material Adverse Change in the financial condition, results of "
            "operations, or business prospects of the Company. The Company has no "
            "liabilities, whether absolute, accrued, contingent, or otherwise, that are "
            "not reflected or reserved against in the Financial Statements, except for "
            "liabilities incurred in the ordinary course of business since the Balance "
            "Sheet Date that, individually or in the aggregate, are not material."
        ),
    ),
    DealDocument(
        id="reps_002",
        deal_type="reps_and_warranties",
        risk_tier="hard",
        excerpt=(
            "REPRESENTATIONS AND WARRANTIES — ENVIRONMENTAL AND REGULATORY\n\n"
            "9.1 ENVIRONMENTAL COMPLIANCE\n"
            "The Company is and has at all times been in full compliance with all applicable "
            "Environmental Laws and has obtained and maintained all necessary Environmental "
            "Permits. There are no pending or, to the Knowledge of the Seller, threatened "
            "Environmental Claims against the Company.\n\n"
            "9.2 REGULATORY APPROVALS\n"
            "All licences, permits, authorisations, and approvals required for the lawful "
            "conduct of the Business as presently conducted have been obtained, are in full "
            "force and effect, and are not subject to any conditions or restrictions that "
            "have not been disclosed to the Buyer.\n\n"
            "9.3 LIMITATION ON ENVIRONMENTAL WARRANTIES\n"
            "Notwithstanding Section 9.1, the Seller makes no representation or warranty "
            "regarding: (a) the presence or absence of hazardous substances on any property "
            "formerly owned or operated by the Company; (b) compliance with Environmental "
            "Laws prior to 1 January 2020; or (c) the adequacy of any environmental "
            "insurance coverage. The Buyer acknowledges that it has conducted its own "
            "environmental due diligence and accepts the environmental condition of the "
            "Company's properties on an 'as-is, where-is' basis."
        ),
        expected_red_flag="representations",
        expected_risk_level="critical",
        expected_exposure_clauses=["representations", "indemnification", "liability_cap"],
        expected_issue_keywords=["environmental", "as-is", "limitation", "no representation", "hazardous"],
        target_clause=(
            "Notwithstanding Section 9.1, the Seller makes no representation or warranty "
            "regarding: (a) the presence or absence of hazardous substances on any property "
            "formerly owned or operated by the Company; (b) compliance with Environmental "
            "Laws prior to 1 January 2020; or (c) the adequacy of any environmental "
            "insurance coverage. The Buyer acknowledges that it has conducted its own "
            "environmental due diligence and accepts the environmental condition of the "
            "Company's properties on an 'as-is, where-is' basis."
        ),
    ),
    DealDocument(
        id="reps_003",
        deal_type="reps_and_warranties",
        risk_tier="hard",
        excerpt=(
            "REPRESENTATIONS AND WARRANTIES — INTELLECTUAL PROPERTY\n\n"
            "10.1 OWNERSHIP OF IP\n"
            "The Company is the sole and exclusive owner of, or has valid and enforceable "
            "licences to use, all Intellectual Property necessary for the conduct of the "
            "Business as presently conducted and as contemplated to be conducted.\n\n"
            "10.2 NO INFRINGEMENT\n"
            "To the Knowledge of the Seller, the conduct of the Business does not infringe "
            "upon or misappropriate the Intellectual Property rights of any third party, "
            "and no third party is infringing upon the Company's Intellectual Property.\n\n"
            "10.3 EMPLOYEE IP ASSIGNMENT\n"
            "All current and former employees, consultants, and contractors of the Company "
            "who have contributed to the development of any Company Intellectual Property "
            "have executed valid and enforceable invention assignment agreements assigning "
            "all rights in their work product to the Company. No current employee or "
            "contractor is in breach of any such agreement, and no former employee has "
            "asserted any claim to ownership of any Company Intellectual Property.\n\n"
            "10.4 OPEN SOURCE\n"
            "The Company has not incorporated any open-source software into its proprietary "
            "products in a manner that would require the Company to disclose or license any "
            "of its proprietary source code under copyleft or similar obligations."
        ),
        expected_red_flag="ip_ownership",
        expected_risk_level="medium",
        expected_exposure_clauses=["ip_ownership", "representations", "assignment_clause"],
        expected_issue_keywords=["intellectual property", "assignment", "open source", "infringement", "knowledge"],
        target_clause=(
            "All current and former employees, consultants, and contractors of the Company "
            "who have contributed to the development of any Company Intellectual Property "
            "have executed valid and enforceable invention assignment agreements assigning "
            "all rights in their work product to the Company. No current employee or "
            "contractor is in breach of any such agreement, and no former employee has "
            "asserted any claim to ownership of any Company Intellectual Property."
        ),
    ),
]


# ──────────────────────────────────────────────────────────────
# Aggregate corpus + sampling
# ──────────────────────────────────────────────────────────────

ALL_DEALS: list[DealDocument] = NDA_DOCS + LOI_DOCS + SPA_DOCS + REPS_DOCS

_TIER_DEALS = {
    "easy": [d for d in ALL_DEALS if d.risk_tier == "easy"],
    "medium": [d for d in ALL_DEALS if d.risk_tier == "medium"],
    "hard": [d for d in ALL_DEALS if d.risk_tier == "hard"],
}


def sample_deal(seed: int | None = None, tier: str = "easy") -> DealDocument:
    """Return a deal document deterministically based on seed and tier.

    Args:
        seed: Random seed for reproducibility. If None, random choice.
        tier: One of 'easy', 'medium', 'hard'.

    Returns:
        A DealDocument matching the requested tier.
    """
    pool = _TIER_DEALS.get(tier, ALL_DEALS)
    if not pool:
        pool = ALL_DEALS

    if seed is not None:
        rng = random.Random(seed)
        return rng.choice(pool)

    return random.choice(pool)


def get_deal_by_id(deal_id: str) -> DealDocument:
    """Retrieve a specific deal by ID."""
    for deal in ALL_DEALS:
        if deal.id == deal_id:
            return deal
    raise ValueError(f"Unknown deal ID: {deal_id}")
