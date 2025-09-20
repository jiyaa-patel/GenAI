import os
import google.generativeai as genai
from dotenv import load_dotenv
import re
try:
    from google.cloud import secretmanager as google_secretmanager
except Exception:
    google_secretmanager = None

load_dotenv()

class AgreementAnalyzer:
    def __init__(self):
        self.api_key = (
            os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
            or self._fetch_api_key_from_secret_manager()
        )
        if not self.api_key:
            raise RuntimeError("Missing Gemini API key. Set GEMINI_API_KEY/GOOGLE_API_KEY or configure Secret Manager.")
        genai.configure(api_key=self.api_key)
        
        # Initialize Gemini model
        for model_name in ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"]:
            try:
                self.model = genai.GenerativeModel(model_name)
                _ = self.model.generate_content("ping")
                print(f"Using Gemini API model: {model_name}")
                break
            except Exception:
                continue
        else:
            raise RuntimeError("Failed to initialize any Gemini API model.")

    def _fetch_api_key_from_secret_manager(self):
        """Try to fetch Gemini API key from Google Secret Manager.

        Expected environment variables:
        - GCP_PROJECT or GOOGLE_CLOUD_PROJECT: GCP project id
        - GEMINI_API_SECRET_NAME (optional): Secret name (default: "GEMINI_API_KEY")
        - GEMINI_API_SECRET_VERSION (optional): Secret version (default: "latest")
        """
        try:
            if google_secretmanager is None:
                return None
            project_id = os.getenv("GCP_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT")
            if not project_id:
                return None
            secret_name = os.getenv("GEMINI_API_SECRET_NAME", "GEMINI_API_KEY")
            version = os.getenv("GEMINI_API_SECRET_VERSION", "latest")

            client = google_secretmanager.SecretManagerServiceClient()
            resource_name = f"projects/{project_id}/secrets/{secret_name}/versions/{version}"
            response = client.access_secret_version(name=resource_name)
            return response.payload.data.decode("utf-8").strip()
        except Exception:
            return None

    def detect_agreement_type(self, text):
        """Detect the type of legal agreement based on content analysis."""
        detection_prompt = f"""
        Analyze the following legal document text and determine the type of agreement.
        
        DOCUMENT TEXT:
        {text[:3000]}  # First 3000 characters for type detection
        
        CLASSIFY this document into ONE of these categories:
        1. Residential Rental/Lease Agreement
        2. Commercial Lease Agreement  
        3. Paying Guest (PG) or Hostel Contract
        4. Maintenance Agreement with Housing Society
        5. Employment Agreement
        6. Service Agreement
        7. Purchase Agreement
        8. Partnership Agreement
        9. Other (specify)
        
        Respond with ONLY the category number and name, nothing else.
        Example: "1. Residential Rental/Lease Agreement"
        """
        
        try:
            response = self.model.generate_content(detection_prompt)
            result = getattr(response, 'text', str(response)).strip()
            return result
        except Exception as e:
            print(f"Error detecting agreement type: {e}")
            return "Unknown Agreement Type"

    def generate_rental_summary(self, text):
        """Generate a specialized summary for rental agreements (200-250 words)."""
        rental_summary_prompt = f"""
        You are a legal document analyst specializing in rental agreements. 
        Analyze the following rental agreement document and create a comprehensive summary of 200-250 words.
        
        DOCUMENT TEXT:
        {text}
        
        Your summary MUST include these key components:
        - Rent amount and payment terms
        - Security deposit details
        - Notice period requirements
        - Lock-in period (if any)
        - Renewal terms and conditions
        - Penalties and late fees
        
        Also include:
        - Property details and address
        - Tenant and landlord obligations
        - Maintenance responsibilities
        - Any special conditions or restrictions
        
        Format the summary in clear, professional language suitable for a client.
        Keep it between 200-250 words.
        Focus on the most important terms that affect the tenant's rights and obligations.
        """
        
        try:
            response = self.model.generate_content(rental_summary_prompt)
            return getattr(response, 'text', str(response))
        except Exception as e:
            print(f"Error generating rental summary: {e}")
            return "Error: Unable to generate summary. Please check your API configuration."

    def generate_commercial_lease_summary(self, text):
        """Generate a specialized summary for commercial lease agreements."""
        commercial_summary_prompt = f"""
        You are a legal document analyst specializing in commercial lease agreements.
        Analyze the following commercial lease document and create a comprehensive summary of 200-250 words.
        
        DOCUMENT TEXT:
        {text}
        
        Your summary MUST include these key components:
        - Base rent and additional charges (CAM, utilities, taxes)
        - Security deposit and guarantees
        - Term length and renewal options
        - Use restrictions and permitted activities
        - Operating hours and access rights
        - Maintenance and repair responsibilities
        - Insurance requirements
        - Assignment and subletting rights
        - Default and termination provisions
        
        Format the summary in clear, professional language suitable for a business client.
        Keep it between 200-250 words.
        Focus on business-critical terms and financial obligations.
        """
        
        try:
            response = self.model.generate_content(commercial_summary_prompt)
            return getattr(response, 'text', str(response))
        except Exception as e:
            print(f"Error generating commercial lease summary: {e}")
            return "Error: Unable to generate summary. Please check your API configuration."

    def generate_pg_hostel_summary(self, text):
        """Generate a specialized summary for PG/Hostel contracts."""
        pg_summary_prompt = f"""
        You are a legal document analyst specializing in paying guest (PG) and hostel contracts.
        Analyze the following PG/Hostel agreement document and create a comprehensive summary of 200-250 words.
        
        DOCUMENT TEXT:
        {text}
        
        Your summary MUST include these key components:
        - Monthly rent and advance payment requirements
        - Security deposit amount and refund terms
        - Notice period for vacating
        - Lock-in period and early termination fees
        - Meal plans and food charges (if applicable)
        - House rules and restrictions
        - Maintenance and cleaning responsibilities
        - Guest policy and visitor restrictions
        - Payment due dates and late fees
        
        Format the summary in clear, professional language suitable for a tenant.
        Keep it between 200-250 words.
        Focus on accommodation-specific terms and living conditions.
        """
        
        try:
            response = self.model.generate_content(pg_summary_prompt)
            return getattr(response, 'text', str(response))
        except Exception as e:
            print(f"Error generating PG/Hostel summary: {e}")
            return "Error: Unable to generate summary. Please check your API configuration."

    def generate_maintenance_agreement_summary(self, text):
        """Generate a specialized summary for maintenance agreements with housing societies."""
        maintenance_summary_prompt = f"""
        You are a legal document analyst specializing in maintenance agreements with housing societies.
        Analyze the following maintenance agreement document and create a comprehensive summary of 200-250 words.
        
        DOCUMENT TEXT:
        {text}
        
        Your summary MUST include these key components:
        - Monthly maintenance charges and breakdown
        - Security deposit requirements
        - Notice period for termination
        - Lock-in period (if any)
        - Renewal terms and conditions
        - Penalties for late payment
        - Services covered under maintenance
        - Additional charges for extra services
        - Dispute resolution procedures
        - Society rules and regulations
        
        Format the summary in clear, professional language suitable for a resident.
        Keep it between 200-250 words.
        Focus on maintenance services and financial obligations.
        """
        
        try:
            response = self.model.generate_content(maintenance_summary_prompt)
            return getattr(response, 'text', str(response))
        except Exception as e:
            print(f"Error generating maintenance agreement summary: {e}")
            return "Error: Unable to generate summary. Please check your API configuration."

    def generate_employment_summary(self, text):
        """Generate a specialized summary for employment agreements."""
        prompt = f"""
        You are a legal document analyst specializing in employment agreements.
        Analyze the following employment agreement document and create a comprehensive summary of 200-250 words.

        DOCUMENT TEXT:
        {text}

        Your summary MUST include these key components:
        - Job role and responsibilities
        - Salary and benefits
        - Probation period (if any)
        - Notice period and termination terms
        - Working hours, leave, and holidays
        - Confidentiality and non-compete clauses
        - Dispute resolution process

        Format the summary in clear, professional language suitable for an employee.
        Keep it between 200-250 words.
        """
        try:
            response = self.model.generate_content(prompt)
            return getattr(response, 'text', str(response))
        except Exception as e:
            print(f"Error generating employment summary: {e}")
            return "Error: Unable to generate employment summary."

    def generate_service_summary(self, text):
        """Generate a specialized summary for service agreements."""
        prompt = f"""
        You are a legal document analyst specializing in service agreements.
        Analyze the following service agreement and create a comprehensive summary of 200-250 words.

        DOCUMENT TEXT:
        {text}

        Your summary MUST include these key components:
        - Scope of services
        - Service fees and payment terms
        - Duration of the contract
        - Termination clauses
        - Service-level commitments (SLAs, if any)
        - Liability and indemnity terms
        - Renewal or extension terms

        Format the summary in clear, professional language suitable for a client.
        Keep it between 200-250 words.
        """
        try:
            response = self.model.generate_content(prompt)
            return getattr(response, 'text', str(response))
        except Exception as e:
            print(f"Error generating service agreement summary: {e}")
            return "Error: Unable to generate service agreement summary."

    def generate_purchase_summary(self, text):
        """Generate a specialized summary for purchase agreements."""
        prompt = f"""
        You are a legal document analyst specializing in purchase agreements.
        Analyze the following purchase agreement and create a comprehensive summary of 200-250 words.

        DOCUMENT TEXT:
        {text}

        Your summary MUST include these key components:
        - Parties involved (buyer/seller)
        - Goods/services purchased
        - Purchase price and payment schedule
        - Delivery and inspection terms
        - Warranties and guarantees
        - Risk of loss and insurance
        - Default and remedies
        - Termination and dispute resolution

        Format the summary in clear, professional language suitable for a buyer.
        Keep it between 200-250 words.
        """
        try:
            response = self.model.generate_content(prompt)
            return getattr(response, 'text', str(response))
        except Exception as e:
            print(f"Error generating purchase agreement summary: {e}")
            return "Error: Unable to generate purchase agreement summary."

    def generate_partnership_summary(self, text):
        """Generate a specialized summary for partnership agreements."""
        prompt = f"""
        You are a legal document analyst specializing in partnership agreements.
        Analyze the following partnership agreement and create a comprehensive summary of 200-250 words.

        DOCUMENT TEXT:
        {text}

        Your summary MUST include these key components:
        - Names of partners
        - Capital contributions of each partner
        - Profit/loss sharing ratio
        - Roles and responsibilities
        - Decision-making and voting rights
        - Withdrawal or admission of partners
        - Dispute resolution process
        - Dissolution/exit terms

        Format the summary in clear, professional language suitable for business partners.
        Keep it between 200-250 words.
        """
        try:
            response = self.model.generate_content(prompt)
            return getattr(response, 'text', str(response))
        except Exception as e:
            print(f"Error generating partnership agreement summary: {e}")
            return "Error: Unable to generate partnership agreement summary."

    def generate_summary(self, text):
        print("Analyzing document type...")
        agreement_type = self.detect_agreement_type(text)
        print(f"Detected: {agreement_type}")

        print("Generating specialized summary...")

        if "Residential Rental" in agreement_type or "Lease Agreement" in agreement_type:
            summary = self.generate_rental_summary(text)
        elif "Commercial Lease" in agreement_type:
            summary = self.generate_commercial_lease_summary(text)
        elif "Paying Guest" in agreement_type or "Hostel" in agreement_type:
            summary = self.generate_pg_hostel_summary(text)
        elif "Maintenance Agreement" in agreement_type or "Housing Society" in agreement_type:
            summary = self.generate_maintenance_agreement_summary(text)
        elif "Employment Agreement" in agreement_type:
            summary = self.generate_employment_summary(text)
        elif "Service Agreement" in agreement_type:
            summary = self.generate_service_summary(text)
        elif "Purchase Agreement" in agreement_type:
            summary = self.generate_purchase_summary(text)
        elif "Partnership Agreement" in agreement_type:
            summary = self.generate_partnership_summary(text)
        else:
            generic_prompt = f"""
            You are a legal document analyst. Analyze the following legal document and create a comprehensive summary of 200-250 words.
            
            DOCUMENT TEXT:
            {text}
            
            Your summary should include:
            - Key terms and conditions
            - Important obligations and rights
            - Financial terms and penalties
            - Duration and termination provisions
            - Any special conditions
            
            Format the summary in clear, professional language.
            Keep it between 200-250 words.
            """
            
            try:
                response = self.model.generate_content(generic_prompt)
                summary = getattr(response, 'text', str(response))
            except Exception as e:
                print(f"Error generating generic summary: {e}")
                summary = "Error: Unable to generate summary. Please check your API configuration."
        
        return {
            'agreement_type': agreement_type,
            'summary': summary,
            'word_count': len(summary.split())
        }

    # DETAILED SUMMARY METHODS (600-700 words)

    def generate_detailed_rental_summary(self, text):
        """Generate a detailed summary for rental agreements (600-700 words)."""
        detailed_rental_prompt = f"""
        You are a legal document analyst specializing in rental agreements. 
        Analyze the following rental agreement document and create a comprehensive, detailed summary of 600-700 words.
        
        DOCUMENT TEXT:
        {text}
        
        Your detailed summary MUST include:
        
        1. **PROPERTY DETAILS & PARTIES** (50-70 words):
        - Complete property address and description
        - Landlord and tenant names/details
        - Lease term and commencement date
        
        2. **FINANCIAL TERMS** (100-120 words):
        - Monthly rent amount and payment schedule
        - Security deposit amount and refund conditions
        - Additional charges (utilities, maintenance, etc.)
        - Late payment penalties and grace periods
        
        3. **LEASE TERMS & CONDITIONS** (120-150 words):
        - Lock-in period details and early termination penalties
        - Notice period requirements for both parties
        - Renewal terms and conditions
        - Subletting and assignment restrictions
        
        4. **OBLIGATIONS & RESPONSIBILITIES** (100-120 words):
        - Tenant obligations (maintenance, cleanliness, etc.)
        - Landlord responsibilities (repairs, services, etc.)
        - Property use restrictions and house rules
        - Pet policies and guest restrictions
        
        5. **MAINTENANCE & REPAIRS** (80-100 words):
        - Who handles what type of repairs
        - Emergency maintenance procedures
        - Tenant's responsibility limits
        - Property condition requirements
        
        6. **TERMINATION & DEFAULT** (80-100 words):
        - Grounds for termination
        - Default procedures and remedies
        - Security deposit deductions
        - Move-out requirements
        
        7. **POTENTIAL ISSUES & RISKS** (70-90 words):
        - Identify any unfair or problematic clauses
        - Highlight potential legal issues
        - Note any one-sided terms
        - Suggest areas for negotiation
        
        Format the summary in clear, professional language with proper sections.
        Keep it between 600-700 words total.
        Focus on providing a comprehensive understanding of all clauses and identifying potential problems.
        """
        
        try:
            response = self.model.generate_content(detailed_rental_prompt)
            return getattr(response, 'text', str(response))
        except Exception as e:
            print(f"Error generating detailed rental summary: {e}")
            return "Error: Unable to generate detailed summary. Please check your API configuration."

    def generate_detailed_commercial_lease_summary(self, text):
        """Generate a detailed summary for commercial lease agreements (600-700 words)."""
        detailed_commercial_prompt = f"""
        You are a legal document analyst specializing in commercial lease agreements.
        Analyze the following commercial lease document and create a comprehensive, detailed summary of 600-700 words.
        
        DOCUMENT TEXT:
        {text}
        
        Your detailed summary MUST include:
        
        1. **PREMISES & PARTIES** (50-70 words):
        - Property description and square footage
        - Landlord and tenant business details
        - Lease term and commencement date
        
        2. **FINANCIAL TERMS** (120-150 words):
        - Base rent amount and payment schedule
        - Common Area Maintenance (CAM) charges breakdown
        - Additional charges (utilities, taxes, insurance)
        - Security deposit and personal guarantees
        - Rent escalation clauses and adjustments
        
        3. **LEASE TERMS & USE** (100-120 words):
        - Permitted use of premises
        - Operating hours and access rights
        - Assignment and subletting restrictions
        - Renewal options and terms
        - Early termination provisions
        
        4. **MAINTENANCE & REPAIRS** (80-100 words):
        - Landlord maintenance responsibilities
        - Tenant maintenance obligations
        - Emergency repair procedures
        - Building systems and HVAC maintenance
        - Common area maintenance
        
        5. **INSURANCE & LIABILITY** (80-100 words):
        - Required insurance coverage amounts
        - Additional insured requirements
        - Liability and indemnity provisions
        - Property damage coverage
        - Business interruption considerations
        
        6. **DEFAULT & TERMINATION** (80-100 words):
        - Default events and cure periods
        - Termination procedures and notice
        - Remedies and enforcement
        - Holdover provisions
        - Surrender and restoration requirements
        
        7. **POTENTIAL ISSUES & RISKS** (70-90 words):
        - Identify any unfair or problematic clauses
        - Highlight potential legal issues
        - Note any one-sided terms
        - Suggest areas for negotiation
        - Business impact considerations
        
        Format the summary in clear, professional language with proper sections.
        Keep it between 600-700 words total.
        Focus on providing a comprehensive understanding of all clauses and identifying potential problems.
        """
        
        try:
            response = self.model.generate_content(detailed_commercial_prompt)
            return getattr(response, 'text', str(response))
        except Exception as e:
            print(f"Error generating detailed commercial lease summary: {e}")
            return "Error: Unable to generate detailed summary. Please check your API configuration."

    def generate_detailed_pg_hostel_summary(self, text):
        """Generate a detailed summary for PG/Hostel contracts (600-700 words)."""
        detailed_pg_prompt = f"""
        You are a legal document analyst specializing in paying guest (PG) and hostel contracts.
        Analyze the following PG/Hostel agreement document and create a comprehensive, detailed summary of 600-700 words.
        
        DOCUMENT TEXT:
        {text}
        
        Your detailed summary MUST include:
        
        1. **ACCOMMODATION DETAILS & PARTIES** (50-70 words):
        - Property address and room description
        - Owner/manager and tenant details
        - Contract term and commencement date
        - Type of accommodation (PG/Hostel)
        
        2. **FINANCIAL TERMS** (100-120 words):
        - Monthly rent and advance payment requirements
        - Security deposit amount and refund conditions
        - Additional charges (meals, utilities, etc.)
        - Late payment penalties and grace periods
        - Refund policies for early termination
        
        3. **LIVING TERMS & CONDITIONS** (120-150 words):
        - Lock-in period details and early termination fees
        - Notice period requirements for vacating
        - House rules and restrictions
        - Meal plans and food charges (if applicable)
        - Guest policy and visitor restrictions
        
        4. **FACILITIES & SERVICES** (80-100 words):
        - What facilities are included
        - Meal services and timings
        - Cleaning and maintenance services
        - Internet and utility provisions
        - Common area access and rules
        
        5. **TENANT OBLIGATIONS** (80-100 words):
        - Maintenance and cleaning responsibilities
        - Noise and behavior restrictions
        - Property care requirements
        - Compliance with house rules
        - Reporting maintenance issues
        
        6. **TERMINATION & MOVE-OUT** (80-100 words):
        - Grounds for termination
        - Move-out procedures and notice
        - Security deposit return process
        - Property inspection requirements
        - Final settlement procedures
        
        7. **POTENTIAL ISSUES & RISKS** (70-90 words):
        - Identify any unfair or problematic clauses
        - Highlight potential legal issues
        - Note any one-sided terms
        - Suggest areas for negotiation
        - Living condition concerns
        
        Format the summary in clear, professional language with proper sections.
        Keep it between 600-700 words total.
        Focus on providing a comprehensive understanding of all clauses and identifying potential problems.
        """
        
        try:
            response = self.model.generate_content(detailed_pg_prompt)
            return getattr(response, 'text', str(response))
        except Exception as e:
            print(f"Error generating detailed PG/Hostel summary: {e}")
            return "Error: Unable to generate detailed summary. Please check your API configuration."

    def generate_detailed_maintenance_agreement_summary(self, text):
        """Generate a detailed summary for maintenance agreements (600-700 words)."""
        detailed_maintenance_prompt = f"""
        You are a legal document analyst specializing in maintenance agreements with housing societies.
        Analyze the following maintenance agreement document and create a comprehensive, detailed summary of 600-700 words.
        
        DOCUMENT TEXT:
        {text}
        
        Your detailed summary MUST include:
        
        1. **AGREEMENT OVERVIEW** (50-70 words):
        - Society name and property details
        - Resident and society details
        - Agreement term and commencement date
        
        2. **MAINTENANCE CHARGES** (100-120 words):
        - Monthly maintenance amount and breakdown
        - Service charges and additional fees
        - Payment schedule and due dates
        - Late payment penalties and interest
        
        3. **SERVICES COVERED** (120-150 words):
        - What maintenance services are included
        - Common area maintenance details
        - Security and safety services
        - Utility and infrastructure maintenance
        - Additional services available
        
        4. **RESPONSIBILITIES** (100-120 words):
        - Society maintenance obligations
        - Resident responsibilities
        - Emergency maintenance procedures
        - Complaint handling process
        - Quality standards and timelines
        
        5. **FINANCIAL TERMS** (80-100 words):
        - Security deposit requirements
        - Escalation clauses
        - Refund policies
        - Additional charge procedures
        - Dispute resolution for charges
        
        6. **TERMINATION & DEFAULT** (80-100 words):
        - Grounds for termination
        - Notice period requirements
        - Default procedures and remedies
        - Exit requirements and final settlement
        
        7. **POTENTIAL ISSUES & RISKS** (70-90 words):
        - Identify any unfair or problematic clauses
        - Highlight potential legal issues
        - Note any one-sided terms
        - Suggest areas for negotiation
        - Service quality concerns
        
        Format the summary in clear, professional language with proper sections.
        Keep it between 600-700 words total.
        Focus on providing a comprehensive understanding of all clauses and identifying potential problems.
        """
        
        try:
            response = self.model.generate_content(detailed_maintenance_prompt)
            return getattr(response, 'text', str(response))
        except Exception as e:
            print(f"Error generating detailed maintenance agreement summary: {e}")
            return "Error: Unable to generate detailed summary. Please check your API configuration."

    def generate_detailed_employment_summary(self, text):
        """Generate a detailed summary for employment agreements (600-700 words)."""
        detailed_employment_prompt = f"""
        You are a legal document analyst specializing in employment agreements.
        Analyze the following employment agreement document and create a comprehensive, detailed summary of 600-700 words.
        
        DOCUMENT TEXT:
        {text}
        
        Your detailed summary MUST include:
        
        1. **EMPLOYMENT DETAILS** (50-70 words):
        - Employee and employer details
        - Job title, role, and location
        - Start date and probation period
        - Employment type and status
        
        2. **COMPENSATION & BENEFITS** (100-120 words):
        - Base salary and payment schedule
        - Allowances and variable pay
        - Bonuses, incentives, and benefits
        - Deductions and reimbursements
        - Performance evaluation criteria
        
        3. **TERMS & CONDITIONS** (120-150 words):
        - Working hours and schedule
        - Leave policy and holidays
        - Confidentiality clauses
        - Intellectual property ownership
        - Code of conduct requirements
        - Dress code and workplace policies
        
        4. **OBLIGATIONS & RESTRICTIONS** (100-120 words):
        - Non-compete and non-solicit clauses
        - Conflict of interest rules
        - Performance expectations
        - Reporting duties and hierarchy
        - Training and development requirements
        
        5. **TERMINATION & NOTICE** (80-100 words):
        - Grounds for termination
        - Notice period requirements
        - Severance and exit pay
        - Return of company property
        - Dispute resolution process
        
        6. **WORKPLACE POLICIES** (80-100 words):
        - Health and safety requirements
        - Technology and equipment usage
        - Social media policies
        - Grievance procedures
        - Equal opportunity policies
        
        7. **POTENTIAL ISSUES & RISKS** (70-90 words):
        - Identify any unfair or problematic clauses
        - Highlight potential legal issues
        - Note any one-sided terms
        - Suggest areas for negotiation
        - Employee rights concerns
        
        Format the summary in clear, professional language with proper sections.
        Keep it between 600-700 words total.
        Focus on providing a comprehensive understanding of all clauses and identifying potential problems.
        """
        
        try:
            response = self.model.generate_content(detailed_employment_prompt)
            return getattr(response, 'text', str(response))
        except Exception as e:
            print(f"Error generating detailed employment summary: {e}")
            return "Error: Unable to generate detailed summary. Please check your API configuration."

    def generate_detailed_service_summary(self, text):
        """Generate a detailed summary for service agreements (600-700 words)."""
        detailed_service_prompt = f"""
        You are a legal document analyst specializing in service agreements.
        Analyze the following service agreement and create a comprehensive, detailed summary of 600-700 words.
        
        DOCUMENT TEXT:
        {text}
        
        Your detailed summary MUST include:
        
        1. **PARTIES & PURPOSE** (50-70 words):
        - Service provider and client details
        - Scope of services and purpose
        - Agreement duration and effective date
        - Service location and delivery method
        
        2. **SCOPE & DELIVERABLES** (120-150 words):
        - Detailed service scope and description
        - Specific deliverables and timelines
        - Service levels and performance metrics (SLAs)
        - Quality standards and requirements
        - Change management procedures
        
        3. **FINANCIAL TERMS** (100-120 words):
        - Service fees and payment schedule
        - Taxes, reimbursements, and additional costs
        - Penalties for delays or non-performance
        - Escalation clauses and adjustments
        - Currency and payment methods
        
        4. **OBLIGATIONS & RESPONSIBILITIES** (100-120 words):
        - Service provider duties and commitments
        - Client responsibilities and cooperation
        - Compliance with laws and regulations
        - Confidentiality and data protection
        - Insurance and liability requirements
        
        5. **PERFORMANCE & MONITORING** (80-100 words):
        - Performance measurement criteria
        - Reporting requirements and frequency
        - Monitoring and audit rights
        - Issue escalation procedures
        - Continuous improvement expectations
        
        6. **TERMINATION & DISPUTE RESOLUTION** (80-100 words):
        - Grounds for termination
        - Notice period and transition requirements
        - Refund policies and penalties
        - Dispute resolution procedures
        - Governing law and jurisdiction
        
        7. **POTENTIAL ISSUES & RISKS** (70-90 words):
        - Identify any unfair or problematic clauses
        - Highlight potential legal issues
        - Note any one-sided terms
        - Suggest areas for negotiation
        - Service quality and SLA concerns
        
        Format the summary in clear, professional language with proper sections.
        Keep it between 600-700 words total.
        Focus on providing a comprehensive understanding of all clauses and identifying potential problems.
        """
        
        try:
            response = self.model.generate_content(detailed_service_prompt)
            return getattr(response, 'text', str(response))
        except Exception as e:
            print(f"Error generating detailed service agreement summary: {e}")
            return "Error: Unable to generate detailed summary. Please check your API configuration."

    def generate_detailed_purchase_summary(self, text):
        """Generate a detailed summary for purchase agreements (600-700 words)."""
        detailed_purchase_prompt = f"""
        You are a legal document analyst specializing in purchase agreements.
        Analyze the following purchase agreement and create a comprehensive, detailed summary of 600-700 words.
        
        DOCUMENT TEXT:
        {text}
        
        Your detailed summary MUST include:
        
        1. **PARTIES & TRANSACTION** (50-70 words):
        - Buyer and seller details
        - Goods or services being purchased
        - Transaction value and currency
        - Effective date and duration
        
        2. **PURCHASE DETAILS** (100-120 words):
        - Detailed description of items
        - Quantity, specifications, and quality standards
        - Delivery requirements and timelines
        - Inspection and acceptance criteria
        - Packaging and labeling requirements
        
        3. **FINANCIAL TERMS** (120-150 words):
        - Purchase price and payment schedule
        - Taxes, duties, and additional costs
        - Currency and exchange rate provisions
        - Late payment penalties and interest
        - Refund and cancellation policies
        
        4. **DELIVERY & PERFORMANCE** (100-120 words):
        - Delivery method and location
        - Risk of loss and insurance requirements
        - Performance guarantees and warranties
        - Force majeure and delay provisions
        - Acceptance and rejection procedures
        
        5. **QUALITY & WARRANTIES** (80-100 words):
        - Quality standards and specifications
        - Warranty terms and duration
        - Defect liability and remedies
        - Testing and inspection rights
        - Quality assurance procedures
        
        6. **DEFAULT & REMEDIES** (80-100 words):
        - Events of default
        - Available remedies and enforcement
        - Liquidated damages and penalties
        - Termination procedures
        - Dispute resolution process
        
        7. **POTENTIAL ISSUES & RISKS** (70-90 words):
        - Identify any unfair or problematic clauses
        - Highlight potential legal issues
        - Note any one-sided terms
        - Suggest areas for negotiation
        - Quality and delivery concerns
        
        Format the summary in clear, professional language with proper sections.
        Keep it between 600-700 words total.
        Focus on providing a comprehensive understanding of all clauses and identifying potential problems.
        """
        
        try:
            response = self.model.generate_content(detailed_purchase_prompt)
            return getattr(response, 'text', str(response))
        except Exception as e:
            print(f"Error generating detailed purchase agreement summary: {e}")
            return "Error: Unable to generate detailed summary. Please check your API configuration."

    def generate_detailed_partnership_summary(self, text):
        """Generate a detailed summary for partnership agreements (600-700 words)."""
        detailed_partnership_prompt = f"""
        You are a legal document analyst specializing in partnership agreements.
        Analyze the following partnership agreement and create a comprehensive, detailed summary of 600-700 words.
        
        DOCUMENT TEXT:
        {text}
        
        Your detailed summary MUST include:
        
        1. **PARTNERSHIP OVERVIEW** (50-70 words):
        - Partnership name and business purpose
        - Names and details of all partners
        - Partnership type and structure
        - Effective date and duration
        
        2. **CAPITAL & FINANCIAL TERMS** (100-120 words):
        - Capital contributions of each partner
        - Profit and loss sharing ratios
        - Additional capital requirements
        - Financial reporting and audit rights
        - Banking and financial arrangements
        
        3. **RIGHTS & RESPONSIBILITIES** (120-150 words):
        - Management and decision-making rights
        - Voting rights and procedures
        - Roles and responsibilities of each partner
        - Performance expectations and standards
        - Conflict of interest provisions
        
        4. **OPERATIONS & MANAGEMENT** (100-120 words):
        - Day-to-day operations management
        - Major decision approval requirements
        - Meeting and communication procedures
        - Record keeping and documentation
        - Compliance and regulatory requirements
        
        5. **PARTNER CHANGES** (80-100 words):
        - Admission of new partners
        - Withdrawal and retirement procedures
        - Transfer of partnership interests
        - Buyout provisions and valuation
        - Succession planning
        
        6. **DISSOLUTION & EXIT** (80-100 words):
        - Grounds for dissolution
        - Winding up procedures
        - Asset distribution and settlement
        - Continuation of business options
        - Post-dissolution obligations
        
        7. **POTENTIAL ISSUES & RISKS** (70-90 words):
        - Identify any unfair or problematic clauses
        - Highlight potential legal issues
        - Note any one-sided terms
        - Suggest areas for negotiation
        - Partnership stability concerns
        
        Format the summary in clear, professional language with proper sections.
        Keep it between 600-700 words total.
        Focus on providing a comprehensive understanding of all clauses and identifying potential problems.
        """
        
        try:
            response = self.model.generate_content(detailed_partnership_prompt)
            return getattr(response, 'text', str(response))
        except Exception as e:
            print(f"Error generating detailed partnership agreement summary: {e}")
            return "Error: Unable to generate detailed summary. Please check your API configuration."

    def generate_detailed_summary(self, text):
        """Generate a detailed, comprehensive summary (600-700 words) with clause analysis and risk identification."""
        print("Analyzing document type for detailed summary...")
        agreement_type = self.detect_agreement_type(text)
        print(f"Detected: {agreement_type}")

        print("Generating detailed comprehensive summary...")

        if "Residential Rental" in agreement_type or "Lease Agreement" in agreement_type:
            summary = self.generate_detailed_rental_summary(text)
        elif "Commercial Lease" in agreement_type:
            summary = self.generate_detailed_commercial_lease_summary(text)
        elif "Paying Guest" in agreement_type or "Hostel" in agreement_type:
            summary = self.generate_detailed_pg_hostel_summary(text)
        elif "Maintenance Agreement" in agreement_type or "Housing Society" in agreement_type:
            summary = self.generate_detailed_maintenance_agreement_summary(text)
        elif "Employment Agreement" in agreement_type:
            summary = self.generate_detailed_employment_summary(text)
        elif "Service Agreement" in agreement_type:
            summary = self.generate_detailed_service_summary(text)
        elif "Purchase Agreement" in agreement_type:
            summary = self.generate_detailed_purchase_summary(text)
        elif "Partnership Agreement" in agreement_type:
            summary = self.generate_detailed_partnership_summary(text)
        else:
            generic_detailed_prompt = f"""
            You are a legal document analyst. Analyze the following legal document and create a comprehensive, detailed summary of 600-700 words.
            
            DOCUMENT TEXT:
            {text}
            
            Your detailed summary MUST include:
            
            1. **DOCUMENT OVERVIEW** (50-70 words):
            - Document type and purpose
            - Parties involved
            - Key dates and duration
            
            2. **MAIN TERMS & CONDITIONS** (120-150 words):
            - Primary obligations and rights
            - Key financial terms
            - Duration and scope
            
            3. **DETAILED CLAUSE ANALYSIS** (150-180 words):
            - Important clauses explained
            - Specific terms and conditions
            - Any special provisions
            
            4. **OBLIGATIONS & RESPONSIBILITIES** (100-120 words):
            - What each party must do
            - Performance requirements
            - Compliance obligations
            
            5. **FINANCIAL TERMS** (80-100 words):
            - Payment schedules
            - Penalties and fees
            - Financial obligations
            
            6. **TERMINATION & DEFAULT** (80-100 words):
            - How the agreement can end
            - Default procedures
            - Consequences of breach
            
            7. **POTENTIAL ISSUES & RISKS** (70-90 words):
            - Identify any unfair or problematic clauses
            - Highlight potential legal issues
            - Note any one-sided terms
            - Suggest areas for negotiation
            
            Format the summary in clear, professional language with proper sections.
            Keep it between 600-700 words total.
            Focus on providing a comprehensive understanding of all clauses and identifying potential problems.
            """
            
            try:
                response = self.model.generate_content(generic_detailed_prompt)
                summary = getattr(response, 'text', str(response))
            except Exception as e:
                print(f"Error generating detailed generic summary: {e}")
                summary = "Error: Unable to generate detailed summary. Please check your API configuration."
        
        return {
            'agreement_type': agreement_type,
            'summary': summary,
            'word_count': len(summary.split())
        }

