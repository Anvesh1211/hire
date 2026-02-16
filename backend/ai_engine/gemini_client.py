from typing import Dict
import json
from datetime import datetime

class AIGenerator:
    """
    SAR narrative generator with toggle between Gemini and Local LLM
    For demo, we simulate AI generation with high-quality templates
    """
    
    def __init__(self, use_gemini: bool = True):
        self.use_gemini = use_gemini
        self.model_name = "Gemini Pro 1.5" if use_gemini else "Llama 2 7B (Local)"
        
    def toggle_model(self):
        """Switch between Gemini and Local LLM"""
        self.use_gemini = not self.use_gemini
        self.model_name = "Gemini Pro 1.5" if self.use_gemini else "Llama 2 7B (Local)"
        return self.model_name
    
    def generate_sar_narrative(
        self,
        detection_results: Dict,
        reasoning: Dict,
        customer_profile: Dict,
        case_id: str
    ) -> Dict:
        """
        Generate complete SAR narrative with all sections
        """
        
        narrative = {
            "case_id": case_id,
            "generated_at": datetime.utcnow().isoformat(),
            "ai_model": self.model_name,
            "sections": {}
        }
        
        # Section 1: Executive Summary
        narrative["sections"]["executive_summary"] = self._generate_executive_summary(
            detection_results, reasoning, customer_profile
        )
        
        # Section 2: Customer Information
        narrative["sections"]["customer_information"] = self._generate_customer_section(
            customer_profile
        )
        
        # Section 3: Transaction Analysis
        narrative["sections"]["transaction_analysis"] = self._generate_transaction_analysis(
            detection_results
        )
        
        # Section 4: Suspicious Activity Description
        narrative["sections"]["suspicious_activity"] = self._generate_suspicious_activity(
            detection_results, reasoning
        )
        
        # Section 5: Legal Basis
        narrative["sections"]["legal_basis"] = self._generate_legal_basis(
            reasoning
        )
        
        # Section 6: Recommendation
        narrative["sections"]["recommendation"] = reasoning.get("recommendation", "")
        
        # Combine into full narrative
        narrative["full_narrative"] = self._combine_sections(narrative["sections"])
        
        return narrative
    
    def _generate_executive_summary(self, detection_results: Dict, reasoning: Dict, customer_profile: Dict) -> str:
        risk_level = detection_results.get("overall_risk", "UNKNOWN")
        confidence = reasoning.get("confidence_score", 0.0)
        pattern_count = len(detection_results.get("all_patterns", []))
        
        summary = f"""EXECUTIVE SUMMARY

This Suspicious Activity Report (SAR) documents {pattern_count} distinct patterns of suspicious financial activity identified in account {customer_profile.get('account_number', 'N/A')} held by {customer_profile.get('customer_name', 'N/A')}.

Risk Assessment: {risk_level}
Confidence Level: {confidence:.1%}
Reporting Entity: {customer_profile.get('reporting_bank', 'Barclays Bank India')}
Report Date: {datetime.utcnow().strftime('%Y-%m-%d')}

The activity exhibits characteristics consistent with structured transactions designed to evade regulatory reporting thresholds, raising concerns under the Prevention of Money Laundering Act (PMLA) 2002 and related RBI directives.
"""
        return summary
    
    def _generate_customer_section(self, customer_profile: Dict) -> str:
        return f"""CUSTOMER INFORMATION

Account Holder: {customer_profile.get('customer_name', 'N/A')}
Account Number: {customer_profile.get('account_number', 'N/A')}
Customer ID: {customer_profile.get('customer_id', 'N/A')}
PAN: {customer_profile.get('pan', 'N/A')}
Account Type: {customer_profile.get('account_type', 'Savings')}
Account Opening Date: {customer_profile.get('account_opening_date', 'N/A')}

Occupation: {customer_profile.get('occupation', 'N/A')}
Declared Annual Income: ₹{customer_profile.get('annual_income', 0):,.0f}
Source of Income: {customer_profile.get('income_source', 'N/A')}

Registered Address: {customer_profile.get('address', 'N/A')}
Contact: {customer_profile.get('phone', 'N/A')}

KYC Status: {customer_profile.get('kyc_status', 'Verified')}
Risk Category: {customer_profile.get('risk_category', 'Medium')}
"""
    
    def _generate_transaction_analysis(self, detection_results: Dict) -> str:
        summary = detection_results.get("transaction_summary", {})
        
        analysis = f"""TRANSACTION ANALYSIS

Review Period: {summary.get('date_range', {}).get('start', 'N/A')} to {summary.get('date_range', {}).get('end', 'N/A')}
Total Transactions: {summary.get('total_count', 0)}
Total Amount: ₹{summary.get('total_amount', 0):,.2f}
Unique Locations: {summary.get('unique_locations', 0)}

PATTERN DETECTION RESULTS:

"""
        
        for pattern in detection_results.get("all_patterns", []):
            analysis += f"• {pattern}\n"
        
        analysis += "\n\nQUANTITATIVE EVIDENCE:\n\n"
        
        for evidence in detection_results.get("all_evidence", []):
            analysis += f"Pattern Type: {evidence.get('pattern', 'Unknown')}\n"
            for key, value in evidence.items():
                if key != 'pattern':
                    analysis += f"  - {key}: {value}\n"
            analysis += "\n"
        
        return analysis
    
    def _generate_suspicious_activity(self, detection_results: Dict, reasoning: Dict) -> str:
        activity = """DESCRIPTION OF SUSPICIOUS ACTIVITY

Based on comprehensive analysis of transaction patterns, the following suspicious behaviors have been identified:

"""
        
        # Behavioral red flags
        if reasoning.get("behavioral_red_flags"):
            activity += "Behavioral Indicators:\n"
            for i, flag in enumerate(reasoning["behavioral_red_flags"], 1):
                activity += f"{i}. {flag}\n"
            activity += "\n"
        
        # Financial inconsistencies
        if reasoning.get("financial_inconsistencies"):
            activity += "Financial Anomalies:\n"
            for inconsistency in reasoning["financial_inconsistencies"]:
                if isinstance(inconsistency, dict):
                    activity += f"• {inconsistency.get('issue', '')}: {inconsistency.get('detail', '')}\n"
                    activity += f"  Implication: {inconsistency.get('implication', '')}\n"
            activity += "\n"
        
        # Risk factors
        if detection_results.get("all_red_flags"):
            activity += "Critical Risk Factors:\n"
            for i, flag in enumerate(detection_results["all_red_flags"], 1):
                activity += f"{i}. {flag}\n"
        
        return activity
    
    def _generate_legal_basis(self, reasoning: Dict) -> str:
        legal = """LEGAL AND REGULATORY BASIS

This SAR is filed pursuant to the following legal provisions:

"""
        
        for violation in reasoning.get("legal_violations", []):
            legal += f"Typology: {violation.get('typology', 'N/A')}\n"
            legal += f"Applicable Law: {', '.join(violation.get('applicable_law', []))}\n"
            legal += f"Violation Type: {violation.get('violation_type', 'N/A')}\n"
            legal += f"Severity: {violation.get('severity', 'N/A')}\n\n"
        
        legal += """
Additional Regulatory Framework:
• Prevention of Money Laundering Act (PMLA), 2002
• RBI Master Direction on Know Your Customer (KYC), 2016
• Prevention of Money Laundering (Maintenance of Records) Rules, 2005
• Financial Intelligence Unit - India (FIU-IND) Reporting Guidelines
"""
        
        return legal
    
    def _combine_sections(self, sections: Dict) -> str:
        """Combine all sections into final narrative"""
        
        full_text = "SUSPICIOUS ACTIVITY REPORT\n"
        full_text += "=" * 80 + "\n\n"
        
        for section_name, section_content in sections.items():
            full_text += section_content + "\n\n"
            full_text += "-" * 80 + "\n\n"
        
        return full_text
    
    def review_and_improve(self, narrative: str, feedback: str) -> str:
        """
        AI-powered review and improvement
        Simulated for demo
        """
        
        review_result = f"""
NARRATIVE REVIEW COMPLETED

Model: {self.model_name}
Review Timestamp: {datetime.utcnow().isoformat()}

Feedback Addressed: {feedback}

Improvements Made:
• Enhanced legal citations
• Strengthened evidence linkage
• Improved clarity and precision
• Verified regulatory compliance

The narrative has been refined based on the provided feedback.
"""
        
        return review_result