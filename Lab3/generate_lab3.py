import subprocess,sys
subprocess.check_call([sys.executable,"-m","pip","install","cairosvg","reportlab"],stdout=subprocess.DEVNULL)
import cairosvg
cairosvg.svg2png(url="Lab3_Component_Diagram.svg",write_to="Lab3_Component_Diagram_Kushagra_Bhandari_PES1UG24CS245.png",output_width=1400)
cairosvg.svg2pdf(url="Lab3_Component_Diagram.svg",write_to="Lab3_Component_Diagram_Kushagra_Bhandari_PES1UG24CS245.pdf")
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name="Small",parent=styles["BodyText"],fontSize=9.2,leading=11))
doc=SimpleDocTemplate("Lab3_Written_Justification_Kushagra_Bhandari_PES1UG24CS245.pdf",pagesize=A4,rightMargin=45,leftMargin=45,topMargin=40,bottomMargin=40)
story=[]
story.append(Paragraph("Lab 3 – Written Justification",styles["Title"]))
story.append(Paragraph("Self-Service Coffee Kiosk | PES1UG24CS245",styles["Heading3"]))
story.append(Spacer(1,8))
for line in open("Lab3_Written_Justification.md",encoding="utf-8").read().splitlines()[4:]:
    if line.startswith("### "): story.append(Paragraph("<b>"+line[4:]+"</b>",styles["Small"]))
    elif line.startswith("## "): story.append(Paragraph("<b>"+line[3:]+"</b>",styles["Small"]))
    elif line.strip(): story.append(Paragraph(line.replace("**",""),styles["Small"]))
    story.append(Spacer(1,3))
doc.build(story)
