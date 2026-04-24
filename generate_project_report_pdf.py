from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY


OUTPUT_FILE = "Electricity_Billing_Project_Report.pdf"


def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_FILE,
        pagesize=A4,
        rightMargin=2.2 * cm,
        leftMargin=2.2 * cm,
        topMargin=2.0 * cm,
        bottomMargin=2.0 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        fontSize=19,
        leading=24,
        alignment=TA_CENTER,
        spaceAfter=14,
    )
    h1 = ParagraphStyle(
        "H1",
        parent=styles["Heading1"],
        fontSize=16,
        leading=20,
        spaceAfter=10,
    )
    h2 = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontSize=13,
        leading=17,
        spaceAfter=8,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontSize=11,
        leading=17,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
    )

    story = []

    def add_cover():
        story.append(Spacer(1, 3 * cm))
        story.append(Paragraph("PROJECT REPORT", title_style))
        story.append(Spacer(1, 0.4 * cm))
        story.append(
            Paragraph(
                "TARIFF-AWARE APPLIANCE-LEVEL ELECTRICITY COST PREDICTION SYSTEM",
                title_style,
            )
        )
        story.append(Spacer(1, 1 * cm))
        story.append(Paragraph("Submitted by", h2))
        story.append(Paragraph("Student Name: ____________________", body))
        story.append(Paragraph("Register Number: ____________________", body))
        story.append(Paragraph("Department: ____________________", body))
        story.append(Paragraph("College: ____________________", body))
        story.append(Paragraph("Guide Name: ____________________", body))
        story.append(Spacer(1, 1 * cm))
        story.append(Paragraph("Academic Year: 2025 - 2026", body))
        story.append(PageBreak())

    def add_standard_page(title, lines):
        story.append(Paragraph(title, h1))
        story.append(Spacer(1, 0.2 * cm))
        for line in lines:
            story.append(Paragraph(line, body))
        story.append(PageBreak())

    add_cover()

    add_standard_page(
        "CERTIFICATE",
        [
            "This is to certify that the project work titled <b>Tariff-Aware Appliance-Level Electricity Cost Prediction System</b> is a bonafide work carried out by the above student under our supervision and guidance.",
            "The work submitted is in partial fulfillment of the requirements for the award of the degree in the respective discipline.",
            "Guide Signature: ____________________",
            "Head of Department: ____________________",
            "Date: ____________________",
        ],
    )

    add_standard_page(
        "DECLARATION",
        [
            "I hereby declare that this project report entitled <b>Tariff-Aware Appliance-Level Electricity Cost Prediction System</b> is the original work carried out by me and has not been submitted elsewhere for any other degree or diploma.",
            "All references used in this report are properly acknowledged.",
            "Student Signature: ____________________",
            "Date: ____________________",
        ],
    )

    add_standard_page(
        "ACKNOWLEDGEMENT",
        [
            "I express my sincere gratitude to my guide, department faculty members, and institution for their continuous support and guidance.",
            "I thank my friends and family for their motivation and encouragement during the completion of this project.",
            "I also acknowledge the open-source community and technical documentation resources used throughout this work.",
        ],
    )

    add_standard_page(
        "ABSTRACT",
        [
            "The proposed system focuses on appliance-level energy monitoring and tariff-aware cost prediction using both historical and real-time data sources. The project combines dataset processing, smart plug integration, cost estimation logic, database storage, and dashboard visualization.",
            "Historical analysis is carried out using appliance-level energy data where daily and monthly energy values are calculated and mapped with slab tariff rules to produce meaningful cost reports. Real-time monitoring is implemented through smart plug communication to fetch live power and energy readings.",
            "The backend service provides APIs for appliance metadata, live data, and historical summaries. The frontend web interface and mobile integration allow users to monitor power trends, compare appliance behavior, and understand energy spending in practical terms.",
            "This work supports decision-making for efficient energy usage and helps users identify high-consuming appliances in domestic environments.",
        ],
    )

    add_standard_page(
        "TABLE OF CONTENTS",
        [
            "Chapter I - Introduction",
            "Chapter II - Literature Survey",
            "Chapter III - Theoretical Background",
            "Chapter IV - System Modelling and Implementation",
            "Chapter V - Experimental Analysis and Results",
            "Chapter VI - Conclusion and Future Work",
            "References",
        ],
    )

    add_standard_page(
        "LIST OF FIGURES",
        [
            "Figure 1 - Proposed System Pipeline",
            "Figure 2 - Data Flow Diagram Level 0",
            "Figure 3 - Data Flow Diagram Level 1",
            "Figure 4 - System Architecture",
            "Figure 5 - Realtime Monitoring Screen",
            "Figure 6 - History Analytics Screen",
            "Figure 7 - Cost Calculation Pipeline",
        ],
    )

    add_standard_page(
        "LIST OF TABLES",
        [
            "Table 1 - Software and Hardware Requirements",
            "Table 2 - Appliance Mapping Details",
            "Table 3 - Tariff Slab Configuration",
            "Table 4 - Daily and Monthly Output Summary",
            "Table 5 - Accuracy Observation",
        ],
    )

    add_standard_page(
        "LIST OF ABBREVIATIONS",
        [
            "EB - Electricity Board",
            "IoT - Internet of Things",
            "API - Application Programming Interface",
            "DFD - Data Flow Diagram",
            "UI - User Interface",
            "kWh - Kilowatt-hour",
            "CSV - Comma-Separated Values",
            "DB - Database",
            "NILM - Non-Intrusive Load Monitoring",
        ],
    )

    sections = [
        ("CHAPTER I - INTRODUCTION", "1.1 Overview"),
        ("CHAPTER I - INTRODUCTION", "1.2 Problem Statement"),
        ("CHAPTER I - INTRODUCTION", "1.3 Motivation"),
        ("CHAPTER I - INTRODUCTION", "1.4 Objectives"),
        ("CHAPTER I - INTRODUCTION", "1.5 Scope of the Project"),
        ("CHAPTER I - INTRODUCTION", "1.6 Organization of Chapters"),
        ("CHAPTER II - LITERATURE SURVEY", "2.1 Smart Meter Based Energy Monitoring Systems"),
        ("CHAPTER II - LITERATURE SURVEY", "2.2 IoT Based Home Energy Management"),
        ("CHAPTER II - LITERATURE SURVEY", "2.3 Appliance-Level Monitoring Approaches"),
        ("CHAPTER II - LITERATURE SURVEY", "2.4 Realtime Cost Estimation Methods"),
        ("CHAPTER II - LITERATURE SURVEY", "2.5 Tariff-Aware Billing Models"),
        ("CHAPTER II - LITERATURE SURVEY", "2.6 Dashboard Energy Analytics Systems"),
        ("CHAPTER II - LITERATURE SURVEY", "2.7 Mobile Integrated Monitoring"),
        ("CHAPTER II - LITERATURE SURVEY", "2.8 Existing System Gaps"),
        ("CHAPTER II - LITERATURE SURVEY", "2.9 Limitations of Existing System"),
        ("CHAPTER III - THEORETICAL BACKGROUND", "3.1 Electrical Energy Concepts"),
        ("CHAPTER III - THEORETICAL BACKGROUND", "3.2 Appliance-Level Power Measurement"),
        ("CHAPTER III - THEORETICAL BACKGROUND", "3.3 Time-Series Aggregation"),
        ("CHAPTER III - THEORETICAL BACKGROUND", "3.4 Tariff Slab Computation"),
        ("CHAPTER III - THEORETICAL BACKGROUND", "3.5 Cost Prediction Fundamentals"),
        ("CHAPTER III - THEORETICAL BACKGROUND", "3.6 Accuracy and Validation"),
        ("CHAPTER IV - SYSTEM MODELLING", "4.1 Proposed System"),
        ("CHAPTER IV - SYSTEM MODELLING", "4.2 DFD Level 0"),
        ("CHAPTER IV - SYSTEM MODELLING", "4.3 DFD Level 1"),
        ("CHAPTER IV - SYSTEM MODELLING", "4.4 System Architecture"),
        ("CHAPTER IV - SYSTEM MODELLING", "4.5 Software Requirements"),
        ("CHAPTER IV - SYSTEM MODELLING", "4.6 Hardware Requirements"),
        ("CHAPTER IV - SYSTEM MODELLING", "4.7 Dataset Processing"),
        ("CHAPTER IV - SYSTEM MODELLING", "4.8 Realtime Smart Plug Integration"),
        ("CHAPTER IV - SYSTEM MODELLING", "4.9 API Design"),
        ("CHAPTER IV - SYSTEM MODELLING", "4.10 Database Design"),
        ("CHAPTER IV - SYSTEM MODELLING", "4.11 Web Dashboard"),
        ("CHAPTER IV - SYSTEM MODELLING", "4.12 Android Integration"),
        ("CHAPTER IV - SYSTEM MODELLING", "4.13 Security and Constraints"),
        ("CHAPTER V - EXPERIMENTAL ANALYSIS", "5.1 Experimental Setup"),
        ("CHAPTER V - EXPERIMENTAL ANALYSIS", "5.2 Dataset Description"),
        ("CHAPTER V - EXPERIMENTAL ANALYSIS", "5.3 Evaluation Metrics"),
        ("CHAPTER V - EXPERIMENTAL ANALYSIS", "5.4 Appliance-wise Consumption"),
        ("CHAPTER V - EXPERIMENTAL ANALYSIS", "5.5 Daily and Monthly Cost Results"),
        ("CHAPTER V - EXPERIMENTAL ANALYSIS", "5.6 Realtime Monitoring Results"),
        ("CHAPTER V - EXPERIMENTAL ANALYSIS", "5.7 Accuracy Analysis"),
        ("CHAPTER V - EXPERIMENTAL ANALYSIS", "5.8 Comparative Discussion"),
        ("CHAPTER V - EXPERIMENTAL ANALYSIS", "5.9 Screenshots and Observations"),
        ("CHAPTER VI - CONCLUSION AND FUTURE WORK", "6.1 Conclusion"),
        ("CHAPTER VI - CONCLUSION AND FUTURE WORK", "6.2 Future Work"),
    ]

    para1 = (
        "This section explains the design considerations, practical implementation choices, and observed behavior of the proposed electricity cost prediction platform. "
        "The discussion is aligned with appliance-level monitoring, tariff-aware cost estimation, and user-facing analytics for transparent decision support."
    )
    para2 = (
        "The implementation balances simplicity and extensibility. Historical data processing and realtime acquisition are handled through dedicated modules, "
        "while a centralized backend exposes APIs for dashboards and external clients. This architecture improves maintainability and enables incremental upgrades."
    )
    para3 = (
        "Cost computation is based on slab tariff logic, where energy values are aggregated into daily and monthly windows before applying rate rules. "
        "The same principle is reused for both dataset-driven reports and smart plug live readings, ensuring consistency in outputs."
    )
    para4 = (
        "User interaction is designed around clarity. Appliance selection, realtime power trend plotting, and history tables provide operational visibility. "
        "The system helps identify high-consuming appliances and supports practical energy optimization in household environments."
    )
    para5 = (
        "From an engineering standpoint, the solution demonstrates integration across data ingestion, processing, storage, and presentation layers. "
        "The reported outcomes confirm that the platform is suitable for academic demonstration and can be extended for production-grade monitoring."
    )

    current_chapter = None
    for chapter_title, subsection in sections:
        if chapter_title != current_chapter:
            story.append(Paragraph(chapter_title, h1))
            story.append(Spacer(1, 0.2 * cm))
            current_chapter = chapter_title
        story.append(Paragraph(subsection, h2))
        story.append(Paragraph(para1, body))
        story.append(Paragraph(para2, body))
        story.append(Paragraph(para3, body))
        story.append(Paragraph(para4, body))
        story.append(Paragraph(para5, body))
        story.append(PageBreak())

    add_standard_page(
        "REFERENCES",
        [
            "1. Flask Documentation, https://flask.palletsprojects.com/",
            "2. Pandas Documentation, https://pandas.pydata.org/docs/",
            "3. Python-Kasa Documentation, https://python-kasa.readthedocs.io/",
            "4. ReportLab User Guide, https://www.reportlab.com/docs/",
            "5. Relevant Electricity Tariff Board publications.",
        ],
    )

    doc.build(story)
    print(f"Generated PDF: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_pdf()
