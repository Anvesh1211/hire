import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

class StructuringDetector:
    """Detects structuring (smurfing) patterns in transactions"""
    
    def __init__(self, ctr_threshold: float = 10000):
        self.ctr_threshold = ctr_threshold
        
    def analyze(self, transactions: pd.DataFrame) -> Dict:
        """
        Analyze transactions for structuring patterns
        Returns detailed detection results with evidence
        """
        results = {
            "detected": False,
            "confidence": 0.0,
            "patterns": [],
            "evidence": [],
            "risk_score": 0.0,
            "red_flags": []
        }
        
        if len(transactions) < 3:
            return results
            
        # Convert amount to numeric
        transactions['amount'] = pd.to_numeric(transactions['amount'], errors='coerce')
        transactions['date'] = pd.to_datetime(transactions['date'])
        
        # Pattern 1: Multiple transactions just below threshold
        below_threshold = transactions[
            (transactions['amount'] > self.ctr_threshold * 0.85) & 
            (transactions['amount'] < self.ctr_threshold)
        ]
        
        if len(below_threshold) >= 3:
            results["detected"] = True
            results["patterns"].append("Multiple transactions 85-99% of CTR threshold")
            results["evidence"].append({
                "pattern": "Near-threshold clustering",
                "count": len(below_threshold),
                "transactions": below_threshold['transaction_id'].tolist(),
                "amounts": below_threshold['amount'].tolist(),
                "threshold_percentage": (below_threshold['amount'] / self.ctr_threshold * 100).mean()
            })
            results["red_flags"].append(f"{len(below_threshold)} transactions within 15% below CTR limit")
        
        # Pattern 2: Low variance in amounts (indicates deliberate structuring)
        if len(transactions) >= 5:
            cv = transactions['amount'].std() / transactions['amount'].mean()
            if cv < 0.10:  # Coefficient of variation < 10%
                results["detected"] = True
                results["patterns"].append("Unusually consistent transaction amounts")
                results["evidence"].append({
                    "pattern": "Low variance",
                    "coefficient_variation": round(cv, 4),
                    "mean_amount": round(transactions['amount'].mean(), 2),
                    "std_deviation": round(transactions['amount'].std(), 2)
                })
                results["red_flags"].append(f"Abnormally low variance (CV={cv:.4f}) suggests premeditated structuring")
        
        # Pattern 3: Temporal clustering (multiple transactions in short time)
        transactions_sorted = transactions.sort_values('date')
        date_diffs = transactions_sorted['date'].diff()
        rapid_sequences = (date_diffs <= timedelta(days=2)).sum()
        
        if rapid_sequences >= 3:
            results["detected"] = True
            results["patterns"].append("Rapid sequential transactions")
            results["evidence"].append({
                "pattern": "Temporal clustering",
                "rapid_sequence_count": int(rapid_sequences),
                "average_gap_days": float(date_diffs.mean().days) if not date_diffs.isna().all() else 0
            })
            results["red_flags"].append(f"{rapid_sequences} transactions within 48-hour windows")
        
        # Pattern 4: Unknown sources (cash deposits)
        unknown_sources = transactions[transactions['source'] == 'Unknown']
        if len(unknown_sources) >= 5:
            results["detected"] = True
            results["patterns"].append("Multiple unknown source transactions")
            results["evidence"].append({
                "pattern": "Source obscuration",
                "unknown_count": len(unknown_sources),
                "total_unknown_amount": float(unknown_sources['amount'].sum())
            })
            results["red_flags"].append(f"{len(unknown_sources)} transactions from unknown/undocumented sources")
        
        # Calculate overall risk score
        risk_factors = len(results["patterns"])
        results["risk_score"] = min(risk_factors * 0.25, 1.0)
        results["confidence"] = min(0.6 + (risk_factors * 0.1), 0.95)
        
        return results


class SmurfingDetector:
    """Detects smurfing (multiple entities, coordinated deposits)"""
    
    def analyze(self, transactions: pd.DataFrame) -> Dict:
        results = {
            "detected": False,
            "confidence": 0.0,
            "patterns": [],
            "evidence": []
        }
        
        # Check for coordinated timing patterns
        if len(transactions) >= 5:
            transactions['date'] = pd.to_datetime(transactions['date'])
            same_day_txns = transactions.groupby(transactions['date'].dt.date).size()
            
            if (same_day_txns >= 3).sum() >= 2:
                results["detected"] = True
                results["patterns"].append("Multiple coordinated same-day deposits")
                results["evidence"].append({
                    "pattern": "Smurfing coordination",
                    "days_with_multiple": int((same_day_txns >= 3).sum()),
                    "max_same_day": int(same_day_txns.max())
                })
                results["confidence"] = 0.72
        
        return results


class LayeringDetector:
    """Detects layering (complex movement to hide origin)"""
    
    def analyze(self, transactions: pd.DataFrame) -> Dict:
        results = {
            "detected": False,
            "confidence": 0.0,
            "patterns": [],
            "evidence": []
        }
        
        # Look for international transfers after deposits
        intl_txns = transactions[transactions['transaction_type'].str.contains('International|Wire', na=False)]
        
        if len(intl_txns) >= 2:
            results["detected"] = True
            results["patterns"].append("International wire transfers following cash deposits")
            results["evidence"].append({
                "pattern": "Layering via international transfers",
                "international_count": len(intl_txns),
                "destinations": intl_txns['location'].unique().tolist(),
                "total_amount": float(intl_txns['amount'].sum())
            })
            results["confidence"] = 0.68
        
        return results


class ComprehensiveDetectionEngine:
    """Orchestrates all detection modules"""
    
    def __init__(self, ctr_threshold: float = 10000):
        self.structuring = StructuringDetector(ctr_threshold)
        self.smurfing = SmurfingDetector()
        self.layering = LayeringDetector()
        
    def analyze_all(self, transactions: pd.DataFrame) -> Dict:
        """Run all detection algorithms and combine results"""
        
        results = {
            "overall_risk": "LOW",
            "risk_score": 0.0,
            "detections": {
                "structuring": self.structuring.analyze(transactions),
                "smurfing": self.smurfing.analyze(transactions),
                "layering": self.layering.analyze(transactions)
            },
            "all_patterns": [],
            "all_evidence": [],
            "all_red_flags": [],
            "transaction_summary": {
                "total_count": len(transactions),
                "total_amount": float(transactions['amount'].sum()),
                "date_range": {
                    "start": str(transactions['date'].min()),
                    "end": str(transactions['date'].max())
                },
                "unique_locations": transactions['location'].nunique()
            }
        }
        
        # Aggregate all findings
        for detection_type, detection_result in results["detections"].items():
            if detection_result["detected"]:
                results["all_patterns"].extend(detection_result["patterns"])
                results["all_evidence"].extend(detection_result["evidence"])
                if "red_flags" in detection_result:
                    results["all_red_flags"].extend(detection_result["red_flags"])
        
        # Calculate overall risk
        max_confidence = max([d["confidence"] for d in results["detections"].values()])
        detected_count = sum([d["detected"] for d in results["detections"].values()])
        
        results["risk_score"] = min(max_confidence + (detected_count * 0.05), 1.0)
        
        if results["risk_score"] >= 0.75:
            results["overall_risk"] = "CRITICAL"
        elif results["risk_score"] >= 0.50:
            results["overall_risk"] = "HIGH"
        elif results["risk_score"] >= 0.30:
            results["overall_risk"] = "MEDIUM"
        
        return results