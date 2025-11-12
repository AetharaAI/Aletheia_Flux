"""Data processing tools for CSV and PDF files."""
import csv
import io
import base64
from typing import List, Dict, Any
import re


class DataProcessor:
    """Process CSV and PDF files for analysis."""
    
    async def process_csv(self, file_content: bytes, filename: str) -> Dict:
        """
        Process CSV file and extract insights.
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
        
        Returns:
            Dict with schema, sample rows, and basic statistics
        """
        try:
            # Decode content
            content_str = file_content.decode('utf-8')
            reader = csv.DictReader(io.StringIO(content_str))
            
            rows = list(reader)
            if not rows:
                return {"error": "Empty CSV file"}
            
            # Extract schema
            columns = list(rows[0].keys())
            
            # Sample data (first 10 rows)
            sample_rows = rows[:10]
            
            # Basic statistics
            total_rows = len(rows)
            
            # Column analysis
            column_analysis = {}
            for col in columns:
                values = [row.get(col, '') for row in rows]
                non_empty = [v for v in values if v.strip()]
                
                column_analysis[col] = {
                    "total_values": len(values),
                    "non_empty": len(non_empty),
                    "empty": len(values) - len(non_empty),
                    "sample_values": non_empty[:5]
                }
            
            return {
                "filename": filename,
                "total_rows": total_rows,
                "total_columns": len(columns),
                "columns": columns,
                "column_analysis": column_analysis,
                "sample_rows": sample_rows,
                "insights": self._generate_csv_insights(rows, columns)
            }
        
        except Exception as e:
            return {"error": f"Failed to process CSV: {str(e)}"}
    
    def _generate_csv_insights(self, rows: List[Dict], columns: List[str]) -> List[str]:
        """Generate automated insights from CSV data."""
        insights = []
        
        # Row count insight
        if len(rows) > 1000:
            insights.append(f"Large dataset with {len(rows):,} rows")
        
        # Missing data insight
        for col in columns:
            empty_count = sum(1 for row in rows if not row.get(col, '').strip())
            if empty_count > len(rows) * 0.1:
                pct = (empty_count / len(rows)) * 100
                insights.append(f"Column '{col}' has {pct:.1f}% missing values")
        
        # Numeric column detection
        numeric_cols = []
        for col in columns:
            values = [row.get(col, '') for row in rows[:100]]
            numeric_values = [v for v in values if self._is_numeric(v)]
            if len(numeric_values) / len(values) > 0.8:
                numeric_cols.append(col)
        
        if numeric_cols:
            insights.append(f"Numeric columns detected: {', '.join(numeric_cols)}")
        
        return insights
    
    def _is_numeric(self, value: str) -> bool:
        """Check if value is numeric."""
        try:
            float(value.replace(',', ''))
            return True
        except:
            return False
    
    async def process_pdf(self, file_content: bytes, filename: str) -> Dict:
        """
        Process PDF file and extract text.
        
        Note: Basic text extraction without external libraries.
        For production, consider using PyPDF2 or pdfplumber.
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
        
        Returns:
            Dict with extracted text and metadata
        """
        try:
            # Basic PDF text extraction (simplified)
            # In production, use proper PDF parsing library
            text = file_content.decode('utf-8', errors='ignore')
            
            # Clean up extracted text
            text = re.sub(r'[^\x00-\x7F]+', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Extract basic metadata
            word_count = len(text.split())
            char_count = len(text)
            
            return {
                "filename": filename,
                "text": text[:5000],  # First 5000 chars
                "total_chars": char_count,
                "total_words": word_count,
                "insights": [
                    f"Extracted {word_count:,} words from PDF",
                    "Text extraction is basic - may not capture all formatting"
                ]
            }
        
        except Exception as e:
            return {"error": f"Failed to process PDF: {str(e)}"}


# Global processor instance
data_processor = DataProcessor()


async def process_file(file_content: bytes, filename: str, file_type: str) -> Dict:
    """Process uploaded file based on type."""
    if file_type in ['text/csv', 'application/vnd.ms-excel']:
        return await data_processor.process_csv(file_content, filename)
    elif file_type == 'application/pdf':
        return await data_processor.process_pdf(file_content, filename)
    else:
        return {"error": f"Unsupported file type: {file_type}"}
