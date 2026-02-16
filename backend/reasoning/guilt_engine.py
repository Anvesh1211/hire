from typing import Dict, List
import json

class GuiltReasoningEngine:
    """
    Explains WHY a transaction pattern is suspicious
    This is the key differentiator - evidence-based reasoning
    """
    
    def __init__(self):
        self.legal_framework = {
            "structuring": {
                "sections": ["PMLA Section 12", "RBI Master Direction on KYC 2016"],
                "violation": "Deliberate avoidance of CTR reporting threshold",
                "severity": "High"
            },
            "smurfing": {
                "sections": ["PMLA Section 3", "Prevention of Money Laundering Rules 2005"],
                "violation": "Use of multiple entities to disguise source of funds",
                "severity": "Critical"
            },
            "layering": {
                "sections": ["PMLA Section 4", "FIU-IND Guidelines 2021"],
                "violation": "Complex transactions to obscure audit trail",
                "severity": "High"
            }
        }
    
    def generate_reasoning(self, detection_results: Dict, customer_profile: Dict) -> Dict:
        """
        Generate comprehensive 'Why Guilty' explanation
        """
        
        reasoning = {
            "verdict": "SUSPICIOUS ACTIVITY CONFIRMED",
            "confidence_score": detection_results.get("risk_score", 0.0),
            "behavioral_red_flags": [],
            "financial_inconsistencies": [],
            "legal_violations": [],
            "risk_factors": [],
            "recommendation": "",
            "supporting_evidence": []
        }
        
        # Analyze behavioral patterns
        if "structuring" in detection_results["detections"]:
            struct_data = detection_results["detections"]["structuring"]
            if struct_data["detected"]:
                reasoning["behavioral_red_flags"].extend([
                    "Systematic avoidance of regulatory reporting thresholds",
                    "Premeditated transaction amount selection",
                    "Pattern consistency indicates deliberate planning"
                ])
                
                # Add specific evidence
                for evidence in struct_data.get("evidence", []):
                    if evidence["pattern"] == "Near-threshold clustering":
                        reasoning["supporting_evidence"].append({
                            "type": "Threshold Avoidance",
                            "detail": f"{evidence['count']} transactions averaging {evidence['threshold_percentage']:.1f}% of CTR limit",
                            "implication": "Calculated to avoid mandatory reporting"
                        })
                    
                    if evidence["pattern"] == "Low variance":
                        reasoning["supporting_evidence"].append({
                            "type": "Statistical Anomaly",
                            "detail": f"Coefficient of variation: {evidence['coefficient_variation']:.4f} (typical: >0.25)",
                            "implication": "Unnatural consistency suggests scripted behavior"
                        })
        
        # Analyze financial inconsistencies
        customer_income = customer_profile.get("annual_income", 0)
        total_transactions = detection_results["transaction_summary"]["total_amount"]
        
        if customer_income > 0 and total_transactions > customer_income * 2:
            reasoning["financial_inconsistencies"].append({
                "issue": "Income-Transaction Mismatch",
                "declared_income": f"₹{customer_income:,.0f}",
                "transaction_volume": f"₹{total_transactions:,.0f}",
                "ratio": f"{(total_transactions/customer_income):.1f}x declared income",
                "implication": "Source of funds unclear and disproportionate"
            })
        
        # Unknown sources
        if any("unknown source" in p.lower() for p in detection_results["all_patterns"]):
            reasoning["financial_inconsistencies"].append({
                "issue": "Undocumented Fund Sources",
                "detail": "Multiple cash deposits from unidentified sources",
                "implication": "Violates KYC source-of-funds verification requirements"
            })
        
        # Legal mapping
        detected_types = [k for k, v in detection_results["detections"].items() if v["detected"]]
        for typology in detected_types:
            if typology in self.legal_framework:
                legal_info = self.legal_framework[typology]
                reasoning["legal_violations"].append({
                    "typology": typology.upper(),
                    "applicable_law": legal_info["sections"],
                    "violation_type": legal_info["violation"],
                    "severity": legal_info["severity"]
                })
        
        # Risk factors
        reasoning["risk_factors"] = detection_results.get("all_red_flags", [])
        
        # Generate recommendation
        risk_score = reasoning["confidence_score"]
        if risk_score >= 0.75:
            reasoning["recommendation"] = "IMMEDIATE SAR FILING REQUIRED - Critical risk indicators present"
        elif risk_score >= 0.50:
            reasoning["recommendation"] = "SAR filing recommended - Multiple suspicious patterns detected"
        else:
            reasoning["recommendation"] = "Enhanced monitoring - Further investigation advised"
        
        return reasoning
    
    def format_narrative_explanation(self, reasoning: Dict) -> str:
        """
        Generate human-readable explanation for SAR narrative
        """
        
        narrative_parts = []
        
        # Opening statement
        narrative_parts.append(
            f"Based on comprehensive transaction analysis, this account exhibits {len(reasoning['behavioral_red_flags'])} "
            f"behavioral red flags and {len(reasoning['financial_inconsistencies'])} financial inconsistencies, "
            f"resulting in a risk confidence score of {reasoning['confidence_score']:.2%}."
        )
        
        # Behavioral patterns
        if reasoning["behavioral_red_flags"]:
            narrative_parts.append("\n**Behavioral Analysis:**")
            for i, flag in enumerate(reasoning["behavioral_red_flags"], 1):
                narrative_parts.append(f"{i}. {flag}")
        
        # Financial issues
        if reasoning["financial_inconsistencies"]:
            narrative_parts.append("\n**Financial Inconsistencies:**")
            for inconsistency in reasoning["financial_inconsistencies"]:
                if isinstance(inconsistency, dict):
                    narrative_parts.append(f"- {inconsistency['issue']}: {inconsistency.get('detail', inconsistency.get('implication', ''))}")
                else:
                    narrative_parts.append(f"- {inconsistency}")
        
        # Legal basis
        if reasoning["legal_violations"]:
            narrative_parts.append("\n**Legal Framework Violations:**")
            for violation in reasoning["legal_violations"]:
                narrative_parts.append(
                    f"- {violation['typology']}: Violates {', '.join(violation['applicable_law'])} "
                    f"({violation['violation_type']})"
                )
        
        # Supporting evidence
        if reasoning["supporting_evidence"]:
            narrative_parts.append("\n**Quantitative Evidence:**")
            for evidence in reasoning["supporting_evidence"]:
                narrative_parts.append(
                    f"- {evidence['type']}: {evidence['detail']} → {evidence['implication']}"
                )
        
        # Conclusion
        narrative_parts.append(f"\n**Recommendation:** {reasoning['recommendation']}")
        
        return "\n".join(narrative_parts)